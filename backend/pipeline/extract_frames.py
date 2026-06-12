"""Extract frames from a video file using OpenCV."""

import cv2
import numpy as np
from typing import Tuple


def extract_frames(
    video_path: str,
    frame_step: int = 5,
) -> Tuple[list[np.ndarray], float, int]:
    """
    Sample every *frame_step*-th frame from *video_path*.

    Returns:
        frames           - list of BGR numpy arrays
        orig_fps         - original video frame rate
        total_frames     - total frame count in the video
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    orig_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames: list[np.ndarray] = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_step == 0:
            frames.append(frame)
        idx += 1

    cap.release()
    return frames, orig_fps, total_frames
