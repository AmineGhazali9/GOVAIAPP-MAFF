"""Azure AI Foundry adapter — calls Foundry agents via AgentsClient."""

from __future__ import annotations

import logging

from maf_app.config import get_settings, get_agent_id, is_foundry_configured

logger = logging.getLogger(__name__)


def call_agent(agent_name: str, prompt: str) -> str:
    """Call an Azure AI Foundry agent by logical name.

    Returns the agent's text response.
    Raises RuntimeError if the call fails.
    """
    settings = get_settings()

    if not is_foundry_configured(agent_name):
        raise RuntimeError(
            f"Agent '{agent_name}' not configured "
            f"(FOUNDRY_ENABLED=false or agent ID missing)"
        )

    try:
        from azure.identity import DefaultAzureCredential
        from azure.ai.agents import AgentsClient
        from azure.ai.agents.models import ListSortOrder
    except ImportError as exc:
        raise RuntimeError(
            "azure-ai-agents and azure-identity packages are required. "
            "Install with: pip install azure-ai-agents azure-identity"
        ) from exc

    agent_id = get_agent_id(agent_name)
    endpoint = settings.foundry_project_endpoint

    logger.info("Calling Foundry agent=%s (id=%s)", agent_name, agent_id)

    try:
        client = AgentsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )

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
        logger.error("Foundry error agent=%s: %s", agent_name, exc)
        raise RuntimeError(
            f"Foundry call failed for '{agent_name}': {exc}"
        ) from exc
