"""RagInterneAgent — enriches context with internal documents."""

from __future__ import annotations

import logging

from maf_app.agents import AgentResult, PipelineContext
from maf_app.config import is_foundry_configured
from maf_app.foundry.adapter import call_agent

logger = logging.getLogger(__name__)

AGENT_NAME = "rag_interne"


def run(context: PipelineContext) -> AgentResult:
    """Execute the RAG Interne agent.

    Uses Azure AI Foundry if configured, otherwise returns a stub response.
    """
    prompt = context.last_content
    logger.info("RagInterneAgent processing (%d chars)", len(prompt))

    if is_foundry_configured(AGENT_NAME):
        try:
            content = call_agent(AGENT_NAME, prompt)
        except Exception as exc:
            logger.warning("RagInterne Foundry fallback: %s", exc)
            content = f"[FALLBACK {AGENT_NAME}] Foundry unavailable: {exc}"
    else:
        content = (
            f"[STUB {AGENT_NAME}] Documents internes pertinents :\n"
            f"- Politique de gouvernance des données v2.1\n"
            f"- Charte éthique IA de l'entreprise\n"
            f"- Procédure d'évaluation des risques algorithmiques\n"
            f"- Enrichissement basé sur : {prompt[:200]}"
        )

    result = AgentResult(content=content, source=AGENT_NAME)
    context.add_result(result)
    logger.info("RagInterneAgent done (%d chars)", len(content))
    return result
