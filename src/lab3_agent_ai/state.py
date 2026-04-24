from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentState:
    topic: str
    objective: str
    step_id: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    notes: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""
    status: str = "running"
    stop_reason: str = ""
    tool_errors: int = 0
    evaluator_result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def log_step(
    state: AgentState,
    action: str,
    payload: dict[str, Any],
    result: Any,
    next_reason: str,
) -> None:
    if isinstance(result, str):
        result_summary = result[:500]
    else:
        result_summary = str(result)[:500]

    state.history.append(
        {
            "step_id": state.step_id,
            "action": action,
            "payload": payload,
            "result": result_summary,
            "n_sources": len(state.sources),
            "n_notes": len(state.notes),
            "next_reason": next_reason,
        }
    )
    state.step_id += 1
