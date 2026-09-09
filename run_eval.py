from __future__ import annotations

import argparse

from analysis.reporting import render_console_report
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
    args = parser.parse_args()

    engine = EvalEngine(args.config)
    results, decision = engine.run()
    print(render_console_report(decision))
    artifact_path = write_json_artifact(args.output, results, decision)
    print(f"\nArtifact: {artifact_path}")


if __name__ == "__main__":
    main()
