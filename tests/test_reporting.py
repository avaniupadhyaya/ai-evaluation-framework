from analysis.reporting import render_html_report, render_markdown_report
from pipeline.models import ReleaseDecision, SliceMetric


def sample_decision() -> ReleaseDecision:
    return ReleaseDecision(
        decision="BLOCK",
        reasons=["safety: regression exceeded tolerance"],
        overall_pass_rate=0.91,
        slice_metrics={
            "safety": SliceMetric(
                slice_name="safety",
                pass_rate=0.97,
                total=100,
                passed=97,
                baseline=0.995,
                regression=0.025,
                threshold=0.99,
                max_regression=0.005,
                blocker=True,
                status="FAIL",
                severity_weight=8.0,
                weighted_risk=0.24,
            )
        },
        weighted_risk_score=0.24,
        human_review_count=2,
    )


def test_markdown_report_contains_release_context():
    report = render_markdown_report(sample_decision())
    assert "Evaluation Release Report" in report
    assert "Weighted risk score" in report
    assert "safety" in report
    assert "BLOCK" in report


def test_html_report_contains_release_context():
    report = render_html_report(sample_decision())
    assert "<!doctype html>" in report.lower()
    assert "Weighted risk" in report
    assert "safety" in report
    assert "BLOCK" in report
