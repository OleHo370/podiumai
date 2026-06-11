"""Send structured metrics to OpenRouter (Claude) and return JSON coaching feedback."""

import os
import json
from openai import OpenAI

_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)

_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

_SYSTEM_PROMPT = """You are PodiumAI, an expert public-speaking coach.
You receive structured metrics from a recorded speech and return actionable JSON feedback.
Always respond with valid JSON matching the schema below — no markdown fences, no extra text.

Schema:
{
  "overall_score": <0-100 integer>,
  "summary": "<2-3 sentence overall impression>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": [
    {"area": "<label>", "detail": "<specific, actionable advice>"}
  ],
  "drill": "<one concrete 60-second practice exercise the speaker can do right now>"
}"""


def get_feedback(metrics: dict) -> dict:
    """
    Send a metrics dict to the LLM and return parsed JSON coaching feedback.

    TODO: Add retry logic and graceful error handling for API failures.
    TODO: Tune the prompt with few-shot examples once the pipeline produces real data.

    Args:
        metrics: Output from pipeline/get_metrics.py — keys match Metrics model fields.

    Returns:
        Parsed feedback dict matching the schema in _SYSTEM_PROMPT.
    """
    user_message = (
        "Here are the metrics from the speaker's presentation:\n"
        + json.dumps(metrics, indent=2)
        + "\n\nPlease provide your coaching feedback as JSON."
    )

    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)
