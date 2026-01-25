"""Users & Authentication domain models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class Role(str, enum.Enum):
    """User roles for RBAC."""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    MODERATOR = "moderator"


class LearningStyle(str, enum.Enum):
    """Learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MULTIMODAL = "multimodal"


class User(Base):
    """User account with RBAC."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.STUDENT)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    mastery = relationship("UserConceptMastery", back_populates="user", cascade="all, delete-orphan")
    learning_events = relationship("LearningEvent", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """Extended user profile with learning preferences."""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    learning_style = Column(Enum(LearningStyle), default=LearningStyle.MULTIMODAL)
    preferred_difficulty = Column(String(50), default="adaptive")  # beginner, intermediate, advanced, adaptive
    accessibility_needs = Column(JSON, default=dict)  # e.g., {"screen_reader": true, "high_contrast": false}
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class Session(Base):
    """JWT session management with rotation support."""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(String(512), unique=True, nullable=False, index=True)
    access_token_jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID for revocation
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(512))
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class UserGoal(Base):
    """User learning goals with timeframes."""
    __tablename__ = "user_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_proficiency = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, expert
    target_date = Column(DateTime)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")
