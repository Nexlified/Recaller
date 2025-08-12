"""create events table

Revision ID: 005_create_events
Revises: 004_create_organizations
Create Date: 2025-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_create_events'
down_revision = '004_create_organizations'
branch_labels = None
depends_on = None


def upgrade():
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
        sa.Column('timezone', sa.String(50), nullable=True, default='UTC'),
        
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
        sa.Column('actual_attendees', sa.Integer(), nullable=True, default=0),
        sa.Column('max_capacity', sa.Integer(), nullable=True),
        
        # Event Properties
        sa.Column('is_recurring', sa.Boolean(), nullable=True, default=False),
        sa.Column('recurrence_pattern', sa.String(50), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('requires_invitation', sa.Boolean(), nullable=True, default=False),
        
        # Metadata
        sa.Column('cost', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=True, default='USD'),
        sa.Column('dress_code', sa.String(100), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('event_website', sa.String(500), nullable=True),
        
        # Media
        sa.Column('event_image_url', sa.String(500), nullable=True),
        sa.Column('photo_album_url', sa.String(500), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), nullable=True, default='planned'),
        
        # Audit
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_events_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_events_created_by_user_id_users')),
        sa.ForeignKeyConstraint(['organizer_contact_id'], ['contacts.id'], name=op.f('fk_events_organizer_contact_id_contacts')),
        sa.ForeignKeyConstraint(['host_organization_id'], ['organizations.id'], name=op.f('fk_events_host_organization_id_organizations')),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes as specified in the schema
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index('idx_events_tenant', 'events', ['tenant_id'], unique=False)
    op.create_index('idx_events_type', 'events', ['event_type'], unique=False)
    op.create_index('idx_events_date', 'events', ['start_date'], unique=False)
    op.create_index('idx_events_organizer', 'events', ['organizer_contact_id'], unique=False)
    op.create_index('idx_events_organization', 'events', ['host_organization_id'], unique=False)


def downgrade():
    op.drop_index('idx_events_organization', table_name='events')
    op.drop_index('idx_events_organizer', table_name='events')
    op.drop_index('idx_events_date', table_name='events')
    op.drop_index('idx_events_type', table_name='events')
    op.drop_index('idx_events_tenant', table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')