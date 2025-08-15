"""Add family information tracking fields to contacts

Revision ID: 015_add_family_information
Revises: 014_add_gender_relatioship
Create Date: 2024-08-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015_add_family_information'
down_revision = '014_add_gender_relatioship'
branch_labels = None
depends_on = None


def upgrade():
    # Add family information tracking fields to contacts table
    op.add_column('contacts', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('contacts', sa.Column('anniversary_date', sa.Date(), nullable=True))
    op.add_column('contacts', sa.Column('maiden_name', sa.String(255), nullable=True))
    op.add_column('contacts', sa.Column('family_nickname', sa.String(100), nullable=True))
    op.add_column('contacts', sa.Column('is_emergency_contact', sa.Boolean(), default=False, nullable=True))
    
    # Add index for emergency contact queries
    op.create_index('ix_contacts_is_emergency_contact', 'contacts', ['is_emergency_contact'])


def downgrade():
    # Remove index
    op.drop_index('ix_contacts_is_emergency_contact', 'contacts')
    
    # Remove family information tracking fields from contacts table
    op.drop_column('contacts', 'is_emergency_contact')
    op.drop_column('contacts', 'family_nickname')
    op.drop_column('contacts', 'maiden_name')
    op.drop_column('contacts', 'anniversary_date')
    op.drop_column('contacts', 'date_of_birth')