"""Transcribe and analyse the audio track using Whisper and librosa."""

import os
import re
import subprocess
import tempfile
from typing import Any

import librosa
import numpy as np
import whisper

# Ordered so multi-word phrases are checked before their component words
FILLER_WORDS: list[str] = [
    "you know",
    "um",
    "uh",
    "like",
    "so",
    "basically",
    "literally",
]

_SAMPLE_RATE = 16_000         # Hz — Whisper's native rate
_WPM_WINDOW_SEC = 30          # window size for per-segment WPM
_PAUSE_THRESHOLD_SEC = 0.5    # minimum silence duration to count as a pause
_SILENCE_TOP_DB = 35          # librosa threshold for silence detection


def _extract_wav(video_path: str, wav_path: str) -> None:
    """Extract mono 16-kHz WAV from *video_path* into *wav_path* via ffmpeg."""
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", str(_SAMPLE_RATE),
            "-ac", "1",
            wav_path,
        ],
        check=True,
        capture_output=True,
    )


def _count_fillers(text: str) -> tuple[int, list[str]]:
    """Return (total_count, list_of_matched_filler_strings) in *text*."""
    lower = text.lower()
    found: list[str] = []
    for filler in FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        matches = re.findall(pattern, lower)
        found.extend(matches)
    return len(found), sorted(set(found))


def _wpm_windows(segments: list[dict], audio_duration: float) -> tuple[float, list[float]]:
    """Compute per-30-second WPM windows and their average from Whisper segments."""
    # Collect all words with timestamps
    all_words: list[dict] = []
    for seg in segments:
        all_words.extend(seg.get("words", []))

    if not all_words or audio_duration <= 0:
        return 0.0, []

    # Group by 30-second bucket
    bucket_words: dict[int, list[dict]] = {}
    for w in all_words:
        bucket = int(w["start"] // _WPM_WINDOW_SEC)
        bucket_words.setdefault(bucket, []).append(w)

    wpm_list: list[float] = []
    for bucket in sorted(bucket_words):
        bucket_start = bucket * _WPM_WINDOW_SEC
        bucket_end = min(bucket_start + _WPM_WINDOW_SEC, audio_duration)
        duration_min = (bucket_end - bucket_start) / 60.0
        if duration_min > 0:
            wpm_list.append(len(bucket_words[bucket]) / duration_min)

    wpm_avg = float(np.mean(wpm_list)) if wpm_list else 0.0
    return wpm_avg, wpm_list


def _librosa_metrics(wav_path: str) -> dict[str, Any]:
    """Compute pitch_variance, volume_consistency, and pause_count via librosa."""
    y, sr = librosa.load(wav_path, sr=_SAMPLE_RATE, mono=True)

    # Fundamental frequency via pYIN (voiced frames only)
    f0, voiced_flag, _ = librosa.pyin(
        y,
        sr=sr,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
    )
    voiced_f0 = f0[voiced_flag] if voiced_flag is not None else np.array([])
    pitch_variance = float(np.std(voiced_f0)) if len(voiced_f0) > 0 else 0.0

    # RMS energy standard deviation
    rms = librosa.feature.rms(y=y)[0]
    volume_consistency = float(np.std(rms))

    # Count silent gaps longer than the threshold
    intervals = librosa.effects.split(y, top_db=_SILENCE_TOP_DB)
    pause_count = 0
    for i in range(1, len(intervals)):
        gap_sec = (intervals[i][0] - intervals[i - 1][1]) / sr
        if gap_sec > _PAUSE_THRESHOLD_SEC:
            pause_count += 1

    return {
        "pitch_variance": pitch_variance,
        "volume_consistency": volume_consistency,
        "pause_count": pause_count,
    }


def analyse_audio(video_path: str) -> dict[str, Any]:
    """
    Extract and analyse the audio track from *video_path*.

    Returns dict with keys:
        wpm_avg, wpm_windows, filler_count, filler_rate_per_min,
        filler_words_found, pitch_variance, volume_consistency,
        pause_count, transcript
    """
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_path = tmp_wav.name
    tmp_wav.close()

    try:
        _extract_wav(video_path, wav_path)

        model = whisper.load_model("base")
        result = model.transcribe(wav_path, word_timestamps=True, language=None)

        transcript: str = result.get("text", "").strip()
        segments: list[dict] = result.get("segments", [])

        # Audio duration from the last segment end (or librosa as fallback)
        audio_duration = 0.0
        if segments:
            audio_duration = float(segments[-1].get("end", 0.0))
        if audio_duration <= 0:
            y_dur, sr_dur = librosa.load(wav_path, sr=None, mono=True)
            audio_duration = len(y_dur) / sr_dur

        wpm_avg, wpm_windows = _wpm_windows(segments, audio_duration)

        filler_count, filler_words_found = _count_fillers(transcript)
        duration_min = audio_duration / 60.0
        filler_rate_per_min = filler_count / duration_min if duration_min > 0 else 0.0

        librosa_metrics = _librosa_metrics(wav_path)

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

    return {
        "wpm_avg": wpm_avg,
        "wpm_windows": wpm_windows,
        "filler_count": filler_count,
        "filler_rate_per_min": filler_rate_per_min,
        "filler_words_found": filler_words_found,
        "transcript": transcript,
        **librosa_metrics,
    }
