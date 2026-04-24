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
export OPENROUTER_MODEL="meta-llama/llama-3.1-8b-instruct:free"
```

Если `OPENROUTER_MODEL` не задана, код попробует выбрать бесплатную модель из OpenRouter `/models`.

Полный запуск:

```bash
python3 scripts/run_experiments.py
```

Экономный запуск для проверки:

```bash
python3 scripts/run_experiments.py --limit 2 --top-k 3 --max-steps 4
```

## Результаты

- `output/traces/` - JSON trace для agent-запусков;
- `output/results/results.csv` - сырые результаты экспериментов;
- `output/results/summary.csv` - средние значения по конфигурациям;
- `output/figures/` - графики;
- `output/report/lab3_report.docx` - черновик отчета по результатам.

