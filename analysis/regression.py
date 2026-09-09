from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from pipeline.models import CaseResult


@dataclass
class RegressionSlice:
    slice_name: str
    candidate_pass_rate: float
    baseline_pass_rate: float | None
    delta: float | None
    severity: str
    regressed: bool


def build_regression_report(
    results: List[CaseResult],
    baseline: Dict[str, float],
    max_regression_by_slice: Dict[str, float],
) -> List[RegressionSlice]:
    grouped: Dict[str, List[CaseResult]] = {}
    for result in results:
        grouped.setdefault(result.slice_name, []).append(result)

    report: List[RegressionSlice] = []
    for slice_name, slice_results in grouped.items():
        total = len(slice_results)
        candidate = sum(1 for r in slice_results if r.passed) / total if total else 0.0
        baseline_rate = baseline.get(slice_name)
        delta = None if baseline_rate is None else candidate - baseline_rate
        tolerance = float(max_regression_by_slice.get(slice_name, 0.0))
        regressed = baseline_rate is not None and (baseline_rate - candidate) > tolerance
        severity = max(
            (r.severity for r in slice_results),
            key=lambda value: {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(value, 2),
            default="medium",
        )
        report.append(
            RegressionSlice(
                slice_name=slice_name,
                candidate_pass_rate=candidate,
                baseline_pass_rate=baseline_rate,
                delta=delta,
                severity=severity,
                regressed=regressed,
            )
        )

    return sorted(
        report,
        key=lambda row: (
            {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(row.severity, 2),
            -(row.delta or 0.0),
        ),
        reverse=True,
    )
