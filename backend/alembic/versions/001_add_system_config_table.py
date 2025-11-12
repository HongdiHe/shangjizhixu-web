"""Add system_config table

Revision ID: 001
Revises:
Create Date: 2025-01-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create system_configs table."""
    op.create_table(
        'system_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_secret', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_configs_id'), 'system_configs', ['id'], unique=False)
    op.create_index(op.f('ix_system_configs_key'), 'system_configs', ['key'], unique=True)

    # Insert default configurations
    op.execute("""
        INSERT INTO system_configs (key, value, description, is_secret, created_at, updated_at) VALUES
        ('MINERU_API_URL', NULL, 'MinerU OCR API endpoint URL', false, NOW(), NOW()),
        ('MINERU_API_KEY', NULL, 'MinerU API authentication key', true, NOW(), NOW()),
        ('MINERU_MODEL_VERSION', 'vlm', 'MinerU model version (pipeline or vlm)', false, NOW(), NOW()),
        ('LLM_API_URL', 'https://api.openai.com/v1', 'OpenAI API endpoint URL', false, NOW(), NOW()),
        ('LLM_API_KEY', NULL, 'OpenAI API key', true, NOW(), NOW()),
        ('LLM_MODEL', 'gpt-4', 'LLM model name', false, NOW(), NOW()),
        ('LLM_TEMPERATURE', '0.7', 'LLM temperature parameter', false, NOW(), NOW()),
        ('LLM_MAX_TOKENS', '2000', 'LLM max tokens parameter', false, NOW(), NOW())
    """)


def downgrade() -> None:
    """Drop system_configs table."""
    op.drop_index(op.f('ix_system_configs_key'), table_name='system_configs')
    op.drop_index(op.f('ix_system_configs_id'), table_name='system_configs')
    op.drop_table('system_configs')
