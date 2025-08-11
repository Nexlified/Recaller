"""create tenants table

Revision ID: 001
Revises: 
Create Date: 2025-08-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='uq_tenants_slug')
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)

    # Insert default tenant
    op.execute(
        """
        INSERT INTO tenants (name, slug) 
        VALUES ('Default Tenant', 'default')
        """
    )


def downgrade():
    op.drop_index(op.f('ix_tenants_id'), table_name='tenants')
    op.drop_table('tenants')
