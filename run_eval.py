from __future__ import annotations

import argparse
from pathlib import Path

from analysis.reporting import (
    render_console_report,
    render_html_report,
    render_markdown_report,
    write_report,
)
from pipeline.artifacts import write_json_artifact
from pipeline.engine import EvalEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI evaluation framework")
    parser.add_argument("--config", required=True, help="Path to evaluation YAML config")
    parser.add_argument(
        "--output",
        default="artifacts/eval_results.json",
        help="Path for structured JSON evaluation results",
    )
    parser.add_argument(
        "--report-dir",
        default="artifacts/reports",
        help="Directory for Markdown and HTML release reports",
    )
    args = parser.parse_args()

    engine = EvalEngine(args.config)
    results, decision = engine.run()
    print(render_console_report(decision))

    artifact_path = write_json_artifact(args.output, results, decision)
    report_dir = Path(args.report_dir)
    markdown_path = write_report(
        str(report_dir / "eval_report.md"), render_markdown_report(decision)
    )
    html_path = write_report(
        str(report_dir / "eval_report.html"), render_html_report(decision)
    )

    print(f"\nJSON artifact: {artifact_path}")
    print(f"Markdown report: {markdown_path}")
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()
