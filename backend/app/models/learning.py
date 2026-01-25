"""Learning State domain models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class EventType(str, enum.Enum):
    """Types of learning events."""
    LESSON_STARTED = "lesson_started"
    LESSON_COMPLETED = "lesson_completed"
    QUIZ_ATTEMPTED = "quiz_attempted"
    QUIZ_COMPLETED = "quiz_completed"
    LAB_STARTED = "lab_started"
    LAB_COMPLETED = "lab_completed"
    CONCEPT_REVIEWED = "concept_reviewed"
    FEEDBACK_SUBMITTED = "feedback_submitted"


class UserProgress(Base):
    """User progress tracking for content items."""
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, index=True)
    progress_percentage = Column(Float, default=0.0, nullable=False)  # 0.0-100.0
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False, index=True)
    completed_at = Column(DateTime)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    
    # Unique constraint: one progress record per user-content pair
    __table_args__ = (
        UniqueConstraint("user_id", "content_item_id", name="uq_user_progress"),
    )


class UserConceptMastery(Base):
    """Bayesian Knowledge Tracing (BKT) mastery estimates."""
    __tablename__ = "user_concept_mastery"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    mastery_probability = Column(Float, default=0.3, nullable=False)  # 0.0-1.0 (BKT estimate)
    learn_rate = Column(Float, default=0.1)  # BKT parameter
    guess_rate = Column(Float, default=0.2)  # BKT parameter
    slip_rate = Column(Float, default=0.1)  # BKT parameter
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    last_updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="mastery")
    concept = relationship("Concept", back_populates="mastery")
    
    # Unique constraint: one mastery record per user-concept pair
    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_user_concept_mastery"),
    )


class SpacedRepetitionSchedule(Base):
    """SM-2 algorithm spaced repetition scheduling."""
    __tablename__ = "spaced_repetition_schedule"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    easiness_factor = Column(Float, default=2.5, nullable=False)  # SM-2 parameter
    interval_days = Column(Integer, default=1, nullable=False)  # Days until next review
    repetitions = Column(Integer, default=0, nullable=False)  # Number of successful reviews
    next_review_date = Column(DateTime, nullable=False, index=True)
    last_reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    concept = relationship("Concept")
    
    # Unique constraint: one schedule per user-concept pair
    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_spaced_rep_schedule"),
    )


class LearningEvent(Base):
    """Immutable audit trail of learning activities."""
    __tablename__ = "learning_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="SET NULL"), nullable=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    meta_data = Column("metadata", JSON, default=dict)  # Additional event data
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="learning_events")
