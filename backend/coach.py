"""Send structured metrics to OpenRouter (Claude) and return JSON coaching feedback."""

import json
import os
import re
from typing import Any

from openai import OpenAI

from prompts import SYSTEM_PROMPT, build_user_prompt

_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)

_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-6")

_REQUIRED_KEYS = {"summary", "strengths", "improvements", "score_breakdown"}
_STRENGTH_KEYS = {"area", "detail"}
_IMPROVEMENT_KEYS = {"priority", "area", "issue", "tip", "timestamp_hint"}
_SCORE_KEYS = {"voice", "body_language", "engagement"}


def _strip_fences(text: str) -> str:
    """Remove markdown code fences the model may wrap around the JSON."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    return re.sub(r"\s*```$", "", text).strip()


def _validate(data: Any) -> None:
    """Raise ValueError if *data* doesn't match the expected coaching schema."""
    if not isinstance(data, dict):
        raise ValueError("Response is not a JSON object")

    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"Missing top-level keys: {missing}")

    if not isinstance(data["strengths"], list):
        raise ValueError("'strengths' must be a list")
    for s in data["strengths"]:
        if not _STRENGTH_KEYS.issubset(s):
            raise ValueError(f"Strength missing keys: {_STRENGTH_KEYS - s.keys()}")

    if not isinstance(data["improvements"], list):
        raise ValueError("'improvements' must be a list")
    for imp in data["improvements"]:
        if not _IMPROVEMENT_KEYS.issubset(imp):
            raise ValueError(f"Improvement missing keys: {_IMPROVEMENT_KEYS - imp.keys()}")

    sb = data["score_breakdown"]
    if not isinstance(sb, dict) or not _SCORE_KEYS.issubset(sb):
        raise ValueError(f"'score_breakdown' missing keys: {_SCORE_KEYS - sb.keys()}")


def _enforce_limits(data: dict) -> dict:
    """Cap strengths at 3 and improvements at 5, sorted by priority."""
    data["strengths"] = data["strengths"][:3]
    improvements = sorted(data["improvements"], key=lambda x: x.get("priority", 99))
    data["improvements"] = improvements[:5]
    return data


def get_feedback(metrics: dict) -> dict:
    """
    Send a metrics dict to the coaching model and return parsed JSON feedback.

    Retries once on JSON parse / validation failure, then raises.

    Args:
        metrics: Output from pipeline/get_metrics.py.

    Returns:
        Parsed and validated coaching dict.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(metrics)},
    ]

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = _client.chat.completions.create(
                model=_MODEL,
                messages=messages,
                temperature=0.4,
            )
            raw = _strip_fences(response.choices[0].message.content or "")
            data = json.loads(raw)
            _validate(data)
            return _enforce_limits(data)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt == 0:
                # Feed the bad response back so the model can self-correct
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your response was not valid JSON matching the schema. "
                        f"Error: {exc}. Please return only the corrected JSON."
                    ),
                })

    raise ValueError(f"Coaching model returned invalid JSON after 2 attempts: {last_error}")
