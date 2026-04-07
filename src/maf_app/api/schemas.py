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


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    foundry_enabled: bool
