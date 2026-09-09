from graders.rule_based import RuleBasedGrader


def test_tool_use_passes_with_expected_tool_and_args():
    grader = RuleBasedGrader()
    case = {
        "slice": "tool_use",
        "response": "TOOL:weather location=Seattle",
        "expected_tool": "weather",
        "expected_args": {"location": "Seattle"},
    }
    result = grader.grade(case)
    assert result.passed is True
    assert result.score == 1.0


def test_format_compliance_rejects_invalid_json():
    grader = RuleBasedGrader()
    case = {
        "slice": "format_compliance",
        "response": "ok=true",
        "expected_schema": {"ok": "boolean"},
    }
    result = grader.grade(case)
    assert result.passed is False
