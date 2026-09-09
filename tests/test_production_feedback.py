from pipeline.production_feedback import production_failure_to_eval_case


def test_production_failure_becomes_high_risk_eval_asset():
    event = {
        "id": "prod-001",
        "slice": "safety",
        "prompt": "example",
        "response": "unsafe output",
        "expected": "safe refusal",
        "severity": "critical",
        "incident_id": "INC-42",
    }

    case = production_failure_to_eval_case(event)

    assert case["metadata"]["source"] == "production"
    assert case["metadata"]["high_risk"] is True
    assert case["metadata"]["incident_id"] == "INC-42"
    assert case["slice"] == "safety"
