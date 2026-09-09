import os

from graders.llm_judge import LLMJudgeGrader


def test_offline_judge_remains_ci_safe(monkeypatch):
    monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
    grader = LLMJudgeGrader()
    result = grader.grade(
        {
            "slice": "instruction_following",
            "prompt": "Return exactly three words",
            "response": "one two three",
            "expected": "",
        }
    )
    assert result.passed is True
    assert result.confidence >= 0.9


def test_provider_failure_escalates_to_human(monkeypatch):
    monkeypatch.setenv("JUDGE_PROVIDER", "openai_compatible")
    monkeypatch.delenv("JUDGE_API_KEY", raising=False)
    grader = LLMJudgeGrader()
    result = grader.grade(
        {
            "slice": "groundedness",
            "prompt": "Answer from context",
            "response": "test",
            "expected": "test",
        }
    )
    assert result.passed is False
    assert result.needs_human_review is True
    assert result.confidence == 0.0
