"""Pydantic schemas for the MAF API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

MaturiteDonnees = Literal["debutant", "intermediaire", "avance"]


class Source(BaseModel):
    """A source reference from the pipeline."""

    title: str
    content: str
    source: str


class PipelineStep(BaseModel):
    """Timing and status for a single pipeline agent step."""

    agent: str
    status: str  # "done" | "failed" | "fallback"
    duration_s: float
    fallback_reason: str = ""


class CompanyContext(BaseModel):
    """Input request for policy generation."""

    company_name: str
    sector: str
    maturite_donnees: MaturiteDonnees
    principles: list[str] = []
    constraints: list[str] = []


class PolicyDraftResponse(BaseModel):
    """Response containing the generated policy draft."""

    policy_markdown: str
    sources: list[Source] = []
    mode_used: str = "stub"
    steps: list[PipelineStep] = []
    duration_s: float = 0.0


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    foundry_enabled: bool
