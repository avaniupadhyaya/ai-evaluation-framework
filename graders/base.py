from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GradeResult:
    passed: bool
    score: float
    reason: str
    grader: str
    needs_human_review: bool = False
    confidence: float = 1.0
    severity: str = "medium"


class BaseGrader(ABC):
    name = "base"

    @abstractmethod
    def grade(self, case: Dict[str, Any]) -> GradeResult:
        raise NotImplementedError
