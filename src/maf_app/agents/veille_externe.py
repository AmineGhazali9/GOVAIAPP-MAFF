"""VeilleExterneAgent — collects external regulatory signals."""

from __future__ import annotations

import logging

from maf_app.agents import AgentResult, PipelineContext
from maf_app.config import is_foundry_configured
from maf_app.foundry.adapter import call_agent

logger = logging.getLogger(__name__)

AGENT_NAME = "veille_externe"


def run(context: PipelineContext) -> AgentResult:
    """Execute the Veille Externe agent.

    Uses Azure AI Foundry if configured, otherwise returns a stub response.
    """
    prompt = context.last_content
    logger.info("VeilleExterneAgent processing (%d chars)", len(prompt))

    if is_foundry_configured(AGENT_NAME):
        try:
            content = call_agent(AGENT_NAME, prompt)
        except Exception as exc:
            logger.warning("VeilleExterne Foundry fallback: %s", exc)
            content = f"[FALLBACK {AGENT_NAME}] Foundry unavailable: {exc}"
    else:
        content = (
            f"[STUB {AGENT_NAME}] Signaux réglementaires identifiés :\n"
            f"- EU AI Act : obligations de transparence et gouvernance\n"
            f"- OCDE : principes d'IA responsable\n"
            f"- CNIL : recommandations sur l'IA et les données personnelles\n"
            f"- Contexte analysé : {prompt[:200]}"
        )

    result = AgentResult(content=content, source=AGENT_NAME)
    context.add_result(result)
    logger.info("VeilleExterneAgent done (%d chars)", len(content))
    return result
