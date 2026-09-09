from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Protocol


class JudgeProvider(Protocol):
    name: str

    def evaluate(self, case: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass
class OpenAICompatibleJudgeProvider:
    """Minimal provider adapter for OpenAI-compatible chat-completions APIs.

    Environment variables:
      JUDGE_API_KEY       required
      JUDGE_BASE_URL      default: https://api.openai.com/v1
      JUDGE_MODEL         default: gpt-5-mini

    The provider expects strict JSON from the judge model with keys:
      passed: bool
      score: float [0,1]
      confidence: float [0,1]
      reason: str
    """

    name: str = "openai_compatible"

    def evaluate(self, case: Dict[str, Any]) -> Dict[str, Any]:
        api_key = os.getenv("JUDGE_API_KEY")
        if not api_key:
            raise RuntimeError("JUDGE_API_KEY is not configured")

        base_url = os.getenv("JUDGE_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.getenv("JUDGE_MODEL", "gpt-5-mini")

        rubric = {
            "slice": case.get("slice"),
            "prompt": case.get("prompt"),
            "response": case.get("response"),
            "expected": case.get("expected"),
            "context": case.get("context"),
            "metadata": case.get("metadata", {}),
        }

        system = (
            "You are an evaluation judge. Return ONLY valid JSON with keys: "
            "passed (boolean), score (0-1), confidence (0-1), reason (short string). "
            "Judge the model response against the requested evaluation slice, prompt, "
            "expected behavior, context, and metadata. Be conservative when evidence is ambiguous."
        )
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(rubric)},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }

        request = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))

        content = body["choices"][0]["message"]["content"]
        result = json.loads(content)
        return {
            "passed": bool(result["passed"]),
            "score": float(result["score"]),
            "confidence": float(result.get("confidence", result["score"])),
            "reason": str(result["reason"]),
        }


def build_provider(name: str | None) -> JudgeProvider | None:
    if not name or name == "offline":
        return None
    if name == "openai_compatible":
        return OpenAICompatibleJudgeProvider()
    raise KeyError(f"Unknown judge provider: {name}")
