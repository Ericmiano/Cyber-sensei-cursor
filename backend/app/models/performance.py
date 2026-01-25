"""Performance & Feedback domain models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class LabStatus(str, enum.Enum):
    """Lab session status."""
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    TERMINATED = "terminated"


class TeachingFeedback(Base):
    """AI teaching efficacy feedback and shortcomings."""
    __tablename__ = "teaching_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=True, index=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=True, index=True)
    efficacy_score = Column(Float)  # E = (ΔMastery / Time) × UserSatisfaction
    mastery_delta = Column(Float)  # Change in mastery probability
    time_spent_seconds = Column(Integer)
    user_satisfaction = Column(Float)  # 0.0-1.0 (user rating)
    shortcomings = Column(JSON, default=list)  # List of identified issues
    suggested_improvements = Column(Text)
    is_addressed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    content_item = relationship("ContentItem")


class LabSession(Base):
    """Containerized lab environment lifecycle management."""
    __tablename__ = "lab_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, index=True)
    docker_container_id = Column(String(255), unique=True, index=True)
    docker_image = Column(String(255), nullable=False)
    status = Column(Enum(LabStatus), default=LabStatus.PENDING, nullable=False, index=True)
    port_mappings = Column(JSON, default=dict)  # {"80": "8080", "443": "8443"}
    environment_variables = Column(JSON, default=dict)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    timeout_at = Column(DateTime)
    error_message = Column(Text)
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    content_item = relationship("ContentItem")


class GradingRubric(Base):
    """Automated grading criteria for practical labs."""
    __tablename__ = "grading_rubrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    criteria = Column(JSON, nullable=False)  # [
    #   {
    #     "type": "file_exists",
    #     "path": "/app/script.sh",
    #     "weight": 0.3,
    #     "description": "Script file must exist"
    #   },
    #   {
    #     "type": "port_listening",
    #     "port": 8080,
    #     "weight": 0.4,
    #     "description": "Web server must be running"
    #   },
    #   {
    #     "type": "command_output",
    #     "command": "curl http://localhost:8080",
    #     "expected": "Hello World",
    #     "weight": 0.3,
    #     "description": "Server must return correct response"
    #   }
    # ]
    total_weight = Column(Float, default=1.0, nullable=False)
    passing_threshold = Column(Float, default=0.7, nullable=False)  # 0.0-1.0
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem")
