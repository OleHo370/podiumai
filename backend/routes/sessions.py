"""GET /api/sessions — list all coaching sessions and retrieve individual session details."""

from flask import Blueprint, jsonify
from database import SessionLocal
from models import Session, Metrics

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions", methods=["GET"])
def list_sessions():
    """
    Return all sessions ordered by most recent first.

    TODO: Add pagination (page/limit query params).
    TODO: Filter by date range.
    """
    db = SessionLocal()
    try:
        sessions = db.query(Session).order_by(Session.created_at.desc()).all()
        return jsonify([s.to_dict() for s in sessions])
    finally:
        db.close()


@sessions_bp.route("/sessions/<int:session_id>", methods=["GET"])
def get_session(session_id: int):
    """
    Return a single session with its associated metrics.

    TODO: Include the AI feedback JSON once coach.py is integrated into the upload pipeline.
    """
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if session is None:
            return jsonify({"error": "Session not found"}), 404

        metrics = db.query(Metrics).filter(Metrics.session_id == session_id).first()
        return jsonify({
            **session.to_dict(),
            "metrics": metrics.to_dict() if metrics else None,
        })
    finally:
        db.close()
