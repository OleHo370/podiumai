"""POST /api/upload — receives a video file, runs the analysis pipeline, and persists results."""

import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import SessionLocal
from models import Session, Metrics

# TODO: import pipeline steps once implemented
# from pipeline.extract_frames import extract_frames
# from pipeline.pose_analysis import analyse_pose
# from pipeline.audio_analysis import analyse_audio
# from pipeline.get_metrics import build_metrics
# from coach import get_feedback

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "webm", "mkv"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_video():
    """
    Accepts a multipart/form-data POST with a 'video' file field.

    TODO: Run extract_frames → pose_analysis + audio_analysis → build_metrics → get_feedback.
    TODO: Persist Session + Metrics rows and return the feedback JSON with the session id.
    TODO: Add background task queue (e.g. Celery / RQ) so large files don't block the request.
    """
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not _allowed(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"}), 415

    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    # --- Placeholder response until pipeline is wired up ---
    db = SessionLocal()
    try:
        session = Session(filename=filename, overall_score=None)
        db.add(session)
        db.commit()
        db.refresh(session)

        return jsonify({
            "session_id": session.id,
            "message": "File uploaded. Pipeline not yet implemented.",
        }), 202
    finally:
        db.close()
