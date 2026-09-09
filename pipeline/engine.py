from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Dict, List

import yaml

from graders.router import GraderRouter
from pipeline.models import CaseResult, ReleaseDecision, SliceMetric

SEVERITY_WEIGHTS = {"low": 1.0, "medium": 2.0, "high": 4.0, "critical": 8.0}


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
        escalation = self.config.get("human_escalation", {})
        confidence_floor = float(escalation.get("confidence_floor", 0.70))
        high_risk_floor = float(escalation.get("high_risk_confidence_floor", 0.90))

        results: List[CaseResult] = []
        for case in cases:
            slice_name = case["slice"]
            grader_name = routing.get(slice_name, "rule_based")
            grader = self.router.get(grader_name)
            grade = grader.grade(case)
            metadata = case.get("metadata", {}) or {}
            severity = str(metadata.get("severity", grade.severity or "medium")).lower()
            high_risk = bool(metadata.get("high_risk")) or severity in {"high", "critical"}
            floor = high_risk_floor if high_risk else confidence_floor
            needs_review = grade.needs_human_review or grade.confidence < floor
            results.append(
                CaseResult(
                    case_id=case["id"],
                    slice_name=slice_name,
                    passed=grade.passed,
                    score=grade.score,
                    grader=grade.grader,
                    reason=grade.reason,
                    needs_human_review=needs_review,
                    confidence=grade.confidence,
                    severity=severity,
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
        total_weighted_risk = 0.0
        total_weight = 0.0

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
            severity = str(rule.get("severity", "medium")).lower()
            severity_weight = float(rule.get("severity_weight", SEVERITY_WEIGHTS.get(severity, 2.0)))

            threshold_failed = pass_rate < threshold
            regression_failed = regression is not None and regression > max_regression
            human_review = any(r.needs_human_review for r in slice_results)
            weighted_risk = (1.0 - pass_rate) * severity_weight
            total_weighted_risk += weighted_risk
            total_weight += severity_weight

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
                severity_weight=severity_weight,
                weighted_risk=weighted_risk,
            )

        overall_pass_rate = (
            sum(1 for result in results if result.passed) / len(results) if results else 0.0
        )
        release_policy = self.config.get("release_policy", {})
        minimum_overall = float(release_policy.get("minimum_overall_pass_rate", 0.0))
        if overall_pass_rate < minimum_overall:
            reasons.append(
                f"overall: pass rate {overall_pass_rate:.1%} below minimum {minimum_overall:.1%}"
            )

        weighted_risk_score = total_weighted_risk / total_weight if total_weight else 0.0
        max_weighted_risk = release_policy.get("max_weighted_risk_score")
        if max_weighted_risk is not None and weighted_risk_score > float(max_weighted_risk):
            reasons.append(
                f"risk: weighted risk score {weighted_risk_score:.3f} exceeds maximum {float(max_weighted_risk):.3f}"
            )

        human_review_count = sum(1 for r in results if r.needs_human_review)
        max_pending_reviews = release_policy.get("max_pending_human_reviews")
        if max_pending_reviews is not None and human_review_count > int(max_pending_reviews):
            reasons.append(
                f"review: {human_review_count} cases require human review; maximum allowed is {int(max_pending_reviews)}"
            )

        decision = "BLOCK" if reasons else ("REVIEW" if human_review_count else "SHIP")
        return ReleaseDecision(
            decision=decision,
            reasons=reasons,
            overall_pass_rate=overall_pass_rate,
            slice_metrics=slice_metrics,
            weighted_risk_score=weighted_risk_score,
            human_review_count=human_review_count,
        )
