"""Create currencies table

Revision ID: 014_create_currencies_table
Revises: 013_optimize_journal
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '014_create_currencies_table'
down_revision = '013_optimize_journal'
branch_labels = None
depends_on = None

def upgrade():
    # Create currencies table
    op.create_table(
        'currencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(3), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('decimal_places', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('country_codes', postgresql.ARRAY(sa.String(2)), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create indexes
    op.create_index('ix_currencies_id', 'currencies', ['id'])
    op.create_index('ix_currencies_code', 'currencies', ['code'])
    op.create_index('ix_currencies_is_active', 'currencies', ['is_active'])
    op.create_index('ix_currencies_is_default', 'currencies', ['is_default'])

def downgrade():
    op.drop_table('currencies')