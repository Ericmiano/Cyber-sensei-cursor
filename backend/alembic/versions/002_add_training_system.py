"""Add training system tables

Revision ID: 002_add_training_system
Revises: 001_add_indexes
Create Date: 2026-02-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_training_system'
down_revision = '001_add_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Training Modules
    op.create_table(
        'training_modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(100)),
        sa.Column('difficulty', sa.String(50)),
        sa.Column('icon', sa.String(100)),
        sa.Column('order_index', sa.Integer),
        sa.Column('duration_minutes', sa.Integer),
        sa.Column('total_lessons', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    op.create_index('idx_training_modules_category', 'training_modules', ['category'])
    op.create_index('idx_training_modules_difficulty', 'training_modules', ['difficulty'])

    # Lessons
    op.create_table(
        'lessons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('training_modules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('order_index', sa.Integer),
        sa.Column('duration_minutes', sa.Integer),
        sa.Column('xp_reward', sa.Integer, default=50),
        sa.Column('difficulty', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    op.create_index('idx_lessons_module_id', 'lessons', ['module_id'])
    op.create_index('idx_lessons_order', 'lessons', ['module_id', 'order_index'])

    # User Training Progress (renamed to avoid conflict with existing user_progress table)
    op.create_table(
        'user_training_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('xp', sa.Integer, default=0),
        sa.Column('level', sa.Integer, default=1),
        sa.Column('current_streak', sa.Integer, default=0),
        sa.Column('longest_streak', sa.Integer, default=0),
        sa.Column('last_active_date', sa.Date),
        sa.Column('total_quizzes_passed', sa.Integer, default=0),
        sa.Column('total_exercises_completed', sa.Integer, default=0),
        sa.Column('total_chat_messages', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    op.create_index('idx_user_training_progress_user_id', 'user_training_progress', ['user_id'])
    op.create_index('idx_user_training_progress_xp', 'user_training_progress', ['xp'])
    op.create_index('idx_user_training_progress_level', 'user_training_progress', ['level'])

    # Lesson Completions
    op.create_table(
        'lesson_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('training_modules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('quiz_score', sa.Integer),
        sa.Column('exercise_completed', sa.Boolean, default=False),
        sa.Column('time_spent_minutes', sa.Integer),
        sa.UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson'),
    )
    op.create_index('idx_lesson_completions_user', 'lesson_completions', ['user_id'])
    op.create_index('idx_lesson_completions_lesson', 'lesson_completions', ['lesson_id'])
    op.create_index('idx_lesson_completions_module', 'lesson_completions', ['module_id'])

    # Achievements
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('achievement_key', sa.String(100), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('icon', sa.String(100)),
        sa.Column('requirement_type', sa.String(50)),  # 'lessons', 'xp', 'streak', etc.
        sa.Column('requirement_value', sa.Integer),
        sa.Column('xp_reward', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_achievements_key', 'achievements', ['achievement_key'])

    # User Achievements
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    op.create_index('idx_user_achievements_user', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_achievement', 'user_achievements', ['achievement_id'])

    # Activity Log
    op.create_table(
        'activity_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activity_type', sa.String(50)),  # 'lesson', 'quiz', 'exercise', etc.
        sa.Column('title', sa.String(255)),
        sa.Column('description', sa.Text),
        sa.Column('xp_earned', sa.Integer),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_activity_log_user', 'activity_log', ['user_id'])
    op.create_index('idx_activity_log_type', 'activity_log', ['activity_type'])
    op.create_index('idx_activity_log_created', 'activity_log', ['created_at'])

    # Chat Messages
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),  # 'user' or 'assistant'
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_chat_messages_user', 'chat_messages', ['user_id'])
    op.create_index('idx_chat_messages_created', 'chat_messages', ['created_at'])


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('activity_log')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('lesson_completions')
    op.drop_table('user_training_progress')
    op.drop_table('lessons')
    op.drop_table('training_modules')
