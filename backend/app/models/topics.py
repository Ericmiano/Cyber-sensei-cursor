"""Topics & Knowledge domain models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class BloomLevel(int, enum.Enum):
    """Bloom's Taxonomy levels (1-6)."""
    REMEMBER = 1
    UNDERSTAND = 2
    APPLY = 3
    ANALYZE = 4
    EVALUATE = 5
    CREATE = 6


class ContentType(str, enum.Enum):
    """Types of generated content."""
    STUDY_GUIDE = "study_guide"
    LAB = "lab"
    QUIZ = "quiz"
    VIDEO_SCRIPT = "video_script"
    SUMMARY = "summary"
    PRACTICE_EXERCISE = "practice_exercise"


class Topic(Base):
    """Learning domain/topic."""
    __tablename__ = "topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_topic = relationship("Topic", remote_side=[id], backref="subtopics")
    concepts = relationship("Concept", back_populates="topic", cascade="all, delete-orphan")
    content_items = relationship("ContentItem", back_populates="topic", cascade="all, delete-orphan")


class Concept(Base):
    """Atomic learning concept with Bloom level."""
    __tablename__ = "concepts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    bloom_level = Column(Integer, nullable=False, default=BloomLevel.REMEMBER)  # 1-6
    difficulty = Column(Float, default=0.5)  # 0.0-1.0
    estimated_time_minutes = Column(Integer, default=30)
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="concepts")
    prerequisites = relationship(
        "Concept",
        secondary="concept_edges",
        primaryjoin="Concept.id == ConceptEdge.prerequisite_id",
        secondaryjoin="Concept.id == ConceptEdge.concept_id",
        backref="dependents",
    )
    content_items = relationship("ContentItem", back_populates="concept", cascade="all, delete-orphan")
    mastery = relationship("UserConceptMastery", back_populates="concept", cascade="all, delete-orphan")


class ConceptEdge(Base):
    """Prerequisite relationships between concepts (DAG)."""
    __tablename__ = "concept_edges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    strength = Column(Float, default=1.0)  # 0.0-1.0, how critical this prerequisite is
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Prevent self-loops and duplicates
    __table_args__ = (
        CheckConstraint("concept_id != prerequisite_id", name="check_no_self_loop"),
        UniqueConstraint("concept_id", "prerequisite_id", name="uq_concept_prerequisite"),
    )


class ContentItem(Base):
    """AI-generated study materials, labs, quizzes."""
    __tablename__ = "content_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True, index=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=True, index=True)
    content_type = Column(Enum(ContentType), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Markdown or structured JSON
    bloom_level = Column(Integer, nullable=False, default=BloomLevel.REMEMBER)
    difficulty = Column(Float, default=0.5)
    citations = Column(JSON, default=list)  # List of chunk IDs or source references
    meta_data = Column("metadata", JSON, default=dict)  # Lab config, quiz questions, etc.
    is_published = Column(Boolean, default=False, nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="content_items")
    concept = relationship("Concept", back_populates="content_items")
    parent_version = relationship("ContentItem", remote_side=[id], backref="revisions")
