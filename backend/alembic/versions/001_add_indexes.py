"""Add database indexes for performance

Revision ID: 001_add_indexes
Revises: 
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_indexes'
down_revision = 'd5849a3f4e80'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes for frequently queried columns
    
    # Users
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    
    # Sessions
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_refresh_token', 'sessions', ['refresh_token'], unique=True)
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])
    
    # Documents
    op.create_index('idx_documents_source_id', 'documents', ['source_id'])
    op.create_index('idx_documents_status', 'documents', ['status'])
    
    # Chunks
    op.create_index('idx_chunks_document_id', 'chunks', ['document_id'])
    op.create_index('idx_chunks_created_at', 'chunks', ['created_at'])
    
    # Topics
    op.create_index('idx_topics_name', 'topics', ['name'], unique=True)
    op.create_index('idx_topics_parent_topic_id', 'topics', ['parent_topic_id'])
    
    # Concepts
    op.create_index('idx_concepts_topic_id', 'concepts', ['topic_id'])
    op.create_index('idx_concepts_name', 'concepts', ['name'])
    op.create_index('idx_concepts_bloom_level', 'concepts', ['bloom_level'])
    
    # Concept Edges
    op.create_index('idx_concept_edges_concept_id', 'concept_edges', ['concept_id'])
    op.create_index('idx_concept_edges_prerequisite_id', 'concept_edges', ['prerequisite_id'])
    op.create_unique_constraint('uq_concept_edges', 'concept_edges', ['concept_id', 'prerequisite_id'])
    
    # Content Items
    op.create_index('idx_content_items_topic_id', 'content_items', ['topic_id'])
    op.create_index('idx_content_items_concept_id', 'content_items', ['concept_id'])
    op.create_index('idx_content_items_content_type', 'content_items', ['content_type'])
    op.create_index('idx_content_items_is_published', 'content_items', ['is_published'])
    
    # User Progress
    op.create_index('idx_user_progress_user_id', 'user_progress', ['user_id'])
    op.create_index('idx_user_progress_content_item_id', 'user_progress', ['content_item_id'])
    op.create_index('idx_user_progress_is_completed', 'user_progress', ['is_completed'])
    op.create_unique_constraint('uq_user_progress', 'user_progress', ['user_id', 'content_item_id'])
    
    # User Concept Mastery
    op.create_index('idx_user_concept_mastery_user_id', 'user_concept_mastery', ['user_id'])
    op.create_index('idx_user_concept_mastery_concept_id', 'user_concept_mastery', ['concept_id'])
    op.create_index('idx_user_concept_mastery_mastery_prob', 'user_concept_mastery', ['mastery_probability'])
    op.create_unique_constraint('uq_user_concept_mastery', 'user_concept_mastery', ['user_id', 'concept_id'])
    
    # Spaced Repetition Schedule
    op.create_index('idx_spaced_rep_user_id', 'spaced_repetition_schedule', ['user_id'])
    op.create_index('idx_spaced_rep_concept_id', 'spaced_repetition_schedule', ['concept_id'])
    op.create_index('idx_spaced_rep_next_review', 'spaced_repetition_schedule', ['next_review_date'])
    op.create_unique_constraint('uq_spaced_rep', 'spaced_repetition_schedule', ['user_id', 'concept_id'])
    
    # Learning Events
    op.create_index('idx_learning_events_user_id', 'learning_events', ['user_id'])
    op.create_index('idx_learning_events_event_type', 'learning_events', ['event_type'])
    op.create_index('idx_learning_events_created_at', 'learning_events', ['created_at'])
    
    # Lab Sessions
    op.create_index('idx_lab_sessions_user_id', 'lab_sessions', ['user_id'])
    op.create_index('idx_lab_sessions_status', 'lab_sessions', ['status'])
    op.create_index('idx_lab_sessions_container_id', 'lab_sessions', ['docker_container_id'], unique=True)


def downgrade() -> None:
    # Remove indexes in reverse order
    op.drop_index('idx_lab_sessions_container_id', 'lab_sessions')
    op.drop_index('idx_lab_sessions_status', 'lab_sessions')
    op.drop_index('idx_lab_sessions_user_id', 'lab_sessions')
    
    op.drop_index('idx_learning_events_created_at', 'learning_events')
    op.drop_index('idx_learning_events_event_type', 'learning_events')
    op.drop_index('idx_learning_events_user_id', 'learning_events')
    
    op.drop_constraint('uq_spaced_rep', 'spaced_repetition_schedule')
    op.drop_index('idx_spaced_rep_next_review', 'spaced_repetition_schedule')
    op.drop_index('idx_spaced_rep_concept_id', 'spaced_repetition_schedule')
    op.drop_index('idx_spaced_rep_user_id', 'spaced_repetition_schedule')
    
    op.drop_constraint('uq_user_concept_mastery', 'user_concept_mastery')
    op.drop_index('idx_user_concept_mastery_mastery_prob', 'user_concept_mastery')
    op.drop_index('idx_user_concept_mastery_concept_id', 'user_concept_mastery')
    op.drop_index('idx_user_concept_mastery_user_id', 'user_concept_mastery')
    
    op.drop_constraint('uq_user_progress', 'user_progress')
    op.drop_index('idx_user_progress_is_completed', 'user_progress')
    op.drop_index('idx_user_progress_content_item_id', 'user_progress')
    op.drop_index('idx_user_progress_user_id', 'user_progress')
    
    op.drop_index('idx_content_items_is_published', 'content_items')
    op.drop_index('idx_content_items_content_type', 'content_items')
    op.drop_index('idx_content_items_concept_id', 'content_items')
    op.drop_index('idx_content_items_topic_id', 'content_items')
    
    op.drop_constraint('uq_concept_edges', 'concept_edges')
    op.drop_index('idx_concept_edges_prerequisite_id', 'concept_edges')
    op.drop_index('idx_concept_edges_concept_id', 'concept_edges')
    
    op.drop_index('idx_concepts_bloom_level', 'concepts')
    op.drop_index('idx_concepts_name', 'concepts')
    op.drop_index('idx_concepts_topic_id', 'concepts')
    
    op.drop_index('idx_topics_parent_topic_id', 'topics')
    op.drop_index('idx_topics_name', 'topics')
    
    op.drop_index('idx_chunks_created_at', 'chunks')
    op.drop_index('idx_chunks_document_id', 'chunks')
    
    op.drop_index('idx_documents_status', 'documents')
    op.drop_index('idx_documents_source_id', 'documents')
    
    op.drop_index('idx_sessions_expires_at', 'sessions')
    op.drop_index('idx_sessions_refresh_token', 'sessions')
    op.drop_index('idx_sessions_user_id', 'sessions')
    
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_role', 'users')
    op.drop_index('idx_users_username', 'users')
    op.drop_index('idx_users_email', 'users')
