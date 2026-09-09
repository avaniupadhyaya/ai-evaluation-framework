from __future__ import annotations

from typing import Any, Dict

from .base import BaseGrader, GradeResult
from .llm_judge import LLMJudgeGrader


class HybridGrader(BaseGrader):
    name = "hybrid"

    def __init__(self) -> None:
        self.judge = LLMJudgeGrader()

    def grade(self, case: Dict[str, Any]) -> GradeResult:
        primary = self.judge.grade(case)

        metadata = case.get("metadata", {}) or {}
        high_risk = bool(metadata.get("high_risk"))

        if high_risk and primary.score < 0.95:
            return GradeResult(
                passed=False,
                score=primary.score,
                reason=f"High-risk case requires human adjudication: {primary.reason}",
                grader=self.name,
                needs_human_review=True,
            )

        return GradeResult(
            passed=primary.passed,
            score=primary.score,
            reason=f"Hybrid primary result: {primary.reason}",
            grader=self.name,
            needs_human_review=primary.needs_human_review,
        )
