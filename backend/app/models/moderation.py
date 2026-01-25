"""Moderation & Safety domain models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class ReviewStatus(str, enum.Enum):
    """Content review status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    REVISED = "revised"


class FlagSeverity(str, enum.Enum):
    """Severity levels for flagged content."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentReview(Base):
    """Human-in-the-loop content moderation."""
    __tablename__ = "content_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False, index=True)
    accuracy_score = Column(Float)  # 0.0-1.0
    appropriateness_score = Column(Float)  # 0.0-1.0
    notes = Column(Text)
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = relationship("User")


class FlaggedItem(Base):
    """Items flagged for review or removal."""
    __tablename__ = "flagged_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=True, index=True)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=True, index=True)
    flagged_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    severity = Column(Enum(FlagSeverity), default=FlagSeverity.MEDIUM, nullable=False, index=True)
    reason = Column(Text, nullable=False)
    auto_flagged = Column(Boolean, default=False, nullable=False)  # True if flagged by AI
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    flagged_by = relationship("User", foreign_keys=[flagged_by_user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])


class AuditLog(Base):
    """Immutable audit trail for security and compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "content_created", "user_deleted"
    resource_type = Column(String(50), nullable=False)  # e.g., "content_item", "user"
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User")


class Misconception(Base):
    """Common errors and misconceptions detected in learning."""
    __tablename__ = "misconceptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    correction = Column(Text, nullable=False)
    frequency = Column(Integer, default=0, nullable=False)  # How often this misconception appears
    detected_from = Column(JSON, default=list)  # List of quiz attempts or user feedback
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    concept = relationship("Concept")
