"""RagInterneAgent -- enriches context with internal documents."""

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
    company_context = context.initial_input
    veille_content = ""
    for r in context.results:
        if r.source == "veille_externe":
            veille_content = r.content
    logger.info("RagInterneAgent processing (%d chars)", len(company_context))

    if is_foundry_configured(AGENT_NAME):
        prompt = (
            "Tu es un agent RAG (Retrieval Augmented Generation) specialise "
            "en gouvernance IA. A partir du contexte entreprise et des signaux "
            "reglementaires fournis, enrichis l'analyse avec des references "
            "aux documents internes pertinents (politiques, normes ISO, NIST, "
            "chartes ethiques, procedures). "
            "NE POSE PAS DE QUESTIONS. Produis directement ton enrichissement.\n\n"
            f"CONTEXTE ENTREPRISE :\n{company_context}\n\n"
            f"SIGNAUX REGLEMENTAIRES (veille externe) :\n{veille_content}"
        )
        try:
            content = call_agent(AGENT_NAME, prompt)
        except Exception as exc:
            logger.warning("RagInterne Foundry fallback: %s", exc)
            content = f"[FALLBACK {AGENT_NAME}] Foundry unavailable: {exc}"
    else:
        content = (
            f"[STUB {AGENT_NAME}] Documents internes pertinents :\n"
            f"- Politique de gouvernance des donnees v2.1\n"
            f"- Charte ethique IA de l'entreprise\n"
            f"- Procedure d'evaluation des risques algorithmiques\n"
            f"- Enrichissement base sur : {company_context[:200]}"
        )

    result = AgentResult(content=content, source=AGENT_NAME)
    context.add_result(result)
    logger.info("RagInterneAgent done (%d chars)", len(content))
    return result
