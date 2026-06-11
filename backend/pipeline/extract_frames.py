"""Extract frames from a video file using OpenCV."""

# TODO: Implement frame extraction
# Steps:
#   1. Open the video with cv2.VideoCapture(video_path)
#   2. Sample every Nth frame (configurable FPS target, e.g. 5 fps)
#   3. Resize frames to a consistent resolution (e.g. 720p) for downstream models
#   4. Return a list of numpy arrays (BGR frames) and the original video FPS

import cv2
import numpy as np
from typing import Tuple


def extract_frames(
    video_path: str,
    target_fps: float = 5.0,
) -> Tuple[list[np.ndarray], float]:
    """
    Sample frames from *video_path* at *target_fps*.

    Returns:
        frames   - list of BGR numpy arrays
        orig_fps - original video frame rate (needed by pose analysis for timing)

    TODO: Add progress callback for long videos.
    TODO: Handle corrupt/truncated video files gracefully.
    """
    raise NotImplementedError("extract_frames not yet implemented")
