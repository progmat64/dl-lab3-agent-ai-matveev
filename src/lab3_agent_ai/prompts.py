from __future__ import annotations

import json


def baseline_prompt(topic: str, wiki_context: str) -> str:
    return f"""
Сформируй краткий научно-аналитический обзор по теме: {topic}.

Используй общий контекст:
{wiki_context}

Обязательная структура ответа:
1) определение темы
2) основные подходы
3) 3-5 ключевых работ
4) возможные приложения
5) ограничения
6) использованные источники

Пиши по-русски, структурированно и без выдуманных библиографических деталей.
""".strip()


def agent_prompt(topic: str, wiki_context: str, notes: list[dict]) -> str:
    return f"""
Подготовь научно-аналитический обзор по теме: {topic}.

Общий контекст:
{wiki_context}

Найденные источники OpenAlex:
{json.dumps(notes, ensure_ascii=False, indent=2)}

Обязательная структура:
- определение темы
- основные подходы
- 3-5 ключевых работ с годами и кратким вкладом, если эти поля есть в источниках
- возможные приложения
- ограничения
- список использованных источников

Требования:
- опирайся только на переданные источники и контекст
- если данных недостаточно, явно укажи ограничение
- пиши по-русски
""".strip()


EVAL_PROMPT = """
Оцени ответ по шкале от 0 до 5 по критериям:
1. correctness
2. groundedness
3. completeness
4. coverage_of_required_fields
5. source_consistency

Верни только JSON:
{
  "correctness": int,
  "groundedness": int,
  "completeness": int,
  "coverage_of_required_fields": int,
  "source_consistency": int,
  "comment": "..."
}
""".strip()


def evaluator_prompt(answer: str, notes: list[dict]) -> str:
    return EVAL_PROMPT + "\n\nОтвет:\n" + answer + "\n\nИсточники:\n" + json.dumps(notes, ensure_ascii=False, indent=2)


def refine_prompt(topic: str, answer: str, notes: list[dict], eval_json: dict) -> str:
    return f"""
Доработай научно-аналитический обзор по теме: {topic}.

Текущий ответ:
{answer}

Источники:
{json.dumps(notes, ensure_ascii=False, indent=2)}

Оценка evaluator:
{json.dumps(eval_json, ensure_ascii=False, indent=2)}

Исправь только реальные недостатки: полноту обязательных полей, связь с источниками и ясность ограничений.
Не выдумывай публикации или факты, которых нет в источниках.
Пиши по-русски.
""".strip()

