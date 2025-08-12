"""Create events tables

Revision ID: 007_create_events
Revises: 006_create_configuration
Create Date: 2025-08-12 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_create_events'
down_revision = '006_create_configuration'
branch_labels = None
depends_on = None


def upgrade():
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        
        # Basic Information
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_category', sa.String(50), nullable=True),
        
        # Date and Time
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=True, server_default='UTC'),
        
        # Location
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('venue', sa.String(255), nullable=True),
        sa.Column('address_street', sa.Text(), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(100), nullable=True),
        sa.Column('address_postal_code', sa.String(20), nullable=True),
        sa.Column('address_country_code', sa.String(2), nullable=True),
        sa.Column('virtual_event_url', sa.String(500), nullable=True),
        
        # Event Details
        sa.Column('organizer_name', sa.String(255), nullable=True),
        sa.Column('organizer_contact_id', sa.Integer(), nullable=True),
        sa.Column('host_organization_id', sa.Integer(), nullable=True),
        
        # Capacity and Scale
        sa.Column('expected_attendees', sa.Integer(), nullable=True),
        sa.Column('actual_attendees', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_capacity', sa.Integer(), nullable=True),
        
        # Event Properties
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_pattern', sa.String(50), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_invitation', sa.Boolean(), nullable=False, server_default='false'),
        
        # Metadata
        sa.Column('cost', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=True, server_default='USD'),
        sa.Column('dress_code', sa.String(100), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('event_website', sa.String(500), nullable=True),
        
        # Media
        sa.Column('event_image_url', sa.String(500), nullable=True),
        sa.Column('photo_album_url', sa.String(500), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='planned'),
        
        # Audit
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_events_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_events_created_by_user_id_users')),
        sa.ForeignKeyConstraint(['organizer_contact_id'], ['contacts.id'], name=op.f('fk_events_organizer_contact_id_contacts')),
        sa.ForeignKeyConstraint(['host_organization_id'], ['organizations.id'], name=op.f('fk_events_host_organization_id_organizations')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_tenant_id'), 'events', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_start_date'), 'events', ['start_date'], unique=False)
    op.create_index(op.f('ix_events_organizer_contact_id'), 'events', ['organizer_contact_id'], unique=False)
    op.create_index(op.f('ix_events_host_organization_id'), 'events', ['host_organization_id'], unique=False)

    # Create contact_event_attendances table
    op.create_table(
        'contact_event_attendances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        
        # Attendance Details
        sa.Column('attendance_status', sa.String(50), nullable=False, server_default='invited'),
        sa.Column('role_at_event', sa.String(100), nullable=True),
        sa.Column('invitation_method', sa.String(50), nullable=True),
        
        # Interaction Context
        sa.Column('how_we_met_at_event', sa.Text(), nullable=True),
        sa.Column('conversation_highlights', sa.Text(), nullable=True),
        sa.Column('follow_up_needed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        
        # RSVP and Response
        sa.Column('rsvp_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rsvp_response', sa.String(50), nullable=True),
        sa.Column('dietary_restrictions', sa.Text(), nullable=True),
        sa.Column('plus_one_count', sa.Integer(), nullable=False, server_default='0'),
        
        # Relationship Impact
        sa.Column('relationship_strength_before', sa.Integer(), nullable=True),
        sa.Column('relationship_strength_after', sa.Integer(), nullable=True),
        sa.Column('connection_quality', sa.String(50), nullable=True),
        
        # Notes and Memories
        sa.Column('personal_notes', sa.Text(), nullable=True),
        sa.Column('memorable_moments', sa.Text(), nullable=True),
        sa.Column('photos_with_contact', sa.ARRAY(sa.String()), nullable=True),
        
        # Audit
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_contact_event_attendances_contact_id_contacts'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_contact_event_attendances_event_id_events'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'event_id', name='uq_contact_event_attendances_contact_event')
    )
    op.create_index(op.f('ix_contact_event_attendances_id'), 'contact_event_attendances', ['id'], unique=False)
    op.create_index(op.f('ix_contact_event_attendances_contact_id'), 'contact_event_attendances', ['contact_id'], unique=False)
    op.create_index(op.f('ix_contact_event_attendances_event_id'), 'contact_event_attendances', ['event_id'], unique=False)
    op.create_index(op.f('ix_contact_event_attendances_attendance_status'), 'contact_event_attendances', ['attendance_status'], unique=False)

    # Create event_tags table
    op.create_table(
        'event_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sa.String(100), nullable=False),
        sa.Column('tag_color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_event_tags_event_id_events'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_tags_id'), 'event_tags', ['id'], unique=False)
    op.create_index(op.f('ix_event_tags_event_id'), 'event_tags', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_tags_tag_name'), 'event_tags', ['tag_name'], unique=False)

    # Create event_follow_ups table
    op.create_table(
        'event_follow_ups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('follow_up_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('completion_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_event_follow_ups_event_id_events'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_event_follow_ups_contact_id_contacts'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_event_follow_ups_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_follow_ups_id'), 'event_follow_ups', ['id'], unique=False)
    op.create_index(op.f('ix_event_follow_ups_event_id'), 'event_follow_ups', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_follow_ups_contact_id'), 'event_follow_ups', ['contact_id'], unique=False)
    op.create_index(op.f('ix_event_follow_ups_due_date'), 'event_follow_ups', ['due_date'], unique=False)
    op.create_index(op.f('ix_event_follow_ups_status'), 'event_follow_ups', ['status'], unique=False)


def downgrade():
    # Drop event_follow_ups table
    op.drop_index(op.f('ix_event_follow_ups_status'), table_name='event_follow_ups')
    op.drop_index(op.f('ix_event_follow_ups_due_date'), table_name='event_follow_ups')
    op.drop_index(op.f('ix_event_follow_ups_contact_id'), table_name='event_follow_ups')
    op.drop_index(op.f('ix_event_follow_ups_event_id'), table_name='event_follow_ups')
    op.drop_index(op.f('ix_event_follow_ups_id'), table_name='event_follow_ups')
    op.drop_table('event_follow_ups')
    
    # Drop event_tags table
    op.drop_index(op.f('ix_event_tags_tag_name'), table_name='event_tags')
    op.drop_index(op.f('ix_event_tags_event_id'), table_name='event_tags')
    op.drop_index(op.f('ix_event_tags_id'), table_name='event_tags')
    op.drop_table('event_tags')
    
    # Drop contact_event_attendances table
    op.drop_index(op.f('ix_contact_event_attendances_attendance_status'), table_name='contact_event_attendances')
    op.drop_index(op.f('ix_contact_event_attendances_event_id'), table_name='contact_event_attendances')
    op.drop_index(op.f('ix_contact_event_attendances_contact_id'), table_name='contact_event_attendances')
    op.drop_index(op.f('ix_contact_event_attendances_id'), table_name='contact_event_attendances')
    op.drop_table('contact_event_attendances')
    
    # Drop events table
    op.drop_index(op.f('ix_events_host_organization_id'), table_name='events')
    op.drop_index(op.f('ix_events_organizer_contact_id'), table_name='events')
    op.drop_index(op.f('ix_events_start_date'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_index(op.f('ix_events_tenant_id'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')
