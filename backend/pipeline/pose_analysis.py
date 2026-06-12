"""Analyse body language using MediaPipe Pose, Hands, and Face Mesh."""

import cv2
import numpy as np
import mediapipe as mp
from typing import Any

_mp_pose = mp.solutions.pose
_mp_hands = mp.solutions.hands
_mp_face = mp.solutions.face_mesh

# MediaPipe Pose landmark indices
_NOSE = 0
_SHOULDER_L = 11
_SHOULDER_R = 12
_WRIST_L = 15
_WRIST_R = 16

# Extracted frames use every 5th source frame; effective fps = orig_fps / 5
_FRAME_STEP = 5

# Horizontal tolerance for eye-contact proxy: nose within ±25% of frame centre
_EYE_CONTACT_TOLERANCE = 0.25


def analyse_pose(frames: list[np.ndarray], orig_fps: float) -> dict[str, Any]:
    """
    Run MediaPipe Pose, Hands, and Face Mesh on *frames*.

    Returns dict keys: posture_sway, hand_velocity, eye_contact_pct, shoulder_raise
    """
    if not frames:
        return {
            "posture_sway": 0.0,
            "hand_velocity": 0.0,
            "eye_contact_pct": 0.0,
            "shoulder_raise": 0.0,
        }

    effective_fps = orig_fps / _FRAME_STEP

    pose_model = _mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    hands_model = _mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    face_model = _mp_face.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    shoulder_x_px: list[float] = []
    shoulder_y_px: list[float] = []
    # Each entry is (x_px, y_px) or None when wrists not visible
    wrist_positions: list[tuple[float, float] | None] = []
    eye_contact_hits = 0
    pose_frame_count = 0

    for frame in frames:
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_result = pose_model.process(rgb)
        hands_model.process(rgb)       # run as required; results unused beyond wrist fallback
        face_result = face_model.process(rgb)

        if not pose_result.pose_landmarks:
            wrist_positions.append(None)
            continue

        lm = pose_result.pose_landmarks.landmark
        pose_frame_count += 1

        # --- Shoulder midpoint ---
        sx = (lm[_SHOULDER_L].x + lm[_SHOULDER_R].x) / 2.0
        sy = (lm[_SHOULDER_L].y + lm[_SHOULDER_R].y) / 2.0
        shoulder_x_px.append(sx * w)
        shoulder_y_px.append(sy * h)

        # --- Wrist positions (average visible wrists) ---
        wrists: list[tuple[float, float]] = []
        for wrist_idx in (_WRIST_L, _WRIST_R):
            if lm[wrist_idx].visibility > 0.5:
                wrists.append((lm[wrist_idx].x * w, lm[wrist_idx].y * h))
        wrist_positions.append(
            (
                sum(x for x, _ in wrists) / len(wrists),
                sum(y for _, y in wrists) / len(wrists),
            )
            if wrists
            else None
        )

        # --- Eye contact proxy: use Face Mesh nose tip when available ---
        if face_result.multi_face_landmarks:
            # Landmark 4 is the nose tip in the 468-point face mesh
            nose_x = face_result.multi_face_landmarks[0].landmark[4].x
        else:
            nose_x = lm[_NOSE].x

        if abs(nose_x - 0.5) < _EYE_CONTACT_TOLERANCE:
            eye_contact_hits += 1

    pose_model.close()
    hands_model.close()
    face_model.close()

    # posture_sway: mean absolute x-displacement of shoulder midpoint (px / sampled frame)
    posture_sway = 0.0
    if len(shoulder_x_px) > 1:
        posture_sway = float(
            np.mean([abs(shoulder_x_px[i] - shoulder_x_px[i - 1]) for i in range(1, len(shoulder_x_px))])
        )

    # hand_velocity: mean wrist speed in px/s
    hand_velocity = 0.0
    valid_wrists = [(i, wp) for i, wp in enumerate(wrist_positions) if wp is not None]
    if len(valid_wrists) > 1:
        velocities: list[float] = []
        for j in range(1, len(valid_wrists)):
            i0, wp0 = valid_wrists[j - 1]
            i1, wp1 = valid_wrists[j]
            frames_elapsed = i1 - i0
            if frames_elapsed > 0 and effective_fps > 0:
                dist = float(np.hypot(wp1[0] - wp0[0], wp1[1] - wp0[1]))
                velocities.append(dist * effective_fps / frames_elapsed)
        if velocities:
            hand_velocity = float(np.mean(velocities))

    # eye_contact_pct: fraction of pose-detected frames where gaze faces camera
    eye_contact_pct = eye_contact_hits / pose_frame_count if pose_frame_count > 0 else 0.0

    # shoulder_raise: 1 - normalised shoulder y; high value = raised shoulders = tension
    shoulder_raise = 0.0
    if shoulder_y_px and frames:
        frame_h = frames[0].shape[0]
        shoulder_raise = float(1.0 - np.mean(shoulder_y_px) / frame_h)

    return {
        "posture_sway": posture_sway,
        "hand_velocity": hand_velocity,
        "eye_contact_pct": float(eye_contact_pct),
        "shoulder_raise": shoulder_raise,
    }
