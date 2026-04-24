from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_TOPICS = [
    "Agentic AI for customer support",
    "Graph RAG for enterprise knowledge systems",
    "LLM evaluation and process-aware metrics",
    "Tool-using language models in scientific search",
    "Retrieval-augmented generation in medicine",
    "Planning and reflection in LLM agents",
    "Human-in-the-loop AI systems",
    "Knowledge graphs for procedural reasoning",
]


@dataclass(frozen=True)
class Paths:
    output_dir: Path = Path("output")

    @property
    def traces_dir(self) -> Path:
        return self.output_dir / "traces"

    @property
    def results_dir(self) -> Path:
        return self.output_dir / "results"

    @property
    def figures_dir(self) -> Path:
        return self.output_dir / "figures"

    @property
    def report_dir(self) -> Path:
        return self.output_dir / "report"

    def ensure(self) -> None:
        for path in [self.traces_dir, self.results_dir, self.figures_dir, self.report_dir]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class AgentConfig:
    top_k: int = 5
    max_steps: int = 6
    min_sources: int = 3
    use_internal_evaluator: bool = False
    refine_threshold: float = 3.5


@dataclass(frozen=True)
class LLMConfig:
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 1200

