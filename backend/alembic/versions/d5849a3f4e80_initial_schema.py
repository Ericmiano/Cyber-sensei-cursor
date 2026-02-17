"""initial_schema

Revision ID: d5849a3f4e80
Revises: 
Create Date: 2026-02-15 16:03:32.655312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5849a3f4e80'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable uuid extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Note: pgvector extension is optional and not installed
    # Vector search features will be disabled without it
    
    # Note: Enums are created automatically by SQLAlchemy when creating tables
    # No need to create them manually
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('student', 'instructor', 'admin', 'moderator', name='role'), nullable=False, server_default='student'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )
    
    # User profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('learning_style', sa.Enum('visual', 'auditory', 'kinesthetic', 'reading', 'multimodal', name='learningstyle'), server_default='multimodal'),
        sa.Column('preferred_difficulty', sa.String(50), server_default='adaptive'),
        sa.Column('accessibility_needs', postgresql.JSON, server_default='{}'),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
        sa.Column('language', sa.String(10), server_default='en'),
        sa.Column('bio', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('refresh_token', sa.String(512), nullable=False, unique=True),
        sa.Column('access_token_jti', sa.String(255), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(512)),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_used_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # User goals table
    op.create_table(
        'user_goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('target_proficiency', sa.String(50), server_default='intermediate'),
        sa.Column('target_date', sa.DateTime()),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )

    
    # Sources table
    op.create_table(
        'sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('author', sa.String(255)),
        sa.Column('publisher', sa.String(255)),
        sa.Column('source_type', sa.Enum('pdf', 'url', 'video', 'book', 'paper', 'course', 'manual', name='sourcetype'), nullable=False),
        sa.Column('url', sa.String(2048), unique=True),
        sa.Column('domain', sa.String(255)),
        sa.Column('domain_authority', sa.Float(), server_default='0.0'),
        sa.Column('age_bonus', sa.Float(), server_default='0.0'),
        sa.Column('peer_reviewed', sa.Boolean(), server_default='false'),
        sa.Column('reliability_score', sa.Float(), server_default='0.0'),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(1024)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('page_count', sa.Integer()),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='documentstatus'), nullable=False, server_default='pending'),
        sa.Column('processing_error', sa.Text()),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Chunks table with vector support
    op.create_table(
        'chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('start_char', sa.Integer()),
        sa.Column('end_char', sa.Integer()),
        sa.Column('page_number', sa.Integer()),
        sa.Column('embedding', postgresql.ARRAY(sa.Float())),
        sa.Column('citation', postgresql.JSON, server_default='{}'),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Topics table
    op.create_table(
        'topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('parent_topic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('topics.id', ondelete='SET NULL')),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Concepts table
    op.create_table(
        'concepts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('topics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('bloom_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('difficulty', sa.Float(), server_default='0.5'),
        sa.Column('estimated_time_minutes', sa.Integer(), server_default='30'),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.CheckConstraint('bloom_level >= 1 AND bloom_level <= 6', name='check_bloom_level'),
    )
    
    # Concept edges table (prerequisite graph)
    op.create_table(
        'concept_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prerequisite_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('strength', sa.Float(), server_default='1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('concept_id != prerequisite_id', name='check_no_self_loop'),
    )
    
    # Content items table
    op.create_table(
        'content_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('topics.id', ondelete='CASCADE')),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE')),
        sa.Column('content_type', sa.Enum('study_guide', 'lab', 'quiz', 'video_script', 'summary', 'practice_exercise', name='contenttype'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('bloom_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('difficulty', sa.Float(), server_default='0.5'),
        sa.Column('citations', postgresql.JSON, server_default='[]'),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # User progress table
    op.create_table(
        'user_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # User concept mastery table (BKT)
    op.create_table(
        'user_concept_mastery',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mastery_probability', sa.Float(), nullable=False, server_default='0.3'),
        sa.Column('learn_rate', sa.Float(), server_default='0.1'),
        sa.Column('guess_rate', sa.Float(), server_default='0.2'),
        sa.Column('slip_rate', sa.Float(), server_default='0.1'),
        sa.Column('total_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('correct_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Spaced repetition schedule table (SM-2)
    op.create_table(
        'spaced_repetition_schedule',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('easiness_factor', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('interval_days', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('repetitions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_review_date', sa.DateTime(), nullable=False),
        sa.Column('last_reviewed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Learning events table (immutable audit trail)
    op.create_table(
        'learning_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.Enum('lesson_started', 'lesson_completed', 'quiz_attempted', 'quiz_completed', 'lab_started', 'lab_completed', 'concept_reviewed', 'feedback_submitted', name='eventtype'), nullable=False),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='SET NULL')),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='SET NULL')),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(512)),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    
    # Content reviews table
    op.create_table(
        'content_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'revised', name='reviewstatus'), nullable=False, server_default='pending'),
        sa.Column('accuracy_score', sa.Float()),
        sa.Column('appropriateness_score', sa.Float()),
        sa.Column('notes', sa.Text()),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Flagged items table
    op.create_table(
        'flagged_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='CASCADE')),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chunks.id', ondelete='CASCADE')),
        sa.Column('flagged_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='flagseverity'), nullable=False, server_default='medium'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('auto_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('resolved_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('details', postgresql.JSON, server_default='{}'),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(512)),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Misconceptions table
    op.create_table(
        'misconceptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('correction', sa.Text(), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('detected_from', postgresql.JSON, server_default='[]'),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Teaching feedback table
    op.create_table(
        'teaching_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='CASCADE')),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE')),
        sa.Column('efficacy_score', sa.Float()),
        sa.Column('mastery_delta', sa.Float()),
        sa.Column('time_spent_seconds', sa.Integer()),
        sa.Column('user_satisfaction', sa.Float()),
        sa.Column('shortcomings', postgresql.JSON, server_default='[]'),
        sa.Column('suggested_improvements', sa.Text()),
        sa.Column('is_addressed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Lab sessions table
    op.create_table(
        'lab_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('docker_container_id', sa.String(255), unique=True),
        sa.Column('docker_image', sa.String(255), nullable=False),
        sa.Column('status', sa.Enum('pending', 'provisioning', 'running', 'completed', 'failed', 'timeout', 'terminated', name='labstatus'), nullable=False, server_default='pending'),
        sa.Column('port_mappings', postgresql.JSON, server_default='{}'),
        sa.Column('environment_variables', postgresql.JSON, server_default='{}'),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('timeout_at', sa.DateTime()),
        sa.Column('error_message', sa.Text()),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Grading rubrics table
    op.create_table(
        'grading_rubrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('content_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_items.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('criteria', postgresql.JSON, nullable=False),
        sa.Column('total_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('passing_threshold', sa.Float(), nullable=False, server_default='0.7'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    
    # Add foreign key for user_goals.topic_id (deferred because topics table created after)
    op.create_foreign_key('fk_user_goals_topic_id', 'user_goals', 'topics', ['topic_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('grading_rubrics')
    op.drop_table('lab_sessions')
    op.drop_table('teaching_feedback')
    op.drop_table('misconceptions')
    op.drop_table('audit_logs')
    op.drop_table('flagged_items')
    op.drop_table('content_reviews')
    op.drop_table('learning_events')
    op.drop_table('spaced_repetition_schedule')
    op.drop_table('user_concept_mastery')
    op.drop_table('user_progress')
    op.drop_table('content_items')
    op.drop_table('concept_edges')
    op.drop_table('concepts')
    op.drop_table('topics')
    op.drop_table('chunks')
    op.drop_table('documents')
    op.drop_table('sources')
    op.drop_table('user_goals')
    op.drop_table('sessions')
    op.drop_table('user_profiles')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS labstatus')
    op.execute('DROP TYPE IF EXISTS flagseverity')
    op.execute('DROP TYPE IF EXISTS reviewstatus')
    op.execute('DROP TYPE IF EXISTS eventtype')
    op.execute('DROP TYPE IF EXISTS contenttype')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS sourcetype')
    op.execute('DROP TYPE IF EXISTS learningstyle')
    op.execute('DROP TYPE IF EXISTS role')
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pgvector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
