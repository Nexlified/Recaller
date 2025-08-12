"""create social groups tables

Revision ID: 003
Revises: 002
Create Date: 2025-08-12 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
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
        sa.Column('privacy_level', sa.String(20), nullable=True, server_default='private'),
        sa.Column('meets_regularly', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('meeting_frequency', sa.String(50), nullable=True),
        sa.Column('meeting_day_of_week', sa.Integer(), nullable=True),
        sa.Column('meeting_time', sa.Time(), nullable=True),
        sa.Column('meeting_location', sa.String(255), nullable=True),
        sa.Column('virtual_meeting_url', sa.String(500), nullable=True),
        sa.Column('founded_date', sa.Date(), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_members', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('auto_add_contacts', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('group_image_url', sa.String(500), nullable=True),
        sa.Column('group_color', sa.String(7), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_social_groups_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_social_groups_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_groups_id'), 'social_groups', ['id'], unique=False)
    op.create_index(op.f('ix_social_groups_tenant_id'), 'social_groups', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_social_groups_group_type'), 'social_groups', ['group_type'], unique=False)
    op.create_index(op.f('ix_social_groups_is_active'), 'social_groups', ['is_active'], unique=False)

    # Create contact_social_group_memberships table
    op.create_table(
        'contact_social_group_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(100), nullable=True, server_default='member'),
        sa.Column('membership_status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('joined_date', sa.Date(), server_default=sa.text('current_date'), nullable=True),
        sa.Column('left_date', sa.Date(), nullable=True),
        sa.Column('participation_level', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('last_participated', sa.Date(), nullable=True),
        sa.Column('total_events_attended', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('membership_notes', sa.Text(), nullable=True),
        sa.Column('invited_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE', name=op.f('fk_contact_social_group_memberships_contact_id_contacts')),
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], ondelete='CASCADE', name=op.f('fk_contact_social_group_memberships_social_group_id_social_groups')),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'], name=op.f('fk_contact_social_group_memberships_invited_by_user_id_users')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'social_group_id', name=op.f('uq_contact_social_group_memberships_contact_id_social_group_id'))
    )
    op.create_index(op.f('ix_contact_social_group_memberships_id'), 'contact_social_group_memberships', ['id'], unique=False)
    op.create_index(op.f('ix_contact_social_group_memberships_contact_id'), 'contact_social_group_memberships', ['contact_id'], unique=False)
    op.create_index(op.f('ix_contact_social_group_memberships_social_group_id'), 'contact_social_group_memberships', ['social_group_id'], unique=False)
    op.create_index(op.f('ix_contact_social_group_memberships_membership_status'), 'contact_social_group_memberships', ['membership_status'], unique=False)

    # Create social_group_activities table
    op.create_table(
        'social_group_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('activity_type', sa.String(50), nullable=True),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('virtual_meeting_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='planned'),
        sa.Column('max_attendees', sa.Integer(), nullable=True),
        sa.Column('actual_attendees', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cost', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('organizer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], ondelete='CASCADE', name=op.f('fk_social_group_activities_social_group_id_social_groups')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_social_group_activities_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_group_activities_id'), 'social_group_activities', ['id'], unique=False)
    op.create_index(op.f('ix_social_group_activities_social_group_id'), 'social_group_activities', ['social_group_id'], unique=False)
    op.create_index(op.f('ix_social_group_activities_scheduled_date'), 'social_group_activities', ['scheduled_date'], unique=False)

    # Create social_group_activity_attendance table
    op.create_table(
        'social_group_activity_attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('attendance_status', sa.String(50), nullable=True, server_default='invited'),
        sa.Column('rsvp_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attendance_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['social_group_activities.id'], ondelete='CASCADE', name=op.f('fk_social_group_activity_attendance_activity_id_social_group_activities')),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE', name=op.f('fk_social_group_activity_attendance_contact_id_contacts')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('activity_id', 'contact_id', name=op.f('uq_social_group_activity_attendance_activity_id_contact_id'))
    )
    op.create_index(op.f('ix_social_group_activity_attendance_id'), 'social_group_activity_attendance', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_social_group_activity_attendance_id'), table_name='social_group_activity_attendance')
    op.drop_table('social_group_activity_attendance')
    
    op.drop_index(op.f('ix_social_group_activities_scheduled_date'), table_name='social_group_activities')
    op.drop_index(op.f('ix_social_group_activities_social_group_id'), table_name='social_group_activities')
    op.drop_index(op.f('ix_social_group_activities_id'), table_name='social_group_activities')
    op.drop_table('social_group_activities')
    
    op.drop_index(op.f('ix_contact_social_group_memberships_membership_status'), table_name='contact_social_group_memberships')
    op.drop_index(op.f('ix_contact_social_group_memberships_social_group_id'), table_name='contact_social_group_memberships')
    op.drop_index(op.f('ix_contact_social_group_memberships_contact_id'), table_name='contact_social_group_memberships')
    op.drop_index(op.f('ix_contact_social_group_memberships_id'), table_name='contact_social_group_memberships')
    op.drop_table('contact_social_group_memberships')
    
    op.drop_index(op.f('ix_social_groups_is_active'), table_name='social_groups')
    op.drop_index(op.f('ix_social_groups_group_type'), table_name='social_groups')
    op.drop_index(op.f('ix_social_groups_tenant_id'), table_name='social_groups')
    op.drop_index(op.f('ix_social_groups_id'), table_name='social_groups')
    op.drop_table('social_groups')