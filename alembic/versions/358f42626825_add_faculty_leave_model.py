"""add_faculty_leave_model

Revision ID: 358f42626825
Revises: bb162e2c2f0d
Create Date: 2026-02-04 17:15:01.250579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '358f42626825'
down_revision: Union[str, None] = 'bb162e2c2f0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create leave type enums
    leave_type_enum = sa.Enum(
        'SICK', 'CASUAL', 'MATERNITY', 'PATERNITY', 'SABBATICAL', 
        'STUDY', 'EMERGENCY', 'OTHER',
        name='leavetype'
    )
    leave_type_enum.create(op.get_bind(), checkfirst=True)
    
    leave_strategy_enum = sa.Enum(
        'WITHIN_SECTION_SWAP', 'REDISTRIBUTE', 'REPLACEMENT', 'CANCEL', 'MANUAL',
        name='leavestrategy'
    )
    leave_strategy_enum.create(op.get_bind(), checkfirst=True)
    
    leave_status_enum = sa.Enum(
        'PROPOSED', 'APPROVED', 'APPLIED', 'REJECTED', 'CANCELLED',
        name='leavestatus'
    )
    leave_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create faculty_leaves table
    op.create_table(
        'faculty_leaves',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faculty_id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('timetable_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('leave_type', leave_type_enum, nullable=False),
        sa.Column('strategy', leave_strategy_enum, nullable=False, server_default='WITHIN_SECTION_SWAP'),
        sa.Column('status', leave_status_enum, nullable=False, server_default='PROPOSED'),
        sa.Column('replacement_faculty_id', sa.Integer(), nullable=True),
        sa.Column('impact_analysis', sa.JSON(), nullable=True),
        sa.Column('resolution_details', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['faculty_id'], ['users.id']),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id']),
        sa.ForeignKeyConstraint(['timetable_id'], ['timetables.id']),
        sa.ForeignKeyConstraint(['replacement_faculty_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )
    op.create_index('ix_faculty_leaves_id', 'faculty_leaves', ['id'])
    op.create_index('ix_faculty_leaves_faculty_id', 'faculty_leaves', ['faculty_id'])
    op.create_index('ix_faculty_leaves_semester_id', 'faculty_leaves', ['semester_id'])
    op.create_index('ix_faculty_leaves_status', 'faculty_leaves', ['status'])


def downgrade() -> None:
    op.drop_index('ix_faculty_leaves_status', table_name='faculty_leaves')
    op.drop_index('ix_faculty_leaves_semester_id', table_name='faculty_leaves')
    op.drop_index('ix_faculty_leaves_faculty_id', table_name='faculty_leaves')
    op.drop_index('ix_faculty_leaves_id', table_name='faculty_leaves')
    op.drop_table('faculty_leaves')
    
    # Drop enums
    sa.Enum(name='leavestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='leavestrategy').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='leavetype').drop(op.get_bind(), checkfirst=True)
