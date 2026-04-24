# Лабораторная работа 3: Agent AI

Проект реализует сравнение трех конфигураций для подготовки научно-аналитического обзора:

- `baseline`: один LLM-ответ на основе краткого Wikipedia-контекста;
- `agent`: пошаговый режим с инструментами, состоянием и trace;
- `agent_evaluator`: agent с внутренней проверкой evaluator и одной возможной доработкой ответа.

## Быстрая проверка без API

```bash
python3 scripts/run_experiments.py --mock-llm --limit 2
```

## Реальный запуск через OpenRouter

Ключ не нужно записывать в код. Перед запуском задайте переменную окружения:

```bash
export OPENROUTER_API_KEY="..."
```

Можно явно указать модель:

```bash
export OPENROUTER_MODEL="openai/gpt-5-mini"
```

Если `OPENROUTER_MODEL` не задана, код использует платную модель `openai/gpt-5-mini` с `reasoning.effort=minimal`, чтобы снизить задержку и риск пустых ответов. Если она недоступна, временно заблокирована или у ключа исчерпан spend limit, скрипт попробует перейти на бесплатные модели из OpenRouter `/models`.

Для принудительного запуска на бесплатной модели можно указать ее явно:

```bash
export OPENROUTER_MODEL="openrouter/free"
```

Полный запуск:

```bash
python3 scripts/run_experiments.py
```

Экономный запуск для проверки:

```bash
python3 scripts/run_experiments.py --limit 2 --top-k 3 --max-steps 4 --max-tokens 700
```

## Результаты

- `output/traces/` - JSON trace для agent-запусков;
- `output/results/results.csv` - сырые результаты экспериментов;
- `output/results/summary.csv` - средние значения по конфигурациям;
- `output/figures/` - графики;
- `output/report/lab3_report.docx` - черновик отчета по результатам.
