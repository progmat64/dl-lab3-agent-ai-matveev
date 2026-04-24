from __future__ import annotations

from .llm import LLM
from .prompts import baseline_prompt
from .tools import search_wikipedia


def run_baseline(topic: str, llm: LLM) -> dict:
    wiki_context = search_wikipedia(topic)
    answer = llm(baseline_prompt(topic, wiki_context))
    return {
        "answer": answer,
        "notes": [],
        "n_steps": 1,
        "tool_errors": 0 if wiki_context else 1,
        "stop_reason": "baseline_answer_generated",
    }

