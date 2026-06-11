"""Transcribe and analyse the audio track using Whisper and librosa."""

# TODO: Implement audio analysis
# Steps:
#   1. Extract audio from the video with ffmpeg (subprocess) or moviepy → temp WAV file
#   2. Load WAV with librosa; compute pitch (librosa.yin or pyin) and RMS energy
#   3. Run openai-whisper on the WAV to get a word-level transcript with timestamps
#   4. Count filler words ("um", "uh", "like", "you know", "basically", "literally")
#   5. Compute WPM: word_count / (audio_duration_seconds / 60)
#   6. Return a dict of aggregated audio metrics

import numpy as np
from typing import Any

FILLER_WORDS = {"um", "uh", "like", "you know", "basically", "literally", "so", "right"}


def analyse_audio(video_path: str) -> dict[str, Any]:
    """
    Extract and analyse the audio track from *video_path*.

    Returns dict with keys: wpm, filler_count, pitch_variance, transcript

    TODO: Use Whisper word timestamps to align fillers with video timeline for UI highlighting.
    TODO: Detect long pauses (silence > 2 s) as an additional metric.
    TODO: Consider streaming Whisper for large files instead of loading everything into RAM.
    """
    raise NotImplementedError("analyse_audio not yet implemented")
