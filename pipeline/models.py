from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CaseResult:
    case_id: str
    slice_name: str
    passed: bool
    score: float
    grader: str
    reason: str
    needs_human_review: bool = False
    confidence: float = 1.0
    severity: str = "medium"


@dataclass
class SliceMetric:
    slice_name: str
    pass_rate: float
    total: int
    passed: int
    baseline: float | None
    regression: float | None
    threshold: float
    max_regression: float
    blocker: bool
    status: str
    severity_weight: float = 1.0
    weighted_risk: float = 0.0


@dataclass
class ReleaseDecision:
    decision: str
    reasons: List[str]
    overall_pass_rate: float
    slice_metrics: Dict[str, SliceMetric]
    weighted_risk_score: float = 0.0
    human_review_count: int = 0
