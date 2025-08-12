"""Create social groups tables

Revision ID: 004_create_social_groups
Revises: 003_create_contacts_organizations
Create Date: 2025-08-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_create_social_groups'
down_revision = '003_create_contacts_org'
branch_labels = None
depends_on = None


def upgrade():
    # Create social_groups table
    op.create_table(
        'social_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('group_type', sa.String(50), nullable=False),
        sa.Column('privacy_level', sa.String(20), nullable=False, server_default='private'),
        sa.Column('meets_regularly', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('meeting_frequency', sa.String(50), nullable=True),
        sa.Column('meeting_location', sa.String(255), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_social_groups_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_social_groups_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_groups_id'), 'social_groups', ['id'], unique=False)
    op.create_index(op.f('ix_social_groups_tenant_id'), 'social_groups', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_social_groups_name'), 'social_groups', ['name'], unique=False)
    op.create_index(op.f('ix_social_groups_group_type'), 'social_groups', ['group_type'], unique=False)

    # Create social_group_memberships table
    op.create_table(
        'social_group_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='member'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], name=op.f('fk_social_group_memberships_social_group_id_social_groups'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_social_group_memberships_contact_id_contacts'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('social_group_id', 'contact_id', name='uq_social_group_memberships_group_contact')
    )
    op.create_index(op.f('ix_social_group_memberships_id'), 'social_group_memberships', ['id'], unique=False)
    op.create_index(op.f('ix_social_group_memberships_social_group_id'), 'social_group_memberships', ['social_group_id'], unique=False)
    op.create_index(op.f('ix_social_group_memberships_contact_id'), 'social_group_memberships', ['contact_id'], unique=False)

    # Create social_group_activities table
    op.create_table(
        'social_group_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='planned'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], name=op.f('fk_social_group_activities_social_group_id_social_groups'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_social_group_activities_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_group_activities_id'), 'social_group_activities', ['id'], unique=False)
    op.create_index(op.f('ix_social_group_activities_social_group_id'), 'social_group_activities', ['social_group_id'], unique=False)
    op.create_index(op.f('ix_social_group_activities_activity_type'), 'social_group_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_social_group_activities_scheduled_at'), 'social_group_activities', ['scheduled_at'], unique=False)

    # Create social_group_activity_attendance table
    op.create_table(
        'social_group_activity_attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('attendance_status', sa.String(20), nullable=False, server_default='invited'),
        sa.Column('response_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attended', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['activity_id'], ['social_group_activities.id'], name=op.f('fk_social_group_activity_attendance_activity_id_social_group_activities'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_social_group_activity_attendance_contact_id_contacts'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('activity_id', 'contact_id', name='uq_social_group_activity_attendance_activity_contact')
    )
    op.create_index(op.f('ix_social_group_activity_attendance_id'), 'social_group_activity_attendance', ['id'], unique=False)
    op.create_index(op.f('ix_social_group_activity_attendance_activity_id'), 'social_group_activity_attendance', ['activity_id'], unique=False)
    op.create_index(op.f('ix_social_group_activity_attendance_contact_id'), 'social_group_activity_attendance', ['contact_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_social_group_activity_attendance_contact_id'), table_name='social_group_activity_attendance')
    op.drop_index(op.f('ix_social_group_activity_attendance_activity_id'), table_name='social_group_activity_attendance')
    op.drop_index(op.f('ix_social_group_activity_attendance_id'), table_name='social_group_activity_attendance')
    op.drop_table('social_group_activity_attendance')
    
    op.drop_index(op.f('ix_social_group_activities_scheduled_at'), table_name='social_group_activities')
    op.drop_index(op.f('ix_social_group_activities_activity_type'), table_name='social_group_activities')
    op.drop_index(op.f('ix_social_group_activities_social_group_id'), table_name='social_group_activities')
    op.drop_index(op.f('ix_social_group_activities_id'), table_name='social_group_activities')
    op.drop_table('social_group_activities')
    
    op.drop_index(op.f('ix_social_group_memberships_contact_id'), table_name='social_group_memberships')
    op.drop_index(op.f('ix_social_group_memberships_social_group_id'), table_name='social_group_memberships')
    op.drop_index(op.f('ix_social_group_memberships_id'), table_name='social_group_memberships')
    op.drop_table('social_group_memberships')
    
    op.drop_index(op.f('ix_social_groups_group_type'), table_name='social_groups')
    op.drop_index(op.f('ix_social_groups_name'), table_name='social_groups')
    op.drop_index(op.f('ix_social_groups_tenant_id'), table_name='social_groups')
    op.drop_index(op.f('ix_social_groups_id'), table_name='social_groups')
    op.drop_table('social_groups')