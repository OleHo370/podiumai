"""Combine outputs from pose_analysis and audio_analysis into a single metrics dict."""

from typing import Any

from pipeline.audio_analysis import analyse_audio
from pipeline.extract_frames import extract_frames
from pipeline.pose_analysis import analyse_pose

# Scoring thresholds
_WPM_TARGET = 130
_WPM_LOW = 100
_WPM_HIGH = 160

_FILLER_RATE_FLOOR = 1.0        # fillers/min below which no penalty
_FILLER_PENALTY_PER_UNIT = 2.0  # score points lost per extra filler/min

# Pitch below this threshold is considered monotone (Hz std-dev)
_PITCH_VARIANCE_MIN = 15.0
_PITCH_MONOTONE_PENALTY = 10.0

# Posture sway above this threshold (px per sampled frame) is excessive
_SWAY_MAX = 5.0
_SWAY_PENALTY_SCALE = 1.5       # score points per px over threshold

# Shoulder raise above this (1 = fully raised) penalised
_SHOULDER_RAISE_MAX = 0.65
_SHOULDER_PENALTY = 8.0

# Eye contact below 60 % is penalised
_EYE_CONTACT_MIN = 0.6
_EYE_CONTACT_PENALTY_SCALE = 30.0


def _compute_score(metrics: dict[str, Any]) -> float:
    """Return an overall presentation score 0–100 based on metric deviations."""
    score = 100.0

    # WPM: penalise if outside [100, 160]
    wpm = metrics["wpm_avg"]
    if wpm < _WPM_LOW:
        score -= min(20.0, (_WPM_LOW - wpm) * 0.4)
    elif wpm > _WPM_HIGH:
        score -= min(20.0, (wpm - _WPM_HIGH) * 0.4)

    # Filler rate: -2 pts per filler/min above 1/min
    filler_rate = metrics["filler_rate_per_min"]
    if filler_rate > _FILLER_RATE_FLOOR:
        score -= min(20.0, (filler_rate - _FILLER_RATE_FLOOR) * _FILLER_PENALTY_PER_UNIT)

    # Pitch variance: penalise monotone delivery
    if metrics["pitch_variance"] < _PITCH_VARIANCE_MIN:
        deficit = _PITCH_VARIANCE_MIN - metrics["pitch_variance"]
        score -= min(_PITCH_MONOTONE_PENALTY, deficit * 0.6)

    # Posture sway: penalise excessive movement
    if metrics["posture_sway"] > _SWAY_MAX:
        score -= min(15.0, (metrics["posture_sway"] - _SWAY_MAX) * _SWAY_PENALTY_SCALE)

    # Shoulder raise: penalise raised/tense shoulders
    if metrics["shoulder_raise"] > _SHOULDER_RAISE_MAX:
        score -= _SHOULDER_PENALTY

    # Eye contact: penalise if below 60 %
    if metrics["eye_contact_pct"] < _EYE_CONTACT_MIN:
        score -= min(20.0, (_EYE_CONTACT_MIN - metrics["eye_contact_pct"]) * _EYE_CONTACT_PENALTY_SCALE)

    return round(max(0.0, min(100.0, score)), 1)


def get_metrics(video_path: str) -> dict[str, Any]:
    """
    Run the full analysis pipeline for *video_path*.

    Returns a flat dict containing all metrics and an overall_score (0–100).
    """
    frames, orig_fps, _total = extract_frames(video_path)
    visual = analyse_pose(frames, orig_fps)
    audio = analyse_audio(video_path)

    metrics: dict[str, Any] = {
        # Audio metrics
        "wpm_avg": audio["wpm_avg"],
        "wpm_windows": audio["wpm_windows"],
        "filler_count": audio["filler_count"],
        "filler_rate_per_min": audio["filler_rate_per_min"],
        "filler_words_found": audio["filler_words_found"],
        "pitch_variance": audio["pitch_variance"],
        "volume_consistency": audio["volume_consistency"],
        "pause_count": audio["pause_count"],
        "transcript": audio["transcript"],
        # Visual / pose metrics
        "posture_sway": visual["posture_sway"],
        "hand_velocity": visual["hand_velocity"],
        "eye_contact_pct": visual["eye_contact_pct"],
        "shoulder_raise": visual["shoulder_raise"],
    }

    metrics["overall_score"] = _compute_score(metrics)
    return metrics
