"""ProducteurPolitiqueAgent  synthesizes the final governance policy."""

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
    company_context = context.initial_input
    veille_content = ""
    rag_content = ""
    for r in context.results:
        if r.source == "veille_externe":
            veille_content = r.content
        elif r.source == "rag_interne":
            rag_content = r.content
    logger.info("ProducteurPolitiqueAgent processing (%d chars)", len(company_context))

    if is_foundry_configured(AGENT_NAME):
        prompt = (
            "Tu es un agent producteur de politiques de gouvernance IA. "
            "A partir du contexte entreprise, des signaux reglementaires et "
            "des references internes fournis, redige une POLITIQUE DE "
            "GOUVERNANCE IA complete en format Markdown.\n\n"
            "La politique DOIT contenir les sections suivantes :\n"
            "1. Cadre reglementaire applicable\n"
            "2. Principes directeurs\n"
            "3. Roles et responsabilites\n"
            "4. Gestion des risques algorithmiques\n"
            "5. Recommandations operationnelles\n"
            "6. Plan d'action avec priorites et echeances\n\n"
            "NE POSE PAS DE QUESTIONS. Redige directement la politique "
            "complete en Markdown.\n\n"
            f"CONTEXTE ENTREPRISE :\n{company_context}\n\n"
            f"SIGNAUX REGLEMENTAIRES (veille externe) :\n{veille_content}\n\n"
            f"REFERENCES INTERNES (RAG) :\n{rag_content}"
        )
        try:
            content = call_agent(AGENT_NAME, prompt)
        except Exception as exc:
            logger.warning("ProducteurPolitique Foundry fallback: %s", exc)
            content = f"[FALLBACK {AGENT_NAME}] Foundry unavailable: {exc}"
    else:
        content = (
            f"# Politique de Gouvernance IA\n\n"
            f"*Generee en mode STUB*\n\n"
            f"## 1. Cadre Reglementaire\n"
            f"{veille_content}\n\n"
            f"## 2. References Internes\n"
            f"{rag_content}\n\n"
            f"## 3. Recommandations\n"
            f"- Mettre en place un comite de gouvernance IA\n"
            f"- Implementer des evaluations d'impact algorithmique\n"
            f"- Assurer la tracabilite des decisions automatisees\n"
            f"- Former les equipes aux principes d'IA responsable\n\n"
            f"## 4. Plan d'Action\n"
            f"| Action | Priorite | Echeance |\n"
            f"|--------|----------|----------|\n"
            f"| Audit des modeles existants | Haute | T1 |\n"
            f"| Formation equipes | Moyenne | T2 |\n"
            f"| Mise en conformite EU AI Act | Haute | T3 |\n"
        )

    result = AgentResult(content=content, source=AGENT_NAME)
    context.add_result(result)
    logger.info("ProducteurPolitiqueAgent done (%d chars)", len(content))
    return result
