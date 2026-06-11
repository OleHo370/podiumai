"""Combine outputs from pose_analysis and audio_analysis into a single metrics dict."""

# TODO: Implement metrics aggregation
# Steps:
#   1. Call extract_frames(video_path) → frames, orig_fps
#   2. Call analyse_pose(frames, orig_fps) → visual_metrics
#   3. Call analyse_audio(video_path)    → audio_metrics
#   4. Merge both dicts and add derived/normalised fields
#   5. Return the combined dict (will be persisted to Metrics model + sent to coach.py)

from typing import Any


def build_metrics(video_path: str) -> dict[str, Any]:
    """
    Orchestrate the full analysis pipeline for *video_path*.

    Returns a flat dict matching the Metrics model fields:
        wpm, filler_count, pitch_variance,
        posture_sway, hand_velocity, eye_contact_pct

    TODO: Add overall_score calculation (weighted average of normalised sub-scores).
    TODO: Cache intermediate results (frames, audio WAV) to avoid re-computation on retry.
    """
    raise NotImplementedError("build_metrics not yet implemented")
