from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from .agent import run_agent, save_trace, state_to_run_result
from .baseline import run_baseline
from .config import AgentConfig, Paths
from .evaluator import CRITERIA, evaluate_answer
from .llm import LLM


def _safe_name(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")[:80]


def run_single(topic: str, mode: str, llm: LLM, paths: Paths, agent_config: AgentConfig) -> dict:
    start = time.time()

    if mode == "baseline":
        result = run_baseline(topic, llm)
    elif mode == "agent":
        state = run_agent(topic, llm, agent_config)
        result = state_to_run_result(state)
        save_trace(state, paths.traces_dir / f"{_safe_name(topic)}__agent.json")
    elif mode == "agent_evaluator":
        state = run_agent(topic, llm, AgentConfig(**{**agent_config.__dict__, "use_internal_evaluator": True}))
        result = state_to_run_result(state)
        save_trace(state, paths.traces_dir / f"{_safe_name(topic)}__agent_evaluator.json")
    else:
        raise ValueError(f"Unknown mode: {mode}")

    latency = time.time() - start
    eval_json = evaluate_answer(result["answer"], result["notes"], llm)

    record = {
        "topic": topic,
        "mode": mode,
        "model": llm.model_name,
        "latency": latency,
        "n_steps": result["n_steps"],
        "tool_errors": result["tool_errors"],
        "stop_reason": result["stop_reason"],
    }
    for key in CRITERIA:
        record[key] = eval_json[key]
    record["rubric"] = eval_json["rubric"]
    record["evaluator_comment"] = eval_json.get("comment", "")
    return record


def run_experiments(topics: list[str], llm: LLM, paths: Paths, agent_config: AgentConfig) -> pd.DataFrame:
    paths.ensure()
    records = []
    for topic in topics:
        for mode in ["baseline", "agent", "agent_evaluator"]:
            print(f"[run] {mode}: {topic}")
            records.append(run_single(topic, mode, llm, paths, agent_config))

    df = pd.DataFrame(records)
    results_path = paths.results_dir / "results.csv"
    df.to_csv(results_path, index=False)

    summary = summarize(df)
    summary.to_csv(paths.results_dir / "summary.csv")
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    cols = CRITERIA + ["rubric", "n_steps", "latency", "tool_errors"]
    return df.groupby("mode")[cols].mean().round(3)

