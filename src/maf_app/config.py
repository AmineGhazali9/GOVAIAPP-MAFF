"""Configuration module -- loads settings from environment variables."""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Mapping: logical agent name -> environment variable for its Foundry ID
AGENT_ENV_VARS: dict[str, str] = {
    "veille_externe": "FOUNDRY_AGENT_VEILLE_EXTERNE_ID",
    "rag_interne": "FOUNDRY_AGENT_RAG_ID",
    "producteur_politique": "FOUNDRY_AGENT_PRODUCTEUR_ID",
}


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment."""

    foundry_enabled: bool = False
    foundry_project_endpoint: str = ""
    agent_veille_externe_id: str = ""
    agent_rag_id: str = ""
    agent_producteur_id: str = ""


def get_settings() -> Settings:
    """Build Settings from current environment variables."""
    return Settings(
        foundry_enabled=os.getenv("FOUNDRY_ENABLED", "false").lower() == "true",
        foundry_project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""),
        agent_veille_externe_id=os.getenv("FOUNDRY_AGENT_VEILLE_EXTERNE_ID", ""),
        agent_rag_id=os.getenv("FOUNDRY_AGENT_RAG_ID", ""),
        agent_producteur_id=os.getenv("FOUNDRY_AGENT_PRODUCTEUR_ID", ""),
    )


def is_foundry_configured(agent_name: str) -> bool:
    """Check whether Foundry is enabled AND the given agent ID is set."""
    settings = get_settings()
    if not settings.foundry_enabled or not settings.foundry_project_endpoint:
        return False
    env_var = AGENT_ENV_VARS.get(agent_name, "")
    if not env_var:
        return False
    return bool(os.getenv(env_var, ""))


def get_agent_id(agent_name: str) -> str:
    """Return the Foundry agent ID for a given logical agent name."""
    env_var = AGENT_ENV_VARS.get(agent_name, "")
    return os.getenv(env_var, "") if env_var else ""
