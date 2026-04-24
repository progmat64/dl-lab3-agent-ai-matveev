from __future__ import annotations

import os
from typing import Protocol

import requests
from openai import OpenAI

from .config import LLMConfig


class LLM(Protocol):
    model_name: str

    def __call__(self, prompt: str) -> str:
        ...


def free_openrouter_models() -> list[str]:
    response = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
    response.raise_for_status()
    models = response.json().get("data", [])
    free_ids = []
    for model in models:
        pricing = model.get("pricing") or {}
        prompt_price = str(pricing.get("prompt", "1"))
        completion_price = str(pricing.get("completion", "1"))
        model_id = model.get("id", "")
        if model_id and prompt_price in {"0", "0.0"} and completion_price in {"0", "0.0"}:
            free_ids.append(model_id)

    preferred_exact = [
        "google/gemma-3-4b-it:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemma-3n-e4b-it:free",
        "openai/gpt-oss-20b:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "openrouter/free",
    ]
    ordered = [model_id for model_id in preferred_exact if model_id in free_ids]

    preferred_terms = ["gemma", "llama-3.2", "gpt-oss-20b", "qwen", "mistral", "deepseek"]
    for term in preferred_terms:
        for model_id in free_ids:
            if term in model_id.lower() and model_id not in ordered:
                ordered.append(model_id)

    for model_id in free_ids:
        if model_id not in ordered:
            ordered.append(model_id)

    return ordered


def choose_free_openrouter_model() -> str:
    free_ids = free_openrouter_models()
    if free_ids:
        return free_ids[0]

    return "openrouter/auto"


class OpenRouterLLM:
    def __init__(self, config: LLMConfig):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set. Use --mock-llm for a local smoke test.")

        explicit_model = config.model or os.environ.get("OPENROUTER_MODEL")
        if explicit_model:
            self.model_candidates = [explicit_model]
        else:
            self.model_candidates = free_openrouter_models() or ["openrouter/auto"]
        self.model_name = self.model_candidates[0]
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://localhost/lab3-agent-ai",
                "X-Title": "ITMO Lab3 Agent AI",
            },
        )

    def __call__(self, prompt: str) -> str:
        last_error: Exception | None = None
        for model in self.model_candidates:
            self.model_name = model
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                content = response.choices[0].message.content
                if content and content.strip():
                    return content
                last_error = RuntimeError(f"Model {model} returned an empty response")
                if len(self.model_candidates) > 1:
                    continue
                raise last_error
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                can_retry = (
                    "429" in message
                    or "403" in message
                    or "rate" in message
                    or "temporarily" in message
                    or "blocked" in message
                    or "permission" in message
                )
                if can_retry and len(self.model_candidates) > 1:
                    continue
                raise
        raise RuntimeError(f"All OpenRouter model candidates failed. Last error: {last_error}")


class MockLLM:
    model_name = "mock-llm"

    def __call__(self, prompt: str) -> str:
        lower = prompt.lower()
        if "верни только json" in lower or "json" in lower and "correctness" in lower:
            return (
                '{"correctness": 4, "groundedness": 4, "completeness": 4, '
                '"coverage_of_required_fields": 4, "source_consistency": 4, '
                '"comment": "Mock evaluation for pipeline verification."}'
            )
        return (
            "1) Определение темы: краткое определение на основе переданного контекста.\\n"
            "2) Основные подходы: поиск источников, извлечение аннотаций, сопоставление работ.\\n"
            "3) 3-5 ключевых работ: перечисляются найденные публикации из notes.\\n"
            "4) Применения: прикладные сценарии зависят от темы запроса.\\n"
            "5) Ограничения: качество зависит от полноты поиска и доступности аннотаций.\\n"
            "6) Использованные источники: OpenAlex и Wikipedia."
        )
