"""API routes for the MAF application."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from maf_app.api.schemas import CompanyContext, HealthResponse, PolicyDraftResponse, Source
from maf_app.config import get_settings
from maf_app.orchestrator import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(status="ok", foundry_enabled=settings.foundry_enabled)


@router.post("/generate-policy", response_model=PolicyDraftResponse)
def generate_policy(request: CompanyContext) -> PolicyDraftResponse:
    """Generate an AI governance policy draft.

    If Foundry is enabled, the pipeline uses Foundry agents.
    Otherwise, stub agents produce a deterministic response.
    """
    context_str = (
        f"Entreprise : {request.company_name} | "
        f"Secteur : {request.sector} | "
        f"Maturite donnees : {request.maturite_donnees} | "
        f"Principes : {', '.join(request.principles)} | "
        f"Contraintes : {', '.join(request.constraints)}"
    )
    logger.info("generate_policy called for %s", request.company_name)

    messages = run_pipeline(context_str)

    # Extract the final policy from the last agent (producteur_politique)
    policy_markdown = ""
    sources: list[Source] = []
    for msg in messages:
        if msg["role"] == "producteur_politique":
            policy_markdown = msg["content"]
        else:
            sources.append(
                Source(
                    title=msg["role"],
                    content=msg["content"],
                    source=msg["role"],
                )
            )

    return PolicyDraftResponse(policy_markdown=policy_markdown, sources=sources)
