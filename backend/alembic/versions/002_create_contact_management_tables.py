"""create contact management tables

Revision ID: 002
Revises: 001
Create Date: 2025-08-11 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('organization_type', sa.String(50), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('size', sa.String(20), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(50), nullable=True),
        sa.Column('country', sa.String(50), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_organizations_tenant_id_tenants'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_tenant_id'), 'organizations', ['tenant_id'], unique=False)

    # Create social_groups table
    op.create_table(
        'social_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('group_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=True, default=0),
        sa.Column('meeting_frequency', sa.String(30), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_social_groups_tenant_id_tenants'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_groups_id'), 'social_groups', ['id'], unique=False)
    op.create_index(op.f('ix_social_groups_tenant_id'), 'social_groups', ['tenant_id'], unique=False)

    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('job_title', sa.String(200), nullable=True),
        sa.Column('current_organization_id', sa.Integer(), nullable=True),
        sa.Column('alma_mater_id', sa.Integer(), nullable=True),
        sa.Column('connection_strength', sa.Numeric(3,2), nullable=True, default=5.0),
        sa.Column('networking_value', sa.String(20), nullable=True, default='medium'),
        sa.Column('relationship_status', sa.String(50), nullable=True, default='active'),
        sa.Column('total_interactions', sa.Integer(), nullable=True, default=0),
        sa.Column('last_meaningful_interaction', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interaction_frequency', sa.String(20), nullable=True),
        sa.Column('next_suggested_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('follow_up_urgency', sa.String(20), nullable=True, default='medium'),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        sa.Column('tags', ARRAY(sa.String()), nullable=True, default=[]),
        sa.Column('contact_source', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_archived', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_contacts_tenant_id_tenants'),
        sa.ForeignKeyConstraint(['current_organization_id'], ['organizations.id'], name='fk_contacts_current_organization_id_organizations'),
        sa.ForeignKeyConstraint(['alma_mater_id'], ['organizations.id'], name='fk_contacts_alma_mater_id_organizations'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_tenant_id'), 'contacts', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=False)

    # Create contact_interactions table
    op.create_table(
        'contact_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('interaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('interaction_quality', sa.Numeric(2,1), nullable=True, default=5.0),
        sa.Column('interaction_mood', sa.String(20), nullable=True),
        sa.Column('initiated_by', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('topics_discussed', ARRAY(sa.String()), nullable=True, default=[]),
        sa.Column('follow_up_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('next_steps', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name='fk_contact_interactions_contact_id_contacts'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_interactions_id'), 'contact_interactions', ['id'], unique=False)
    op.create_index(op.f('ix_contact_interactions_contact_id'), 'contact_interactions', ['contact_id'], unique=False)

    # Create social_group_activities table
    op.create_table(
        'social_group_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('expected_attendees', sa.Integer(), nullable=True),
        sa.Column('actual_attendees', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='planned'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], name='fk_social_group_activities_social_group_id_social_groups'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_group_activities_id'), 'social_group_activities', ['id'], unique=False)
    op.create_index(op.f('ix_social_group_activities_social_group_id'), 'social_group_activities', ['social_group_id'], unique=False)

    # Create contact_social_group_memberships table
    op.create_table(
        'contact_social_group_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('membership_status', sa.String(20), nullable=True, default='active'),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('joined_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('left_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name='fk_contact_social_group_memberships_contact_id_contacts'),
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], name='fk_contact_social_group_memberships_social_group_id_social_groups'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_social_group_memberships_id'), 'contact_social_group_memberships', ['id'], unique=False)
    op.create_index(op.f('ix_contact_social_group_memberships_contact_id'), 'contact_social_group_memberships', ['contact_id'], unique=False)
    op.create_index(op.f('ix_contact_social_group_memberships_social_group_id'), 'contact_social_group_memberships', ['social_group_id'], unique=False)

def downgrade():
    op.drop_table('contact_social_group_memberships')
    op.drop_table('social_group_activities')
    op.drop_table('contact_interactions')
    op.drop_table('contacts')
    op.drop_table('social_groups')
    op.drop_table('organizations')