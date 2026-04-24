from __future__ import annotations

from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


def _add_table_from_df(doc: Document, df: pd.DataFrame) -> None:
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = str(col)
    for _, row_data in df.iterrows():
        row = table.add_row().cells
        for i, value in enumerate(row_data):
            row[i].text = str(value)


def build_report(df: pd.DataFrame, summary: pd.DataFrame, figure_paths: list[Path], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(1.8)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    title = doc.add_heading("Отчет по лабораторной работе 3: Agent AI", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("1. Цель эксперимента", level=1)
    doc.add_paragraph(
        "Цель работы - сравнить baseline-подход и агентный подход при подготовке "
        "научно-аналитического обзора, а также проверить эффект evaluator."
    )

    doc.add_heading("2. Конфигурации", level=1)
    for item in [
        "baseline: один ответ LLM на основе общего контекста Wikipedia.",
        "agent: пошаговый поиск, состояние, notes и JSON trace.",
        "agent + evaluator: agent с внутренней проверкой качества и возможной доработкой ответа.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("3. Сводные результаты", level=1)
    _add_table_from_df(doc, summary.reset_index())

    doc.add_heading("4. Результаты по запускам", level=1)
    display_cols = [
        "topic",
        "mode",
        "correctness",
        "groundedness",
        "completeness",
        "coverage_of_required_fields",
        "rubric",
        "n_steps",
        "latency",
        "tool_errors",
    ]
    _add_table_from_df(doc, df[display_cols].round(3))

    doc.add_heading("5. Графики", level=1)
    for fig in figure_paths:
        if fig.exists():
            doc.add_paragraph(fig.name)
            doc.add_picture(str(fig), width=Cm(15))

    doc.add_heading("6. Вывод", level=1)
    doc.add_paragraph(
        "Вывод следует уточнить после ручного анализа trace минимум для трех тем: "
        "нужно отдельно интерпретировать качество результата, число шагов, latency "
        "и типичные причины ошибок."
    )

    doc.save(output_path)
    return output_path

