from __future__ import annotations

import json
import re
from typing import Any

from .llm import LLM
from .prompts import evaluator_prompt


CRITERIA = [
    "correctness",
    "groundedness",
    "completeness",
    "coverage_of_required_fields",
    "source_consistency",
]


def parse_eval_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"comment": "Evaluator returned invalid JSON: " + raw[:300]}

    for key in CRITERIA:
        value = data.get(key, 0)
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 0
        data[key] = max(0, min(5, value))

    data["rubric"] = sum(data[key] for key in CRITERIA) / len(CRITERIA)
    data.setdefault("comment", "")
    return data


def evaluate_answer(answer: str, notes: list[dict], llm: LLM) -> dict[str, Any]:
    raw = llm(evaluator_prompt(answer, notes))
    return parse_eval_json(raw)

