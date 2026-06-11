"""SQLAlchemy ORM models for PodiumAI."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Session(Base):
    """Represents a single video upload / coaching session."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    overall_score = Column(Float, nullable=True)

    metrics = relationship("Metrics", back_populates="session", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "created_at": self.created_at.isoformat(),
            "overall_score": self.overall_score,
        }


class Metrics(Base):
    """Fine-grained speech and body-language metrics for a session."""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    # Audio metrics
    wpm = Column(Float, nullable=True)            # words per minute
    filler_count = Column(Integer, nullable=True) # count of "um", "uh", "like", etc.
    pitch_variance = Column(Float, nullable=True) # std-dev of fundamental frequency (Hz)

    # Visual / pose metrics
    posture_sway = Column(Float, nullable=True)   # mean lateral shoulder displacement (px)
    hand_velocity = Column(Float, nullable=True)  # mean wrist velocity across frames (px/s)
    eye_contact_pct = Column(Float, nullable=True) # % of frames where gaze faces camera

    session = relationship("Session", back_populates="metrics")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "wpm": self.wpm,
            "filler_count": self.filler_count,
            "pitch_variance": self.pitch_variance,
            "posture_sway": self.posture_sway,
            "hand_velocity": self.hand_velocity,
            "eye_contact_pct": self.eye_contact_pct,
        }
