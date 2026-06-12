"""POST /api/upload — receives a video file, runs the analysis pipeline, and persists results."""

import json
import os
import uuid

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from database import SessionLocal
from models import Session, Metrics
from pipeline.extract_frames import extract_frames
from pipeline.pose_analysis import analyse_pose
from pipeline.audio_analysis import analyse_audio
from pipeline.get_metrics import _compute_score

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"mp4", "mov", "webm"}
MAX_BYTES = 500 * 1024 * 1024  # 500 MB


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@upload_bp.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files["video"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not _allowed(file.filename):
        return jsonify({"error": "Unsupported file type. Allowed: mp4, mov, webm"}), 415

    # Reject oversized uploads before writing to disk when Content-Length is present
    content_length = request.content_length
    if content_length and content_length > MAX_BYTES:
        return jsonify({"error": "File too large. Maximum 500 MB"}), 413

    ext = file.filename.rsplit(".", 1)[1].lower()
    uuid_filename = f"{uuid.uuid4()}.{ext}"

    # Resolve save_path before entering the generator so current_app is available
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], uuid_filename)

    file.save(save_path)

    # Second size guard for clients that omit Content-Length
    if os.path.getsize(save_path) > MAX_BYTES:
        os.remove(save_path)
        return jsonify({"error": "File too large. Maximum 500 MB"}), 413

    def generate():
        try:
            yield _sse({"stage": "Extracting frames..."})
            frames, orig_fps, total_frames = extract_frames(save_path)
            duration_seconds = total_frames / orig_fps if orig_fps > 0 else 0.0

            yield _sse({"stage": "Analysing pose..."})
            visual = analyse_pose(frames, orig_fps)

            yield _sse({"stage": "Transcribing audio..."})
            audio = analyse_audio(save_path)

            overall_score = _compute_score({**visual, **audio})

            db = SessionLocal()
            try:
                session_row = Session(
                    filename=uuid_filename,
                    overall_score=overall_score,
                    duration_seconds=duration_seconds,
                )
                db.add(session_row)
                db.flush()

                metrics_row = Metrics(
                    session_id=session_row.id,
                    wpm_avg=audio["wpm_avg"],
                    wpm_windows=json.dumps(audio["wpm_windows"]),
                    filler_count=audio["filler_count"],
                    filler_rate_per_min=audio["filler_rate_per_min"],
                    filler_words_found=json.dumps(audio["filler_words_found"]),
                    pitch_variance=audio["pitch_variance"],
                    volume_consistency=audio["volume_consistency"],
                    pause_count=audio["pause_count"],
                    transcript=audio["transcript"],
                    posture_sway=visual["posture_sway"],
                    hand_velocity=visual["hand_velocity"],
                    eye_contact_pct=visual["eye_contact_pct"],
                    shoulder_raise=visual["shoulder_raise"],
                )
                db.add(metrics_row)
                db.commit()
                session_id = session_row.id
                metrics_dict = metrics_row.to_dict()
            finally:
                db.close()

            yield _sse({
                "done": True,
                "session_id": session_id,
                "overall_score": overall_score,
                "metrics": metrics_dict,
                "transcript": audio["transcript"],
            })

        except Exception as exc:
            yield _sse({"error": str(exc)})

    return Response(stream_with_context(generate()), mimetype="text/event-stream")
