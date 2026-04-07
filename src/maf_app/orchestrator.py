"""MAF Orchestrator — sequential pipeline for AI governance policy generation.

Replaces AutoGen's RoundRobinGroupChat with a simple sequential loop.
Agents are called in fixed order: VeilleExterne → RagInterne → ProducteurPolitique.
"""

from __future__ import annotations

import logging
import sys
from typing import Callable

from maf_app.agents import AgentResult, PipelineContext
from maf_app.agents import veille_externe, rag_interne, producteur

logger = logging.getLogger(__name__)

# Pipeline agent order (immutable — matches legacy business flow)
PIPELINE: list[Callable[[PipelineContext], AgentResult]] = [
    veille_externe.run,
    rag_interne.run,
    producteur.run,
]


def run_pipeline(company_context: str) -> list[dict[str, str]]:
    """Execute the sequential agent pipeline.

    Args:
        company_context: The initial company context string.

    Returns:
        List of message dicts with 'role' and 'content' keys.
    """
    logger.info("Starting MAF pipeline for: %s", company_context[:80])

    ctx = PipelineContext(initial_input=company_context)

    for agent_fn in PIPELINE:
        agent_fn(ctx)

    messages: list[dict[str, str]] = []
    for result in ctx.results:
        messages.append({
            "role": result.source,
            "content": result.content,
        })

    logger.info("MAF pipeline completed: %d agent(s) responded", len(messages))
    return messages


def main() -> None:
    """CLI entry point — demo with sample company context."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    sample_context = (
        "Entreprise : TechCorp France | "
        "Secteur : Technologies | "
        "Maturité données : intermediaire | "
        "Principes : transparence, équité, robustesse | "
        "Contraintes : conformité EU AI Act 2025"
    )

    print("=" * 60)
    print("MAF Pipeline — AI Governance Policy Generator")
    print("=" * 60)

    messages = run_pipeline(sample_context)

    for msg in messages:
        print(f"\n--- {msg['role']} ---")
        print(msg["content"])

    print("\n" + "=" * 60)
    print(f"Pipeline complete: {len(messages)} agent(s) responded.")
    print("=" * 60)


if __name__ == "__main__":
    main()
