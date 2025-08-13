"""add_contact_visibility_scope

Revision ID: 56acbb5a0ee1
Revises: 007_create_events
Create Date: 2025-08-13 09:45:54.315629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56acbb5a0ee1'
down_revision = '007_create_events'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add visibility column to contacts table
    op.add_column('contacts', sa.Column('visibility', sa.String(10), nullable=False, server_default='private'))
    
    # Add index for visibility column for better query performance
    op.create_index(op.f('ix_contacts_visibility'), 'contacts', ['visibility'], unique=False)


def downgrade() -> None:
    # Remove index
    op.drop_index(op.f('ix_contacts_visibility'), table_name='contacts')
    
    # Remove visibility column
    op.drop_column('contacts', 'visibility')
