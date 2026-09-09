from __future__ import annotations

import os
from typing import Any, Dict

from .base import BaseGrader, GradeResult


class LLMJudgeGrader(BaseGrader):
    """Provider-agnostic judge interface.

    The starter implementation is offline-safe: it uses a conservative heuristic
    when no external judge is configured. Teams can replace `_invoke_judge`
    with their preferred model provider while preserving the same GradeResult contract.
    """

    name = "llm_judge"

    def grade(self, case: Dict[str, Any]) -> GradeResult:
        return self._invoke_judge(case)

    def _invoke_judge(self, case: Dict[str, Any]) -> GradeResult:
        response = str(case.get("response", "")).strip()
        expected = str(case.get("expected", "")).strip().lower()
        context = str(case.get("context", "")).strip().lower()
        slice_name = case.get("slice", "")

        if not response:
            return GradeResult(False, 0.0, "Empty response", self.name)

        response_l = response.lower()

        if slice_name == "groundedness":
            if expected and expected in response_l:
                return GradeResult(True, 1.0, "Response matches expected grounded evidence", self.name)
            if context and any(token in response_l for token in context.split() if len(token) > 5):
                return GradeResult(True, 0.8, "Response appears supported by provided context", self.name)
            return GradeResult(False, 0.4, "Grounding confidence is low", self.name, needs_human_review=True)

        if slice_name == "instruction_following":
            prompt = str(case.get("prompt", "")).lower()
            if "exactly three words" in prompt:
                passed = len(response.split()) == 3
                return GradeResult(
                    passed,
                    1.0 if passed else 0.3,
                    "Response follows exact word-count constraint" if passed else "Response violates exact word-count constraint",
                    self.name,
                )
            if "return only json" in prompt:
                passed = response.startswith("{") and response.endswith("}")
                return GradeResult(
                    passed,
                    1.0 if passed else 0.3,
                    "Response follows JSON-only constraint" if passed else "Response includes non-JSON content",
                    self.name,
                )

        # Conservative generic fallback for starter framework.
        passed = bool(expected and expected in response_l)
        return GradeResult(
            passed,
            1.0 if passed else 0.5,
            "Expected behavior detected" if passed else "Requires provider-backed judge or human review",
            self.name,
            needs_human_review=not passed,
        )
