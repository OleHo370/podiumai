"""SQLAlchemy ORM models for PodiumAI."""

import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    overall_score = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # cascade ensures Metrics row is deleted when Session is deleted
    metrics = relationship(
        "Metrics",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "created_at": self.created_at.isoformat(),
            "overall_score": self.overall_score,
            "duration_seconds": self.duration_seconds,
        }


class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    # Audio metrics
    wpm_avg = Column(Float, nullable=True)
    wpm_windows = Column(String, nullable=True)       # JSON list of per-window WPM floats
    filler_count = Column(Integer, nullable=True)
    filler_rate_per_min = Column(Float, nullable=True)
    filler_words_found = Column(String, nullable=True) # JSON list of matched filler strings
    pitch_variance = Column(Float, nullable=True)
    volume_consistency = Column(Float, nullable=True)
    pause_count = Column(Integer, nullable=True)
    transcript = Column(String, nullable=True)

    # Visual / pose metrics
    posture_sway = Column(Float, nullable=True)
    hand_velocity = Column(Float, nullable=True)
    eye_contact_pct = Column(Float, nullable=True)
    shoulder_raise = Column(Float, nullable=True)

    session = relationship("Session", back_populates="metrics")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "wpm_avg": self.wpm_avg,
            "wpm_windows": json.loads(self.wpm_windows) if self.wpm_windows else [],
            "filler_count": self.filler_count,
            "filler_rate_per_min": self.filler_rate_per_min,
            "filler_words_found": json.loads(self.filler_words_found) if self.filler_words_found else [],
            "pitch_variance": self.pitch_variance,
            "volume_consistency": self.volume_consistency,
            "pause_count": self.pause_count,
            "transcript": self.transcript,
            "posture_sway": self.posture_sway,
            "hand_velocity": self.hand_velocity,
            "eye_contact_pct": self.eye_contact_pct,
            "shoulder_raise": self.shoulder_raise,
        }
