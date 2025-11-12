"""Extend user role column length

Revision ID: 002
Revises: 001
Create Date: 2025-11-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend role column from VARCHAR(16) to VARCHAR(30) to accommodate 'question_submitter'
    op.alter_column('users', 'role',
                    existing_type=sa.VARCHAR(length=16),
                    type_=sa.VARCHAR(length=30),
                    existing_nullable=False)


def downgrade() -> None:
    # Revert to VARCHAR(16)
    op.alter_column('users', 'role',
                    existing_type=sa.VARCHAR(length=30),
                    type_=sa.VARCHAR(length=16),
                    existing_nullable=False)
