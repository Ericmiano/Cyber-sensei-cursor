"""Sources & Ingestion domain models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
import enum

from app.core.database import Base


class SourceType(str, enum.Enum):
    """Types of content sources."""
    PDF = "pdf"
    URL = "url"
    VIDEO = "video"
    BOOK = "book"
    PAPER = "paper"
    COURSE = "course"
    MANUAL = "manual"


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Source(Base):
    """Source metadata with reliability scoring."""
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    author = Column(String(255))
    publisher = Column(String(255))
    source_type = Column(Enum(SourceType), nullable=False)
    url = Column(String(2048), unique=True, index=True)
    domain = Column(String(255), index=True)  # For domain authority calculation
    domain_authority = Column(Float, default=0.0)  # 0.0-1.0
    age_bonus = Column(Float, default=0.0)  # 0.0-1.0 (newer = higher)
    peer_reviewed = Column(Boolean, default=False)
    reliability_score = Column(Float, default=0.0, index=True)  # Calculated: (domain_authority + age_bonus + peer_review) / 5
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")


class Document(Base):
    """Document storage and metadata."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    file_path = Column(String(1024))  # Local storage path
    file_size = Column(Integer)  # Bytes
    mime_type = Column(String(100))
    page_count = Column(Integer)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False, index=True)
    processing_error = Column(Text)
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("Source", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    """Text chunks with embeddings and citations."""
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document
    start_char = Column(Integer)  # Character offset in original document
    end_char = Column(Integer)
    page_number = Column(Integer)
    embedding = Column(ARRAY(Float), nullable=True)  # 1536-dim vector (pgvector)
    citation = Column(JSON, default=dict)  # {"source_id": "...", "page": 1, "section": "..."}
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    # Note: Vector similarity search index will be created via migration
