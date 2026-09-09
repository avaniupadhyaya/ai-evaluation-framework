from __future__ import annotations

import os
from typing import Any, Dict

from .base import BaseGrader, GradeResult
from .providers import build_provider


class LLMJudgeGrader(BaseGrader):
    """LLM judge with provider-backed and offline-safe execution modes.

    Set JUDGE_PROVIDER=openai_compatible to call a real provider adapter.
    If no provider is configured, the grader falls back to conservative local heuristics
    so the repository remains runnable in CI without secrets.
    """

    name = "llm_judge"

    def __init__(self) -> None:
        self.provider_name = os.getenv("JUDGE_PROVIDER", "offline")
        self.provider = build_provider(self.provider_name)

    def grade(self, case: Dict[str, Any]) -> GradeResult:
        if self.provider is not None:
            try:
                judged = self.provider.evaluate(case)
                return GradeResult(
                    passed=bool(judged["passed"]),
                    score=float(judged["score"]),
                    reason=str(judged["reason"]),
                    grader=f"{self.name}:{self.provider_name}",
                    confidence=float(judged.get("confidence", judged["score"])),
                    needs_human_review=False,
                )
            except Exception as exc:
                # Provider failures should degrade safely rather than silently pass.
                return GradeResult(
                    passed=False,
                    score=0.0,
                    reason=f"Provider-backed judge failed: {exc}",
                    grader=f"{self.name}:{self.provider_name}",
                    confidence=0.0,
                    needs_human_review=True,
                )

        return self._offline_grade(case)

    def _offline_grade(self, case: Dict[str, Any]) -> GradeResult:
        response = str(case.get("response", "")).strip()
        expected = str(case.get("expected", "")).strip().lower()
        context = str(case.get("context", "")).strip().lower()
        slice_name = case.get("slice", "")

        if not response:
            return GradeResult(False, 0.0, "Empty response", self.name, confidence=1.0)

        response_l = response.lower()

        if slice_name == "groundedness":
            if expected and expected in response_l:
                return GradeResult(True, 1.0, "Response matches expected grounded evidence", self.name, confidence=0.98)
            if context and any(token in response_l for token in context.split() if len(token) > 5):
                return GradeResult(True, 0.8, "Response appears supported by provided context", self.name, confidence=0.78)
            return GradeResult(False, 0.4, "Grounding confidence is low", self.name, needs_human_review=True, confidence=0.45)

        if slice_name == "instruction_following":
            prompt = str(case.get("prompt", "")).lower()
            if "exactly three words" in prompt:
                passed = len(response.split()) == 3
                return GradeResult(
                    passed,
                    1.0 if passed else 0.3,
                    "Response follows exact word-count constraint" if passed else "Response violates exact word-count constraint",
                    self.name,
                    confidence=0.99,
                )
            if "return only json" in prompt:
                passed = response.startswith("{") and response.endswith("}")
                return GradeResult(
                    passed,
                    1.0 if passed else 0.3,
                    "Response follows JSON-only constraint" if passed else "Response includes non-JSON content",
                    self.name,
                    confidence=0.95,
                )

        passed = bool(expected and expected in response_l)
        return GradeResult(
            passed,
            1.0 if passed else 0.5,
            "Expected behavior detected" if passed else "Requires provider-backed judge or human review",
            self.name,
            needs_human_review=not passed,
            confidence=0.75 if passed else 0.50,
        )
