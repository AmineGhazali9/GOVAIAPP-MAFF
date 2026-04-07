"""MAF agents -- base types and shared models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentResult:
    """Result returned by an agent after processing."""

    content: str
    source: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """Accumulated context passed through the agent pipeline."""

    initial_input: str
    results: list[AgentResult] = field(default_factory=list)

    def add_result(self, result: AgentResult) -> None:
        self.results.append(result)

    @property
    def last_content(self) -> str:
        """Return the content of the last agent result, or initial input."""
        if self.results:
            return self.results[-1].content
        return self.initial_input
