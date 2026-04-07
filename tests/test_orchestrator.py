"""Tests for maf_app.orchestrator module."""

from __future__ import annotations

import pytest

from maf_app.orchestrator import run_pipeline


class TestRunPipeline:
    def test_returns_three_messages(self) -> None:
        result = run_pipeline("Test company context")
        assert len(result["messages"]) == 3

    def test_agent_order(self) -> None:
        result = run_pipeline("Test company context")
        roles = [m["role"] for m in result["messages"]]
        assert roles == ["veille_externe", "rag_interne", "producteur_politique"]

    def test_stub_markers_present(self) -> None:
        result = run_pipeline("Test company context")
        messages = result["messages"]
        assert "[STUB veille_externe]" in messages[0]["content"]
        assert "[STUB rag_interne]" in messages[1]["content"]

    def test_final_message_is_policy(self) -> None:
        result = run_pipeline("Test company context")
        policy = result["messages"][2]["content"]
        assert "# Politique de Gouvernance IA" in policy
        assert "## 1. Cadre Reglementaire" in policy
        assert "## 3. Recommandations" in policy

    def test_context_propagation(self) -> None:
        result = run_pipeline("Entreprise XYZ Secteur Finance")
        messages = result["messages"]
        assert "Entreprise XYZ" in messages[0]["content"]
        assert "STUB rag_interne" in messages[1]["content"]
        policy = messages[2]["content"]
        assert "veille_externe" in policy
        assert "rag_interne" in policy

    def test_all_messages_have_content(self) -> None:
        result = run_pipeline("Test")
        for msg in result["messages"]:
            assert "role" in msg
            assert "content" in msg
            assert len(msg["content"]) > 0

    def test_pipeline_idempotent(self) -> None:
        result1 = run_pipeline("Same context")
        result2 = run_pipeline("Same context")
        assert result1["messages"] == result2["messages"]

    def test_steps_returned(self) -> None:
        result = run_pipeline("Test context")
        steps = result["steps"]
        assert len(steps) == 3
        agents = [s["agent"] for s in steps]
        assert agents == ["veille_externe", "rag_interne", "producteur_politique"]
        for s in steps:
            assert s["status"] == "done"
            assert s["duration_s"] >= 0
            assert s["fallback_reason"] == ""
