from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import AgentConfig
from .evaluator import evaluate_answer
from .llm import LLM
from .prompts import agent_prompt, refine_prompt
from .state import AgentState, log_step
from .tools import normalize_work, search_openalex, search_wikipedia


def save_trace(state: AgentState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)


def run_agent(topic: str, llm: LLM, config: AgentConfig) -> AgentState:
    state = AgentState(topic=topic, objective="Подготовить структурированный научно-аналитический обзор темы")
    tool_errors = 0

    wiki_context = search_wikipedia(topic)
    if not wiki_context:
        tool_errors += 1
    log_step(
        state,
        "search_wikipedia",
        {"topic": topic},
        wiki_context or "empty result",
        "need general context before publication search",
    )

    try:
        raw_sources = search_openalex(topic, per_page=max(config.top_k, config.min_sources))
    except Exception as exc:
        raw_sources = []
        tool_errors += 1
        log_step(state, "search_openalex", {"query": topic}, f"error: {exc}", "fallback to empty source list")

    state.sources = raw_sources
    log_step(
        state,
        "search_openalex",
        {"query": topic, "per_page": max(config.top_k, config.min_sources)},
        f"found={len(raw_sources)}",
        "extract notes from returned publications",
    )

    if len(raw_sources) < config.min_sources and state.step_id < config.max_steps:
        retry_query = topic + " survey review"
        try:
            retry_sources = search_openalex(retry_query, per_page=config.top_k)
            state.sources.extend(retry_sources)
        except Exception as exc:
            tool_errors += 1
            retry_sources = []
            log_step(state, "search_openalex_retry", {"query": retry_query}, f"error: {exc}", "continue with available sources")
        log_step(
            state,
            "search_openalex_retry",
            {"query": retry_query, "per_page": config.top_k},
            f"found={len(retry_sources)}",
            "continue with merged sources",
        )

    notes = [normalize_work(work) for work in state.sources[: config.top_k]]
    state.notes = notes
    log_step(
        state,
        "extract_notes",
        {"n_sources": len(state.sources), "top_k": config.top_k},
        f"notes_prepared={len(notes)}",
        "generate final answer from context and notes",
    )

    state.final_answer = llm(agent_prompt(topic, wiki_context, notes))
    log_step(
        state,
        "generate_final_answer",
        {"topic": topic},
        state.final_answer,
        "finish or run evaluator depending on configuration",
    )

    if config.use_internal_evaluator and state.step_id < config.max_steps:
        state.evaluator_result = evaluate_answer(state.final_answer, notes, llm)
        log_step(
            state,
            "internal_evaluator",
            {"criteria": list(state.evaluator_result.keys())},
            state.evaluator_result,
            "refine if rubric is below threshold",
        )
        if state.evaluator_result.get("rubric", 0) < config.refine_threshold and state.step_id < config.max_steps:
            state.final_answer = llm(refine_prompt(topic, state.final_answer, notes, state.evaluator_result))
            log_step(
                state,
                "refine_final_answer",
                {"threshold": config.refine_threshold},
                state.final_answer,
                "final answer refined after evaluator feedback",
            )

    state.status = "finished"
    state.tool_errors = tool_errors
    state.stop_reason = "final_answer_generated"
    if tool_errors:
        state.stop_reason += f"_with_{tool_errors}_tool_errors"
    log_step(
        state,
        "finish",
        {"status": state.status, "stop_reason": state.stop_reason},
        state.stop_reason,
        "stop criterion reached",
    )
    return state


def state_to_run_result(state: AgentState) -> dict[str, Any]:
    return {
        "answer": state.final_answer,
        "notes": state.notes,
        "n_steps": len(state.history),
        "tool_errors": state.tool_errors,
        "stop_reason": state.stop_reason,
        "state": state,
    }
