from __future__ import annotations

import argparse

from analysis.reporting import render_console_report
from pipeline.engine import EvalEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI evaluation framework")
    parser.add_argument("--config", required=True, help="Path to evaluation YAML config")
    args = parser.parse_args()

    engine = EvalEngine(args.config)
    _, decision = engine.run()
    print(render_console_report(decision))


if __name__ == "__main__":
    main()
