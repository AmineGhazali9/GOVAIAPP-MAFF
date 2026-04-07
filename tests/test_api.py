"""Tests for the MAF API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from maf_app.api.main import app
from maf_app.api.schemas import CompanyContext


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _disable_foundry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure Foundry is disabled for all tests."""
    monkeypatch.setenv("FOUNDRY_ENABLED", "false")


class TestHealth:
    def test_health_ok(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["foundry_enabled"] is False

    def test_health_foundry_enabled(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://fake.endpoint")
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["foundry_enabled"] is True


class TestGeneratePolicy:
    PAYLOAD = {
        "company_name": "TestCorp",
        "sector": "Technologies",
        "maturite_donnees": "intermediaire",
        "principles": ["transparence", "equite"],
        "constraints": ["EU AI Act"],
    }

    def test_generate_policy_stub(self, client: TestClient) -> None:
        resp = client.post("/generate-policy", json=self.PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert "policy_markdown" in data
        assert len(data["policy_markdown"]) > 0
        assert "Politique de Gouvernance IA" in data["policy_markdown"]
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) == 2  # veille_externe + rag_interne

    def test_generate_policy_sources(self, client: TestClient) -> None:
        resp = client.post("/generate-policy", json=self.PAYLOAD)
        data = resp.json()
        source_names = [s["source"] for s in data["sources"]]
        assert "veille_externe" in source_names
        assert "rag_interne" in source_names

    def test_generate_policy_invalid_maturite(self, client: TestClient) -> None:
        payload = {**self.PAYLOAD, "maturite_donnees": "invalid"}
        resp = client.post("/generate-policy", json=payload)
        assert resp.status_code == 422

    def test_generate_policy_missing_fields(self, client: TestClient) -> None:
        resp = client.post("/generate-policy", json={})
        assert resp.status_code == 422

    def test_generate_policy_mode_and_steps(self, client: TestClient) -> None:
        resp = client.post("/generate-policy", json=self.PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode_used"] == "stub"
        assert data["duration_s"] >= 0
        steps = data["steps"]
        assert len(steps) == 3
        assert steps[0]["agent"] == "veille_externe"
        assert steps[1]["agent"] == "rag_interne"
        assert steps[2]["agent"] == "producteur_politique"
        for s in steps:
            assert s["status"] == "done"
            assert s["duration_s"] >= 0
            assert s["fallback_reason"] == ""
