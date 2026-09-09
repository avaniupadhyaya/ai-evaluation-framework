from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def production_failure_to_eval_case(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a normalized production failure into a reusable eval asset.

    Expected keys are intentionally lightweight so teams can map their own incident
    schema into this contract.
    """
    return {
        "id": event["id"],
        "slice": event["slice"],
        "prompt": event.get("prompt", ""),
        "response": event.get("response", ""),
        "expected": event.get("expected", ""),
        "context": event.get("context", ""),
        "metadata": {
            "source": "production",
            "severity": event.get("severity", "medium"),
            "high_risk": event.get("severity") in {"high", "critical"},
            "incident_id": event.get("incident_id"),
        },
    }


def append_eval_case(output_path: str, case: Dict[str, Any]) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(case) + "\n")
    return str(path)
