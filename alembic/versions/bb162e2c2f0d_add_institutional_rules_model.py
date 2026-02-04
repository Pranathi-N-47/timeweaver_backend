"""add_institutional_rules_model

Revision ID: bb162e2c2f0d
Revises: a54be36ba74c
Create Date: 2026-02-04 16:27:02.719275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb162e2c2f0d'
down_revision: Union[str, None] = 'a54be36ba74c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create RuleType enum with unique name to avoid collision
    rule_type_enum = sa.Enum(
        'TIME_WINDOW', 'SLOT_BLACKOUT', 'MAX_CONSECUTIVE', 'ELECTIVE_SYNC',
        'FACULTY_WORKLOAD', 'ROOM_PREFERENCE', 'DAY_BLACKOUT', 'CUSTOM',
        name='institutionalruletype'
    )
    rule_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create institutional_rules table
    op.create_table(
        'institutional_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_type', rule_type_enum, nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('is_hard_constraint', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('applies_to_departments', sa.ARRAY(sa.Integer()), server_default='{}'),
        sa.Column('applies_to_years', sa.ARRAY(sa.Integer()), server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_institutional_rules_id', 'institutional_rules', ['id'])
    op.create_index('ix_institutional_rules_rule_type', 'institutional_rules', ['rule_type'])
    op.create_index('ix_institutional_rules_is_active', 'institutional_rules', ['is_active'])


def downgrade() -> None:
    op.drop_index('ix_institutional_rules_is_active', table_name='institutional_rules')
    op.drop_index('ix_institutional_rules_rule_type', table_name='institutional_rules')
    op.drop_index('ix_institutional_rules_id', table_name='institutional_rules')
    op.drop_table('institutional_rules')
    
    # Drop enum
    sa.Enum(name='institutionalruletype').drop(op.get_bind(), checkfirst=True)

