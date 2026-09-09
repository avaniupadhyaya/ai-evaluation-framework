from analysis.regression import build_regression_report
from pipeline.models import CaseResult


def test_regression_report_flags_slice_beyond_tolerance():
    results = [
        CaseResult("1", "groundedness", True, 1.0, "g", "ok", severity="high"),
        CaseResult("2", "groundedness", False, 0.0, "g", "bad", severity="high"),
    ]
    report = build_regression_report(
        results,
        baseline={"groundedness": 0.90},
        max_regression_by_slice={"groundedness": 0.10},
    )
    assert len(report) == 1
    assert report[0].regressed is True
    assert report[0].delta == -0.40
