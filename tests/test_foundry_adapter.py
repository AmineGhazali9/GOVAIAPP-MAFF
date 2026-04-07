"""Tests for maf_app.foundry.adapter module."""

from __future__ import annotations

import os

import pytest

from maf_app.foundry.adapter import call_agent


class TestCallAgentStub:
    def test_raises_when_not_configured(self) -> None:
        with pytest.raises(RuntimeError, match="not configured"):
            call_agent("veille_externe", "test prompt")

    def test_raises_for_unknown_agent(self) -> None:
        with pytest.raises(RuntimeError, match="not configured"):
            call_agent("unknown_agent", "test prompt")

    def test_raises_when_enabled_but_missing_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("FOUNDRY_ENABLED", "true")
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.com")
        # No agent ID set
        with pytest.raises(RuntimeError, match="not configured"):
            call_agent("veille_externe", "test prompt")


# Conditional Foundry live test
_FOUNDRY_CONFIGURED = (
    os.getenv("FOUNDRY_ENABLED", "").lower() == "true"
    and bool(os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""))
    and bool(os.getenv("FOUNDRY_AGENT_VEILLE_EXTERNE_ID", ""))
)


@pytest.mark.skipif(not _FOUNDRY_CONFIGURED, reason="Foundry not configured")
class TestCallAgentFoundryLive:
    """Live Foundry tests -- only run when credentials are available."""

    def test_veille_externe_returns_content(self) -> None:
        result = call_agent("veille_externe", "Test: analyse reglementaire IA")
        assert isinstance(result, str)
        assert len(result) > 0
