"""Tests for maf_app.orchestrator module."""

from __future__ import annotations

import pytest

from maf_app.orchestrator import run_pipeline


class TestRunPipeline:
    def test_returns_three_messages(self) -> None:
        messages = run_pipeline("Test company context")
        assert len(messages) == 3

    def test_agent_order(self) -> None:
        messages = run_pipeline("Test company context")
        roles = [m["role"] for m in messages]
        assert roles == ["veille_externe", "rag_interne", "producteur_politique"]

    def test_stub_markers_present(self) -> None:
        messages = run_pipeline("Test company context")
        assert "[STUB veille_externe]" in messages[0]["content"]
        assert "[STUB rag_interne]" in messages[1]["content"]

    def test_final_message_is_policy(self) -> None:
        messages = run_pipeline("Test company context")
        policy = messages[2]["content"]
        assert "# Politique de Gouvernance IA" in policy
        assert "## 1. Cadre Réglementaire" in policy
        assert "## 3. Recommandations" in policy

    def test_context_propagation(self) -> None:
        messages = run_pipeline("Entreprise XYZ Secteur Finance")
        # Veille should reference the input
        assert "Entreprise XYZ" in messages[0]["content"]
        # RAG should reference veille output
        assert "STUB veille_externe" in messages[1]["content"]
        # Producteur should include both veille and rag in policy
        policy = messages[2]["content"]
        assert "veille_externe" in policy
        assert "rag_interne" in policy

    def test_all_messages_have_content(self) -> None:
        messages = run_pipeline("Test")
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert len(msg["content"]) > 0

    def test_pipeline_idempotent(self) -> None:
        result1 = run_pipeline("Same context")
        result2 = run_pipeline("Same context")
        assert result1 == result2
