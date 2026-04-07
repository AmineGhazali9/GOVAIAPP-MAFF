"""API routes for the MAF application."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter

from maf_app.api.schemas import (
    CompanyContext,
    HealthResponse,
    PipelineStep,
    PolicyDraftResponse,
    Source,
)
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
    """Generate an AI governance policy draft."""
    context_str = (
        f"Entreprise : {request.company_name} | "
        f"Secteur : {request.sector} | "
        f"Maturite donnees : {request.maturite_donnees} | "
        f"Principes : {', '.join(request.principles)} | "
        f"Contraintes : {', '.join(request.constraints)}"
    )
    logger.info("generate_policy called for %s", request.company_name)

    settings = get_settings()
    mode_used = "foundry" if settings.foundry_enabled else "stub"

    t0 = time.monotonic()
    pipeline_result = run_pipeline(context_str)
    total_duration = round(time.monotonic() - t0, 2)

    messages = pipeline_result["messages"]
    raw_steps = pipeline_result["steps"]

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

    steps = [
        PipelineStep(
            agent=s["agent"],
            status=s["status"],
            duration_s=s["duration_s"],
            fallback_reason=s.get("fallback_reason", ""),
        )
        for s in raw_steps
    ]

    return PolicyDraftResponse(
        policy_markdown=policy_markdown,
        sources=sources,
        mode_used=mode_used,
        steps=steps,
        duration_s=total_duration,
    )
