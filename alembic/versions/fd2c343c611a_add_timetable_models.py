"""add_timetable_models

Revision ID: fd2c343c611a
Revises: 7bcc83480b76
Create Date: 2026-02-02 12:36:45.724782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd2c343c611a'
down_revision: Union[str, None] = '7bcc83480b76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    """
    Create tables for Module 3: Timetable Generation & Scheduling
    
    Tables:
        - timetables: Generated timetables with quality metrics
        - timetable_slots: Individual class assignments
        - conflicts: Detected scheduling conflicts
    """
    # Create timetables table
    op.create_table(
        'timetables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='generating'),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('conflict_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('generation_algorithm', sa.String(length=20), nullable=True),
        sa.Column('generation_time_seconds', sa.Float(), nullable=True),
        sa.Column('generation_config', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('generating', 'completed', 'failed', 'archived')", name='check_status_valid'),
        sa.CheckConstraint('quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)', name='check_quality_score_range'),
        sa.CheckConstraint('conflict_count >= 0', name='check_conflict_count_positive'),
        sa.CheckConstraint("generation_algorithm IS NULL OR generation_algorithm IN ('GA', 'SA', 'HYBRID', 'CSP_GREEDY')", name='check_algorithm_valid'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timetables_id', 'timetables', ['id'])
    op.create_index('ix_timetables_semester_id', 'timetables', ['semester_id'])
    op.create_index('ix_timetables_status', 'timetables', ['status'])
    op.create_index('ix_timetables_is_published', 'timetables', ['is_published'])
    
    # Create timetable_slots table
    op.create_table(
        'timetable_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timetable_id', sa.Integer(), nullable=False),
        sa.Column('section_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('time_slot_id', sa.Integer(), nullable=False),
        sa.Column('faculty_id', sa.Integer(), nullable=True),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='check_day_of_week_valid'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['time_slot_id'], ['time_slots.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['timetable_id'], ['timetables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timetable_slots_id', 'timetable_slots', ['id'])
    op.create_index('ix_timetable_slots_timetable_id', 'timetable_slots', ['timetable_id'])
    op.create_index('ix_timetable_slots_section_id', 'timetable_slots', ['section_id'])
    op.create_index('ix_timetable_slots_room_id', 'timetable_slots', ['room_id'])
    op.create_index('ix_timetable_slots_time_slot_id', 'timetable_slots', ['time_slot_id'])
    op.create_index('ix_timetable_slots_faculty_id', 'timetable_slots', ['faculty_id'])
    op.create_index('ix_timetable_slots_is_locked', 'timetable_slots', ['is_locked'])
    
    # Performance indexes for conflict detection
    op.create_index(
        'idx_timetable_slots_lookup',
        'timetable_slots',
        ['timetable_id', 'day_of_week', 'time_slot_id', 'room_id']
    )
    op.create_index(
        'idx_timetable_slots_faculty',
        'timetable_slots',
        ['faculty_id', 'day_of_week', 'time_slot_id'],
        postgresql_where=sa.text('faculty_id IS NOT NULL')
    )
    
    # Create conflicts table
    op.create_table(
        'conflicts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timetable_id', sa.Integer(), nullable=False),
        sa.Column('conflict_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='HIGH'),
        sa.Column('slot_ids', sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            """conflict_type IN (
                'ROOM_CLASH', 'FACULTY_CLASH', 'STUDENT_CLASH',
                'CAPACITY_VIOLATION', 'LAB_REQUIREMENT_VIOLATION',
                'ELECTIVE_CLASH', 'CONSTRAINT_VIOLATION'
            )""",
            name='check_conflict_type_valid'
        ),
        sa.CheckConstraint("severity IN ('HIGH', 'MEDIUM', 'LOW')", name='check_severity_valid'),
        sa.ForeignKeyConstraint(['timetable_id'], ['timetables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conflicts_id', 'conflicts', ['id'])
    op.create_index('ix_conflicts_timetable_id', 'conflicts', ['timetable_id'])
    op.create_index('ix_conflicts_conflict_type', 'conflicts', ['conflict_type'])
    op.create_index('ix_conflicts_is_resolved', 'conflicts', ['is_resolved'])


def downgrade() -> None:
    """Drop all Module 3 tables"""
    op.drop_table('conflicts')
    op.drop_table('timetable_slots')
    op.drop_table('timetables')

