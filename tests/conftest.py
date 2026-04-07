"""Shared test fixtures — enforce stub mode for deterministic tests."""

from __future__ import annotations

import pytest

# Environment variables to clean for stub isolation
_FOUNDRY_ENV_VARS = [
    "FOUNDRY_ENABLED",
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_AGENT_VEILLE_EXTERNE_ID",
    "FOUNDRY_AGENT_RAG_ID",
    "FOUNDRY_AGENT_PRODUCTEUR_ID",
]


@pytest.fixture(autouse=True)
def _no_foundry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force stub mode by removing all Foundry env vars."""
    for var in _FOUNDRY_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
