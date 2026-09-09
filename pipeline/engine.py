from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import yaml

from graders.router import GraderRouter
from pipeline.models import CaseResult, ReleaseDecision, SliceMetric


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class EvalEngine:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config = load_yaml(config_path)
        self.router = GraderRouter()

    def run(self) -> tuple[List[CaseResult], ReleaseDecision]:
        cases = load_jsonl(self.config["dataset"])
        baseline = load_json(self.config["baseline_metrics"])
        routing = self.config.get("grader_routing", {})

        results: List[CaseResult] = []
        for case in cases:
            slice_name = case["slice"]
            grader_name = routing.get(slice_name, "rule_based")
            grader = self.router.get(grader_name)
            grade = grader.grade(case)
            results.append(
                CaseResult(
                    case_id=case["id"],
                    slice_name=slice_name,
                    passed=grade.passed,
                    score=grade.score,
                    grader=grade.grader,
                    reason=grade.reason,
                    needs_human_review=grade.needs_human_review,
                )
            )

        decision = self._build_release_decision(results, baseline)
        return results, decision

    def _build_release_decision(
        self,
        results: List[CaseResult],
        baseline: Dict[str, float],
    ) -> ReleaseDecision:
        grouped: Dict[str, List[CaseResult]] = defaultdict(list)
        for result in results:
            grouped[result.slice_name].append(result)

        slice_metrics: Dict[str, SliceMetric] = {}
        reasons: List[str] = []

        for slice_name, slice_results in grouped.items():
            rule = self.config["slices"][slice_name]
            total = len(slice_results)
            passed = sum(1 for r in slice_results if r.passed)
            pass_rate = passed / total if total else 0.0
            baseline_rate = baseline.get(slice_name)
            regression = None if baseline_rate is None else baseline_rate - pass_rate
            threshold = float(rule["threshold"])
            max_regression = float(rule["max_regression"])
            blocker = bool(rule.get("blocker", False))

            threshold_failed = pass_rate < threshold
            regression_failed = regression is not None and regression > max_regression
            human_review = any(r.needs_human_review for r in slice_results)

            status = "PASS"
            if threshold_failed or regression_failed:
                status = "FAIL"
            elif human_review:
                status = "REVIEW"

            if blocker and status == "FAIL":
                if threshold_failed:
                    reasons.append(
                        f"{slice_name}: pass rate {pass_rate:.1%} below threshold {threshold:.1%}"
                    )
                if regression_failed:
                    reasons.append(
                        f"{slice_name}: regression {regression:.1%} exceeds tolerance {max_regression:.1%}"
                    )

            slice_metrics[slice_name] = SliceMetric(
                slice_name=slice_name,
                pass_rate=pass_rate,
                total=total,
                passed=passed,
                baseline=baseline_rate,
                regression=regression,
                threshold=threshold,
                max_regression=max_regression,
                blocker=blocker,
                status=status,
            )

        overall_pass_rate = (
            sum(1 for result in results if result.passed) / len(results) if results else 0.0
        )
        minimum_overall = float(
            self.config.get("release_policy", {}).get("minimum_overall_pass_rate", 0.0)
        )
        if overall_pass_rate < minimum_overall:
            reasons.append(
                f"overall: pass rate {overall_pass_rate:.1%} below minimum {minimum_overall:.1%}"
            )

        decision = "BLOCK" if reasons else "SHIP"
        return ReleaseDecision(
            decision=decision,
            reasons=reasons,
            overall_pass_rate=overall_pass_rate,
            slice_metrics=slice_metrics,
        )
