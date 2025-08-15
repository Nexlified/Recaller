"""Add gender field to contacts and create contact relationships table

Revision ID: 014_add_gender_and_relationships
Revises: 013_optimize_journal
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014_add_gender_and_relationships'
down_revision = '013_optimize_journal'
branch_labels = None
depends_on = None


def upgrade():
    # Add gender field to contacts table
    op.add_column('contacts', sa.Column('gender', sa.String(20), nullable=True))
    
    # Create contact_relationships table
    op.create_table(
        'contact_relationships',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False, index=True),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('contact_a_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=False, index=True),
        sa.Column('contact_b_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=False, index=True),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('relationship_category', sa.String(20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('is_gender_resolved', sa.Boolean(), default=False, nullable=True),
        sa.Column('original_relationship_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.UniqueConstraint('tenant_id', 'contact_a_id', 'contact_b_id', name='uq_tenant_contact_relationship')
    )


def downgrade():
    # Drop contact_relationships table
    op.drop_table('contact_relationships')
    
    # Remove gender field from contacts table
    op.drop_column('contacts', 'gender')