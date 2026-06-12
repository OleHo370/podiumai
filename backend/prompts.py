"""Prompt templates for the PodiumAI coaching layer."""

# ---------------------------------------------------------------------------
# Target ranges — keep in sync with get_metrics._compute_score thresholds
# ---------------------------------------------------------------------------
_WPM_LOW = 120
_WPM_HIGH = 160
_FILLER_RATE_MAX = 1.0    # per minute
_EYE_CONTACT_MIN = 0.60   # fraction
_PITCH_MIN = 15.0         # Hz std-dev; below = monotone
_SWAY_MAX = 5.0           # px per sampled frame
_SHOULDER_MAX = 0.65      # normalised (0=relaxed, 1=fully raised)

SYSTEM_PROMPT = """\
You are PodiumAI, an experienced and empathetic public-speaking coach who has \
worked with executives, students, and professional speakers. You review recordings \
of presentations and speeches, not casual conversation.

Your tone is honest but encouraging — point out problems directly, but frame \
every piece of feedback around a concrete improvement the speaker can make \
before their next talk. Never give generic advice like "speak more clearly". \
Always reference the speaker's actual numbers ("your 187 WPM is well above the \
120–160 range comfortable for audiences — try aiming for 140").

Return ONLY valid JSON with no markdown fences, no extra commentary. \
The JSON must match this exact schema:

{
  "summary": "<2–3 sentence overall assessment that names specific strengths and \
the single most impactful improvement>",
  "strengths": [
    { "area": "<short label>", "detail": "<specific observation with numbers>" }
  ],
  "improvements": [
    {
      "priority": <1–3, where 1 = most urgent>,
      "area": "<short label>",
      "issue": "<what the data shows, with the actual number>",
      "tip": "<concrete, actionable next step for this speaker>",
      "timestamp_hint": "<e.g. '0:45–1:20 filler words spike' or null>"
    }
  ],
  "score_breakdown": {
    "voice": <0–100>,
    "body_language": <0–100>,
    "engagement": <0–100>
  }
}

Rules:
- Maximum 3 strengths, maximum 5 improvements.
- Sort improvements by priority ascending (1 first).
- If a metric is within its target range, treat it as a strength.
- Improvements must reference the speaker's actual numbers.
- timestamp_hint is null unless the data clearly suggests a specific window.\
"""


def build_user_prompt(metrics: dict) -> str:
    """Format metrics into a structured prompt section for the coaching model."""

    wpm = metrics.get("wpm_avg") or 0.0
    filler_count = metrics.get("filler_count") or 0
    filler_rate = metrics.get("filler_rate_per_min") or 0.0
    filler_words = metrics.get("filler_words_found") or []
    eye_pct = (metrics.get("eye_contact_pct") or 0.0) * 100
    pitch = metrics.get("pitch_variance") or 0.0
    sway = metrics.get("posture_sway") or 0.0
    volume_cv = metrics.get("volume_consistency") or 0.0
    pauses = metrics.get("pause_count") or 0
    hand_v = metrics.get("hand_velocity") or 0.0
    shoulder = metrics.get("shoulder_raise") or 0.0
    overall = metrics.get("overall_score") or 0.0
    transcript = (metrics.get("transcript") or "").strip()
    wpm_windows = metrics.get("wpm_windows") or []

    def _status(val, lo=None, hi=None, invert=False):
        """Return a short on-target / deviation label."""
        if lo is not None and val < lo:
            return f"below target — {lo - val:.1f} under minimum"
        if hi is not None and val > hi:
            return f"above target — {val - hi:.1f} over maximum"
        if invert:
            return "within target"
        return "within target ✓"

    wpm_note = _status(wpm, _WPM_LOW, _WPM_HIGH)
    filler_note = _status(filler_rate, hi=_FILLER_RATE_MAX)
    eye_note = _status(eye_pct, lo=_EYE_CONTACT_MIN * 100)
    pitch_note = _status(pitch, lo=_PITCH_MIN)
    sway_note = _status(sway, hi=_SWAY_MAX)
    shoulder_note = _status(shoulder, hi=_SHOULDER_MAX)

    filler_detail = (
        f"{', '.join(filler_words)}" if filler_words else "none detected"
    )

    wpm_window_str = ""
    if wpm_windows:
        window_lines = [
            f"  window {i + 1} (0:{i * 30:02d}–0:{(i + 1) * 30:02d}): {w:.0f} WPM"
            for i, w in enumerate(wpm_windows)
        ]
        wpm_window_str = "\n" + "\n".join(window_lines)

    lines = [
        "PRESENTATION METRICS",
        "====================",
        f"Overall score: {overall:.0f}/100",
        "",
        "SPEECH METRICS",
        f"  WPM (avg):         {wpm:.0f}  [target: {_WPM_LOW}–{_WPM_HIGH}]  → {wpm_note}",
    ]
    if wpm_window_str:
        lines.append(f"  WPM by window:    {wpm_window_str}")
    lines += [
        f"  Filler words:      {filler_count} total, {filler_rate:.1f}/min  "
        f"[target: <{_FILLER_RATE_MAX}/min]  → {filler_note}",
        f"  Filler types:      {filler_detail}",
        f"  Pitch variance:    {pitch:.1f} Hz std-dev  "
        f"[target: >{_PITCH_MIN} Hz; low = monotone]  → {pitch_note}",
        f"  Volume consistency:{volume_cv:.4f} RMS std-dev  [lower = more consistent]",
        f"  Pause count:       {pauses} pauses >0.5 s",
        "",
        "BODY LANGUAGE METRICS",
        f"  Eye contact:       {eye_pct:.0f}%  "
        f"[target: >{_EYE_CONTACT_MIN * 100:.0f}%]  → {eye_note}",
        f"  Posture sway:      {sway:.1f} px/frame  "
        f"[target: <{_SWAY_MAX}]  → {sway_note}",
        f"  Hand velocity:     {hand_v:.1f} px/s",
        f"  Shoulder tension:  {shoulder:.2f}  "
        f"[target: <{_SHOULDER_MAX}; high = raised/tense]  → {shoulder_note}",
        "",
        "TRANSCRIPT",
        "----------",
        transcript or "(no transcript available)",
        "",
        "Please provide your coaching feedback as JSON.",
    ]

    return "\n".join(lines)
