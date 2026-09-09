from __future__ import annotations

import json
import re
from typing import Any, Dict

from .base import BaseGrader, GradeResult


class RuleBasedGrader(BaseGrader):
    name = "rule_based"

    def grade(self, case: Dict[str, Any]) -> GradeResult:
        slice_name = case["slice"]
        response = case.get("response", "")

        if slice_name == "tool_use":
            expected_tool = case.get("expected_tool")
            expected_args = case.get("expected_args", {})
            match = re.match(r"TOOL:(\w+)\s*(.*)", response.strip())
            if not match:
                return GradeResult(False, 0.0, "Tool call format not detected", self.name)

            actual_tool = match.group(1)
            raw_args = match.group(2).strip()
            actual_args = {}
            for token in raw_args.split():
                if "=" in token:
                    key, value = token.split("=", 1)
                    actual_args[key] = value

            tool_ok = actual_tool == expected_tool
            args_ok = all(str(actual_args.get(k)) == str(v) for k, v in expected_args.items())
            passed = tool_ok and args_ok
            return GradeResult(
                passed,
                1.0 if passed else 0.0,
                "Tool and arguments match expected call" if passed else "Tool or arguments differ from expected call",
                self.name,
            )

        if slice_name == "format_compliance":
            schema = case.get("expected_schema", {})
            try:
                parsed = json.loads(response)
            except json.JSONDecodeError:
                return GradeResult(False, 0.0, "Response is not valid JSON", self.name)

            for key, expected_type in schema.items():
                if key not in parsed:
                    return GradeResult(False, 0.0, f"Missing required key: {key}", self.name)
                if expected_type == "boolean" and not isinstance(parsed[key], bool):
                    return GradeResult(False, 0.0, f"Key {key} must be boolean", self.name)
            return GradeResult(True, 1.0, "Response satisfies deterministic schema", self.name)

        expected = str(case.get("expected", "")).strip().lower()
        passed = expected in response.strip().lower() if expected else bool(response.strip())
        return GradeResult(
            passed,
            1.0 if passed else 0.0,
            "Expected content found" if passed else "Expected content not found",
            self.name,
        )
