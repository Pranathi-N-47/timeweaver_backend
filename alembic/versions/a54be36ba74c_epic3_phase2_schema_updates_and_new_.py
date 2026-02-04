"""epic3_phase2_schema_updates_and_new_models

Manual migration for Epic 3 Phase 2 schema updates.

Revision ID: a54be36ba74c
Revises: fd2c343c611a
Create Date: 2026-02-04 11:23:57.789404

Changes:
- Create SemesterType and CourseCategory enum types
- Add 3 new tables: curriculum, course_elective_assignments, course_batching_config
- Modify semesters: add semester_type (ODD/EVEN)
- Modify sections: remove semester_id/year, add batch_year_start/end, dedicated_room_id, class_advisor_ids
- Modify rooms: add full_name, change building to required
- Modify courses: add course_category enum
- Modify elective_groups: remove semester_id, add participating_department_ids, make name unique
- Modify timetable_slots: replace time_slot_id+faculty_id with start_slot_id+duration_slots+primary_faculty_id+assisting_faculty_ids+batch_number
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a54be36ba74c'
down_revision: Union[str, None] = 'fd2c343c611a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # STEP 1: Create PostgreSQL Enum Types
    # ========================================
    op.execute('DROP TYPE IF EXISTS semestertype CASCADE')
    op.execute('DROP TYPE IF EXISTS coursecategory CASCADE')
    
    op.execute("CREATE TYPE semestertype AS ENUM ('ODD', 'EVEN')")
    op.execute("CREATE TYPE coursecategory AS ENUM ('CORE', 'PROFESSIONAL_ELECTIVE', 'FREE_ELECTIVE', 'PROJECT', 'MENTORING')")
    
    # ========================================
    # STEP 2: Create New Tables
    # ========================================
    
    # Curriculum table
    op.create_table('curriculum',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('year_level', sa.Integer(), nullable=False),
        sa.Column('semester_type', postgresql.ENUM('ODD', 'EVEN', name='semestertype', create_type=False), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint('year_level >= 1 AND year_level <= 4', name='check_year_level_valid'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('department_id', 'year_level', 'semester_type', 'course_id', name='uq_curriculum_dept_year_sem_course')
    )
    op.create_index(op.f('ix_curriculum_id'), 'curriculum', ['id'], unique=False)
    op.create_index(op.f('ix_curriculum_department_id'), 'curriculum', ['department_id'], unique=False)
    op.create_index(op.f('ix_curriculum_course_id'), 'curriculum', ['course_id'], unique=False)
    
    # CourseElectiveAssignment table
    op.create_table('course_elective_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('elective_group_id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('assigned_room_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assigned_room_id'], ['rooms.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['elective_group_id'], ['elective_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('elective_group_id', 'semester_id', 'course_id', name='uq_elective_assignment_group_sem_course')
    )
    op.create_index(op.f('ix_course_elective_assignments_id'), 'course_elective_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_course_elective_assignments_elective_group_id'), 'course_elective_assignments', ['elective_group_id'], unique=False)
    op.create_index(op.f('ix_course_elective_assignments_semester_id'), 'course_elective_assignments', ['semester_id'], unique=False)
    op.create_index(op.f('ix_course_elective_assignments_course_id'), 'course_elective_assignments', ['course_id'], unique=False)
    
    # CourseBatchingConfig table
    op.create_table('course_batching_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('num_batches', sa.Integer(), nullable=False),
        sa.Column('batch_size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint('batch_size > 0', name='check_batch_size_positive'),
        sa.CheckConstraint('num_batches >= 1 AND num_batches <= 10', name='check_num_batches_valid'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_id', 'semester_id', name='uq_batching_course_sem')
    )
    op.create_index(op.f('ix_course_batching_config_id'), 'course_batching_config', ['id'], unique=False)
    op.create_index(op.f('ix_course_batching_config_course_id'), 'course_batching_config', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_batching_config_semester_id'), 'course_batching_config', ['semester_id'], unique=False)
    
    # ========================================
    # STEP 3: Modify Existing Tables
    # ========================================
    
    # --- Semesters: Add semester_type ---
    op.add_column('semesters', sa.Column('semester_type', postgresql.ENUM('ODD', 'EVEN', name='semestertype', create_type=False), nullable=False, server_default='ODD'))
    
    # --- Sections: Batch lifecycle changes ---
    op.add_column('sections', sa.Column('batch_year_start', sa.Integer(), nullable=False, server_default='2024'))
    op.add_column('sections', sa.Column('batch_year_end', sa.Integer(), nullable=False, server_default='2028'))
    op.add_column('sections', sa.Column('dedicated_room_id', sa.Integer(), nullable=True))
    op.add_column('sections', sa.Column('class_advisor_ids', postgresql.ARRAY(sa.Integer()), nullable=True))
    
    op.create_foreign_key('sections_dedicated_room_id_fkey', 'sections', 'rooms', ['dedicated_room_id'], ['id'])
    op.create_index(op.f('ix_sections_dedicated_room_id'), 'sections', ['dedicated_room_id'], unique=False)
    
    # Drop old semester-based fields
    op.drop_constraint('sections_semester_id_fkey', 'sections', type_='foreignkey')
    op.execute('ALTER TABLE sections DROP CONSTRAINT IF EXISTS check_year_range')
    op.drop_column('sections', 'semester_id')
    op.drop_column('sections', 'year')
    
    # Add new constraint
    op.execute('ALTER TABLE sections ADD CONSTRAINT check_batch_years_valid CHECK (batch_year_start < batch_year_end)')
    
    # --- Rooms: Split room identification ---
    op.add_column('rooms', sa.Column('full_name', sa.String(length=100), nullable=False, server_default='TEMP'))
    op.alter_column('rooms', 'building',
                   existing_type=sa.VARCHAR(length=100),
                   type_=sa.String(length=50),
                   nullable=False)
    
    op.drop_index('ix_rooms_room_number', table_name='rooms')
    op.create_index(op.f('ix_rooms_building'), 'rooms', ['building'], unique=False)
    op.create_unique_constraint('uq_rooms_full_name', 'rooms', ['full_name'])
    
    # --- Courses: Add course_category ---
    op.add_column('courses', sa.Column('course_category', postgresql.ENUM('CORE', 'PROFESSIONAL_ELECTIVE', 'FREE_ELECTIVE', 'PROJECT', 'MENTORING', name='coursecategory', create_type=False), nullable=False, server_default='CORE'))
    
    # --- ElectiveGroups: Make permanent, add participating depts ---
    op.add_column('elective_groups', sa.Column('participating_department_ids', postgresql.ARRAY(sa.Integer()), nullable=True))
    op.create_unique_constraint('uq_elective_groups_name', 'elective_groups', ['name'])
    
    op.drop_constraint('elective_groups_semester_id_fkey', 'elective_groups', type_='foreignkey')
    op.drop_column('elective_groups', 'semester_id')
    
    # --- TimetableSlots: Multi-slot support ---
    # Drop old columns and constraints
    op.drop_constraint('timetable_slots_time_slot_id_fkey', 'timetable_slots', type_='foreignkey')
    op.drop_column('timetable_slots', 'time_slot_id')
    op.drop_column('timetable_slots', 'faculty_id')
    
    # Add new columns
    op.add_column('timetable_slots', sa.Column('start_slot_id', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('timetable_slots', sa.Column('duration_slots', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('timetable_slots', sa.Column('primary_faculty_id', sa.Integer(), nullable=True))
    op.add_column('timetable_slots', sa.Column('assisting_faculty_ids', postgresql.ARRAY(sa.Integer()), nullable=True))
    op.add_column('timetable_slots', sa.Column('batch_number', sa.Integer(), nullable=True))
    
    # Add new FK and indexes
    op.create_foreign_key('timetable_slots_start_slot_id_fkey', 'timetable_slots', 'time_slots', ['start_slot_id'], ['id'])
    op.create_index(op.f('ix_timetable_slots_start_slot_id'), 'timetable_slots', ['start_slot_id'], unique=False)
    op.create_index(op.f('ix_timetable_slots_primary_faculty_id'), 'timetable_slots', ['primary_faculty_id'], unique=False)
    
    # Add new constraints
    op.execute('ALTER TABLE timetable_slots ADD CONSTRAINT check_duration_slots_valid CHECK (duration_slots >= 1 AND duration_slots <= 5)')
    op.execute('ALTER TABLE timetable_slots ADD CONSTRAINT check_batch_number_positive CHECK (batch_number IS NULL OR batch_number > 0)')


def downgrade() -> None:
    # TimetableSlots
    op.execute('ALTER TABLE timetable_slots DROP CONSTRAINT IF EXISTS check_batch_number_positive')
    op.execute('ALTER TABLE timetable_slots DROP CONSTRAINT IF EXISTS check_duration_slots_valid')
    op.drop_index(op.f('ix_timetable_slots_primary_faculty_id'), table_name='timetable_slots')
    op.drop_index(op.f('ix_timetable_slots_start_slot_id'), table_name='timetable_slots')
    op.drop_constraint('timetable_slots_start_slot_id_fkey', 'timetable_slots', type_='foreignkey')
    
    op.drop_column('timetable_slots', 'batch_number')
    op.drop_column('timetable_slots', 'assisting_faculty_ids')
    op.drop_column('timetable_slots', 'primary_faculty_id')
    op.drop_column('timetable_slots', 'duration_slots')
    op.drop_column('timetable_slots', 'start_slot_id')
    
    op.add_column('timetable_slots', sa.Column('faculty_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('timetable_slots', sa.Column('time_slot_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('timetable_slots_time_slot_id_fkey', 'timetable_slots', 'time_slots', ['time_slot_id'], ['id'], ondelete='CASCADE')
    
    # ElectiveGroups
    op.add_column('elective_groups', sa.Column('semester_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('elective_groups_semester_id_fkey', 'elective_groups', 'semesters', ['semester_id'], ['id'])
    op.drop_constraint('uq_elective_groups_name', 'elective_groups', type_='unique')
    op.drop_column('elective_groups', 'participating_department_ids')
    
    # Courses
    op.drop_column('courses', 'course_category')
    
    # Rooms
    op.drop_constraint('uq_rooms_full_name', 'rooms', type_='unique')
    op.drop_index(op.f('ix_rooms_building'), table_name='rooms')
    op.create_index('ix_rooms_room_number', 'rooms', ['room_number'], unique=True)
    op.alter_column('rooms', 'building',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=100),
                   nullable=True)
    op.drop_column('rooms', 'full_name')
    
    # Sections
    op.execute('ALTER TABLE sections DROP CONSTRAINT IF EXISTS check_batch_years_valid')
    op.add_column('sections', sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('sections', sa.Column('semester_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('sections_semester_id_fkey', 'sections', 'semesters', ['semester_id'], ['id'], ondelete='CASCADE')
    
    op.drop_index(op.f('ix_sections_dedicated_room_id'), table_name='sections')
    op.drop_constraint('sections_dedicated_room_id_fkey', 'sections', type_='foreignkey')
    op.drop_column('sections', 'class_advisor_ids')
    op.drop_column('sections', 'dedicated_room_id')
    op.drop_column('sections', 'batch_year_end')
    op.drop_column('sections', 'batch_year_start')
    
    # Semesters
    op.drop_column('semesters', 'semester_type')
    
    # Drop new tables
    op.drop_index(op.f('ix_course_batching_config_semester_id'), table_name='course_batching_config')
    op.drop_index(op.f('ix_course_batching_config_course_id'), table_name='course_batching_config')
    op.drop_index(op.f('ix_course_batching_config_id'), table_name='course_batching_config')
    op.drop_table('course_batching_config')
    
    op.drop_index(op.f('ix_course_elective_assignments_course_id'), table_name='course_elective_assignments')
    op.drop_index(op.f('ix_course_elective_assignments_semester_id'), table_name='course_elective_assignments')
    op.drop_index(op.f('ix_course_elective_assignments_elective_group_id'), table_name='course_elective_assignments')
    op.drop_index(op.f('ix_course_elective_assignments_id'), table_name='course_elective_assignments')
    op.drop_table('course_elective_assignments')
    
    op.drop_index(op.f('ix_curriculum_course_id'), table_name='curriculum')
    op.drop_index(op.f('ix_curriculum_department_id'), table_name='curriculum')
    op.drop_index(op.f('ix_curriculum_id'), table_name='curriculum')
    op.drop_table('curriculum')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS coursecategory')
    op.execute('DROP TYPE IF EXISTS semestertype')
