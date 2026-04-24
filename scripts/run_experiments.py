#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab3_agent_ai.config import DEFAULT_TOPICS, AgentConfig, LLMConfig, Paths
from lab3_agent_ai.experiments import run_experiments, summarize
from lab3_agent_ai.llm import MockLLM, OpenRouterLLM
from lab3_agent_ai.plotting import make_plots
from lab3_agent_ai.report import build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lab 3 Agent AI experiments.")
    parser.add_argument("--mock-llm", action="store_true", help="Use deterministic fake LLM without API calls.")
    parser.add_argument("--model", default=None, help="OpenRouter model id. Overrides OPENROUTER_MODEL.")
    parser.add_argument("--limit", type=int, default=None, help="Run only first N topics.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of OpenAlex sources to pass to the agent.")
    parser.add_argument("--max-steps", type=int, default=6, help="Maximum agent trace steps.")
    parser.add_argument("--max-tokens", type=int, default=1200, help="LLM max_tokens.")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM temperature.")
    parser.add_argument("--output-dir", default="output", help="Output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    topics = DEFAULT_TOPICS[: args.limit] if args.limit else DEFAULT_TOPICS
    paths = Paths(Path(args.output_dir))
    paths.ensure()

    llm = MockLLM() if args.mock_llm else OpenRouterLLM(
        LLMConfig(model=args.model, temperature=args.temperature, max_tokens=args.max_tokens)
    )
    print(f"[model] {llm.model_name}")

    agent_config = AgentConfig(top_k=args.top_k, max_steps=args.max_steps)
    df = run_experiments(topics, llm, paths, agent_config)
    summary = summarize(df)
    print("\n[summary]")
    print(summary)

    figures = make_plots(df, paths.figures_dir)
    report_path = build_report(df, summary, figures, paths.report_dir / "lab3_report.docx")
    print(f"\n[done] results: {paths.results_dir / 'results.csv'}")
    print(f"[done] summary: {paths.results_dir / 'summary.csv'}")
    print(f"[done] report: {report_path}")


if __name__ == "__main__":
    main()

