from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from pipeline.models import CaseResult, ReleaseDecision


def write_json_artifact(
    output_path: str,
    results: Iterable[CaseResult],
    decision: ReleaseDecision,
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "release_decision": asdict(decision),
        "case_results": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)
