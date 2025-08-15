"""Create contact work experience table

Revision ID: 020_create_work_experience
Revises: 019_create_debts_and_payments
Create Date: 2025-01-15 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '020_create_work_experience'
down_revision = '019_create_debts_and_payments'
branch_labels = None
depends_on = None


def upgrade():
    # Create contact_work_experience table
    op.create_table(
        'contact_work_experience',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Company Information
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        
        # Position Details
        sa.Column('job_title', sa.String(255), nullable=False),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('work_location', sa.String(255), nullable=True),
        
        # Duration
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        
        # Contact Information
        sa.Column('work_phone', sa.String(50), nullable=True),
        sa.Column('work_email', sa.String(255), nullable=True),
        sa.Column('work_address', sa.Text(), nullable=True),
        
        # Professional Details
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('key_achievements', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('skills_used', postgresql.ARRAY(sa.Text()), nullable=True),
        
        # Compensation
        sa.Column('salary_range', sa.String(100), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        
        # Professional Networks
        sa.Column('linkedin_profile', sa.String(500), nullable=True),
        sa.Column('other_profiles', postgresql.JSONB(), nullable=True),
        
        # Relationships
        sa.Column('manager_contact_id', sa.Integer(), nullable=True),
        sa.Column('reporting_structure', sa.Text(), nullable=True),
        
        # Reference Information
        sa.Column('can_be_reference', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reference_notes', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['company_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['manager_contact_id'], ['contacts.id']),
        sa.PrimaryKeyConstraint('id'),
        
        # Check constraints
        sa.CheckConstraint('end_date IS NULL OR end_date >= start_date', name='check_end_date_after_start'),
        sa.CheckConstraint('NOT (is_current = true AND end_date IS NOT NULL)', name='check_current_position')
    )
    
    # Create indexes
    op.create_index('ix_contact_work_experience_id', 'contact_work_experience', ['id'])
    op.create_index('ix_contact_work_experience_contact_id', 'contact_work_experience', ['contact_id'])
    op.create_index('ix_contact_work_experience_tenant_id', 'contact_work_experience', ['tenant_id'])
    op.create_index('ix_contact_work_experience_company_name', 'contact_work_experience', ['company_name'])
    op.create_index('ix_contact_work_experience_job_title', 'contact_work_experience', ['job_title'])
    op.create_index('ix_contact_work_experience_is_current', 'contact_work_experience', ['is_current'])
    op.create_index('ix_contact_work_experience_start_date', 'contact_work_experience', ['start_date'])
    op.create_index('ix_contact_work_experience_visibility', 'contact_work_experience', ['visibility'])
    
    # Composite indexes for common queries
    op.create_index('ix_contact_work_experience_contact_current', 'contact_work_experience', ['contact_id', 'is_current'])
    op.create_index('ix_contact_work_experience_company_current', 'contact_work_experience', ['company_name', 'is_current'])


def downgrade():
    op.drop_table('contact_work_experience')
