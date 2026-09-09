from __future__ import annotations

from typing import Dict

from .base import BaseGrader
from .hybrid import HybridGrader
from .llm_judge import LLMJudgeGrader
from .rule_based import RuleBasedGrader


class GraderRouter:
    def __init__(self) -> None:
        self._graders: Dict[str, BaseGrader] = {
            "rule_based": RuleBasedGrader(),
            "llm_judge": LLMJudgeGrader(),
            "hybrid": HybridGrader(),
        }

    def get(self, grader_name: str) -> BaseGrader:
        if grader_name not in self._graders:
            raise KeyError(f"Unknown grader: {grader_name}")
        return self._graders[grader_name]
