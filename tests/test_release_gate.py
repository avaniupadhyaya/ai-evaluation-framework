from pipeline.engine import EvalEngine


def test_release_decision_blocks_on_regression():
    engine = EvalEngine("configs/sample_eval.yaml")
    _, decision = engine.run()
    assert decision.decision in {"SHIP", "BLOCK"}
    assert "tool_use" in decision.slice_metrics
