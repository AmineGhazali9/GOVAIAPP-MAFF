"""MAF Orchestrator  sequential pipeline for AI governance policy generation.

Replaces AutoGen's RoundRobinGroupChat with a simple sequential loop.
Agents are called in fixed order: VeilleExterne -> RagInterne -> ProducteurPolitique.
"""

from __future__ import annotations

import logging
import time
import sys
from typing import Any, Callable

from maf_app.agents import AgentResult, PipelineContext
from maf_app.agents import veille_externe, rag_interne, producteur

logger = logging.getLogger(__name__)

# Pipeline agent order (immutable -- matches legacy business flow)
PIPELINE: list[Callable[[PipelineContext], AgentResult]] = [
    veille_externe.run,
    rag_interne.run,
    producteur.run,
]

# Mapping function -> logical agent name for step reporting
_AGENT_NAMES: dict[Callable[..., Any], str] = {
    veille_externe.run: "veille_externe",
    rag_interne.run: "rag_interne",
    producteur.run: "producteur_politique",
}


def run_pipeline(company_context: str) -> dict[str, Any]:
    """Execute the sequential agent pipeline.

    Args:
        company_context: The initial company context string.

    Returns:
        Dict with 'messages' (list of role/content dicts) and
        'steps' (list of agent/status/duration_s dicts).
    """
    logger.info("Starting MAF pipeline for: %s", company_context[:80])

    ctx = PipelineContext(initial_input=company_context)
    steps: list[dict[str, Any]] = []

    for agent_fn in PIPELINE:
        agent_name = _AGENT_NAMES.get(agent_fn, "unknown")
        t0 = time.monotonic()
        status = "done"
        fallback_reason = ""
        try:
            result = agent_fn(ctx)
            if result.content.startswith("[FALLBACK"):
                status = "fallback"
                fallback_reason = result.content.split("]", 1)[0].split(":", 1)[-1].strip() if ":" in result.content else ""
        except Exception as exc:
            status = "failed"
            fallback_reason = str(exc)
            logger.error("Agent %s failed: %s", agent_name, exc)
        elapsed = round(time.monotonic() - t0, 2)
        steps.append({
            "agent": agent_name,
            "status": status,
            "duration_s": elapsed,
            "fallback_reason": fallback_reason,
        })
        logger.info("Agent %s: %s (%.2fs)", agent_name, status, elapsed)

    messages: list[dict[str, str]] = []
    for result in ctx.results:
        messages.append({
            "role": result.source,
            "content": result.content,
        })

    logger.info("MAF pipeline completed: %d agent(s) responded", len(messages))
    return {"messages": messages, "steps": steps}


def main() -> None:
    """CLI entry point -- demo with sample company context."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    sample_context = (
        "Entreprise : TechCorp France | "
        "Secteur : Technologies | "
        "Maturite donnees : intermediaire | "
        "Principes : transparence, equite, robustesse | "
        "Contraintes : conformite EU AI Act 2025"
    )

    print("=" * 60)
    print("MAF Pipeline -- AI Governance Policy Generator")
    print("=" * 60)

    result = run_pipeline(sample_context)
    messages = result["messages"]
    steps = result["steps"]

    for msg in messages:
        print(f"\n--- {msg['role']} ---")
        print(msg["content"])

    print("\n--- Pipeline Steps ---")
    for step in steps:
        print(f"  {step['agent']}: {step['status']} ({step['duration_s']}s)")

    print("\n" + "=" * 60)
    print(f"Pipeline complete: {len(messages)} agent(s) responded.")
    print("=" * 60)
