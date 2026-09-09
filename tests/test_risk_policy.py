from pipeline.engine import EvalEngine


def test_release_decision_exposes_risk_and_review_metadata():
    engine = EvalEngine("configs/sample_eval.yaml")
    _, decision = engine.run()

    assert decision.weighted_risk_score >= 0.0
    assert decision.human_review_count >= 0
    assert decision.decision in {"SHIP", "REVIEW", "BLOCK"}


def test_slice_metrics_include_severity_weights():
    engine = EvalEngine("configs/sample_eval.yaml")
    _, decision = engine.run()

    safety = decision.slice_metrics["safety"]
    assert safety.severity_weight == 8.0
    assert safety.weighted_risk >= 0.0
