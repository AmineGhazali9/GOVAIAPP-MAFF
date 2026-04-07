"""Azure AI Foundry adapter -- calls Foundry agents via AgentsClient."""

from __future__ import annotations

import logging
import threading

from maf_app.config import get_settings, get_agent_id, is_foundry_configured

logger = logging.getLogger(__name__)

# Module-level cached client to avoid re-creating DefaultAzureCredential
# (which probes IMDS ~10s) on every call.
_client_lock = threading.Lock()
_cached_client = None


def _get_client():
    """Return a cached AgentsClient singleton (thread-safe)."""
    global _cached_client
    if _cached_client is not None:
        return _cached_client

    with _client_lock:
        if _cached_client is not None:
            return _cached_client

        from azure.identity import AzureCliCredential
        from azure.ai.agents import AgentsClient

        settings = get_settings()
        logger.info("Creating AgentsClient (AzureCliCredential)...")
        _cached_client = AgentsClient(
            endpoint=settings.foundry_project_endpoint,
            credential=AzureCliCredential(),
        )
        logger.info("AgentsClient created and cached.")
        return _cached_client


def call_agent(agent_name: str, prompt: str) -> str:
    """Call an Azure AI Foundry agent by logical name.

    Returns the agent's text response.
    Raises RuntimeError if the call fails.
    """
    if not is_foundry_configured(agent_name):
        raise RuntimeError(
            f"Agent '{agent_name}' not configured "
            f"(FOUNDRY_ENABLED=false or agent ID missing)"
        )

    try:
        from azure.ai.agents.models import ListSortOrder
    except ImportError as exc:
        raise RuntimeError(
            "azure-ai-agents and azure-identity packages are required. "
            "Install with: pip install azure-ai-agents azure-identity"
        ) from exc

    agent_id = get_agent_id(agent_name)
    logger.info("Calling Foundry agent=%s (id=%s)", agent_name, agent_id)

    try:
        client = _get_client()

        agent = client.get_agent(agent_id)
        thread = client.threads.create()

        client.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )

        run = client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )

        if run.status == "failed":
            raise RuntimeError(f"Foundry run failed: {run.last_error}")

        msgs = client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING,
        )

        last_text = ""
        for msg in msgs:
            if msg.text_messages:
                last_text = msg.text_messages[-1].text.value

        if not last_text:
            raise RuntimeError(f"No response from Foundry agent '{agent_name}'")

        logger.info(
            "Foundry response agent=%s (%d chars)", agent_name, len(last_text)
        )
        return last_text

    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(
            f"Foundry call failed for agent '{agent_name}': {exc}"
        ) from exc
