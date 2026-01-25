"""Database models for all domains."""
from app.models.users import User, UserProfile, Session, UserGoal
from app.models.sources import Source, Document, Chunk
from app.models.topics import Topic, Concept, ConceptEdge, ContentItem
from app.models.learning import (
    UserProgress,
    UserConceptMastery,
    SpacedRepetitionSchedule,
    LearningEvent,
)
from app.models.moderation import (
    ContentReview,
    FlaggedItem,
    AuditLog,
    Misconception,
)
from app.models.performance import (
    TeachingFeedback,
    LabSession,
    GradingRubric,
)

__all__ = [
    # Users & Auth
    "User",
    "UserProfile",
    "Session",
    "UserGoal",
    # Sources & Ingestion
    "Source",
    "Document",
    "Chunk",
    # Topics & Knowledge
    "Topic",
    "Concept",
    "ConceptEdge",
    "ContentItem",
    # Learning State
    "UserProgress",
    "UserConceptMastery",
    "SpacedRepetitionSchedule",
    "LearningEvent",
    # Moderation & Safety
    "ContentReview",
    "FlaggedItem",
    "AuditLog",
    "Misconception",
    # Performance & Feedback
    "TeachingFeedback",
    "LabSession",
    "GradingRubric",
]
