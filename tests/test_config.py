"""Tests for maf_app.config module."""

from __future__ import annotations

import pytest

from maf_app.config import Settings, get_settings, is_foundry_configured, get_agent_id


class TestGetSettings:
    def test_defaults_when_no_env(self) -> None:
        settings = get_settings()
        assert settings.foundry_enabled is False
        assert settings.foundry_project_endpoint == ""
        assert settings.agent_veille_externe_id == ""

    def test_foundry_enabled_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.com")
        settings = get_settings()
        assert settings.foundry_enabled is True
        assert settings.foundry_project_endpoint == "https://example.com"

    def test_foundry_enabled_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "True")
        settings = get_settings()
        assert settings.foundry_enabled is True


class TestIsFoundryConfigured:
    def test_not_configured_by_default(self) -> None:
        assert is_foundry_configured("veille_externe") is False

    def test_configured_when_all_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.com")
        monkeypatch.setenv("FOUNDRY_AGENT_VEILLE_EXTERNE_ID", "agent-123")
        assert is_foundry_configured("veille_externe") is True

    def test_not_configured_missing_endpoint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_AGENT_VEILLE_EXTERNE_ID", "agent-123")
        assert is_foundry_configured("veille_externe") is False

    def test_not_configured_missing_agent_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.com")
        assert is_foundry_configured("veille_externe") is False

    def test_unknown_agent_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.com")
        assert is_foundry_configured("unknown_agent") is False


class TestGetAgentId:
    def test_returns_empty_for_unknown(self) -> None:
        assert get_agent_id("nonexistent") == ""

    def test_returns_id_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_AGENT_RAG_ID", "rag-456")
        assert get_agent_id("rag_interne") == "rag-456"
