"""Analyse body language using MediaPipe Pose, Hands, and Face Mesh."""

# TODO: Implement pose analysis
# Steps:
#   1. Initialise mediapipe.solutions.pose, .hands, and .face_mesh
#   2. For each frame, run all three models and collect landmark arrays
#   3. Compute per-frame metrics:
#      - Shoulder midpoint X position  → posture_sway (std-dev across frames)
#      - Wrist landmark velocity       → hand_velocity (mean px/s)
#      - Nose / iris landmarks vs camera centre → eye_contact_pct
#   4. Return a dict of aggregated metrics

import numpy as np
from typing import Any


def analyse_pose(frames: list[np.ndarray], orig_fps: float) -> dict[str, Any]:
    """
    Run MediaPipe models on *frames* and return aggregated visual metrics.

    Returns dict with keys: posture_sway, hand_velocity, eye_contact_pct

    TODO: Calibrate eye-contact heuristic with real recorded data.
    TODO: Normalise coordinates by frame resolution so metrics are resolution-independent.
    TODO: Export per-frame landmark timeseries for the frontend visualisation.
    """
    raise NotImplementedError("analyse_pose not yet implemented")
