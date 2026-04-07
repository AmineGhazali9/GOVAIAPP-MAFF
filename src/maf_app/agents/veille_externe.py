"""VeilleExterneAgent  collects external regulatory signals."""

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
    company_context = context.initial_input
    logger.info("VeilleExterneAgent processing (%d chars)", len(company_context))

    if is_foundry_configured(AGENT_NAME):
        prompt = (
            "Tu es un agent de veille reglementaire specialise en gouvernance IA. "
            "Analyse le contexte entreprise ci-dessous et produis directement "
            "une liste structuree des signaux reglementaires pertinents "
            "(EU AI Act, OCDE, lois nationales, normes sectorielles) avec "
            "leur impact pour cette entreprise. "
            "NE POSE PAS DE QUESTIONS. Reponds directement avec ton analyse.\n\n"
            f"CONTEXTE ENTREPRISE :\n{company_context}"
        )
        try:
            content = call_agent(AGENT_NAME, prompt)
        except Exception as exc:
            logger.warning("VeilleExterne Foundry fallback: %s", exc)
            content = f"[FALLBACK {AGENT_NAME}] Foundry unavailable: {exc}"
    else:
        content = (
            f"[STUB {AGENT_NAME}] Signaux reglementaires identifies :\n"
            f"- EU AI Act : obligations de transparence et gouvernance\n"
            f"- OCDE : principes d'IA responsable\n"
            f"- CNIL : recommandations sur l'IA et les donnees personnelles\n"
            f"- Contexte analyse : {company_context[:200]}"
        )

    result = AgentResult(content=content, source=AGENT_NAME)
    context.add_result(result)
    logger.info("VeilleExterneAgent done (%d chars)", len(content))
    return result
