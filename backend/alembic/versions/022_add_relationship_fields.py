"""Add relationship enhancement fields

Revision ID: 022_add_relationship_fields
Revises: 020_create_work_experience
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '022_add_relationship_fields'
down_revision = '021_create_shared_activities'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to contact_relationships table
    op.add_column('contact_relationships', sa.Column('relationship_strength', sa.Integer(), nullable=True))
    op.add_column('contact_relationships', sa.Column('relationship_status', sa.String(20), nullable=False, server_default='active'))
    op.add_column('contact_relationships', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('contact_relationships', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('contact_relationships', sa.Column('is_mutual', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('contact_relationships', sa.Column('context', sa.Text(), nullable=True))


def downgrade():
    # Remove the added fields
    op.drop_column('contact_relationships', 'context')
    op.drop_column('contact_relationships', 'is_mutual')
    op.drop_column('contact_relationships', 'end_date')
    op.drop_column('contact_relationships', 'start_date')
    op.drop_column('contact_relationships', 'relationship_status')
    op.drop_column('contact_relationships', 'relationship_strength')
