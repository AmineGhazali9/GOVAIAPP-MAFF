"""ProducteurPolitiqueAgent — synthesizes the final governance policy."""

from __future__ import annotations

import logging

from maf_app.agents import AgentResult, PipelineContext
from maf_app.config import is_foundry_configured
from maf_app.foundry.adapter import call_agent

logger = logging.getLogger(__name__)

AGENT_NAME = "producteur_politique"


def run(context: PipelineContext) -> AgentResult:
    """Execute the Producteur Politique agent.

    Uses Azure AI Foundry if configured, otherwise returns a stub policy.
    """
    prompt = context.last_content
    logger.info("ProducteurPolitiqueAgent processing (%d chars)", len(prompt))

    if is_foundry_configured(AGENT_NAME):
        try:
            content = call_agent(AGENT_NAME, prompt)
        except Exception as exc:
            logger.warning("ProducteurPolitique Foundry fallback: %s", exc)
            content = f"[FALLBACK {AGENT_NAME}] Foundry unavailable: {exc}"
    else:
        # Build a stub policy from accumulated context
        veille = ""
        rag = ""
        for r in context.results:
            if r.source == "veille_externe":
                veille = r.content
            elif r.source == "rag_interne":
                rag = r.content

        content = (
            f"# Politique de Gouvernance IA\n\n"
            f"*Générée en mode STUB*\n\n"
            f"## 1. Cadre Réglementaire\n"
            f"{veille}\n\n"
            f"## 2. Références Internes\n"
            f"{rag}\n\n"
            f"## 3. Recommandations\n"
            f"- Mettre en place un comité de gouvernance IA\n"
            f"- Implémenter des évaluations d'impact algorithmique\n"
            f"- Assurer la traçabilité des décisions automatisées\n"
            f"- Former les équipes aux principes d'IA responsable\n\n"
            f"## 4. Plan d'Action\n"
            f"| Action | Priorité | Échéance |\n"
            f"|--------|----------|----------|\n"
            f"| Audit des modèles existants | Haute | T1 |\n"
            f"| Formation équipes | Moyenne | T2 |\n"
            f"| Mise en conformité EU AI Act | Haute | T3 |\n"
        )

    result = AgentResult(content=content, source=AGENT_NAME)
    context.add_result(result)
    logger.info("ProducteurPolitiqueAgent done (%d chars)", len(content))
    return result
