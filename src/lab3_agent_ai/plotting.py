from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def make_plots(df: pd.DataFrame, figures_dir: Path) -> list[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    summary = df.groupby("mode")[["correctness", "groundedness", "completeness", "rubric"]].mean()
    ax = summary.plot(kind="bar", figsize=(10, 5), ylim=(0, 5))
    ax.set_title("Сравнение качества результатов")
    ax.set_ylabel("Средний балл")
    ax.set_xlabel("Конфигурация")
    plt.tight_layout()
    path = figures_dir / "quality_comparison.png"
    plt.savefig(path, dpi=180)
    plt.close()
    paths.append(path)

    process = df.groupby("mode")[["n_steps", "latency"]].mean()
    ax = process.plot(kind="bar", figsize=(9, 5))
    ax.set_title("Сравнение процесса выполнения")
    ax.set_ylabel("Среднее значение")
    ax.set_xlabel("Конфигурация")
    plt.tight_layout()
    path = figures_dir / "process_comparison.png"
    plt.savefig(path, dpi=180)
    plt.close()
    paths.append(path)

    return paths

