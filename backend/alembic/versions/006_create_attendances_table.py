"""create contact_event_attendances table

Revision ID: 006_create_attendances
Revises: 005_create_events
Create Date: 2025-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_create_attendances'
down_revision = '005_create_events'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'contact_event_attendances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        
        # Attendance Details
        sa.Column('attendance_status', sa.String(50), nullable=True, default='invited'),
        sa.Column('role_at_event', sa.String(100), nullable=True),
        sa.Column('invitation_method', sa.String(50), nullable=True),
        
        # Interaction Context
        sa.Column('how_we_met_at_event', sa.Text(), nullable=True),
        sa.Column('conversation_highlights', sa.Text(), nullable=True),
        sa.Column('follow_up_needed', sa.Boolean(), nullable=True, default=False),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        
        # RSVP and Response
        sa.Column('rsvp_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rsvp_response', sa.String(50), nullable=True),
        sa.Column('dietary_restrictions', sa.Text(), nullable=True),
        sa.Column('plus_one_count', sa.Integer(), nullable=True, default=0),
        
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
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE', name=op.f('fk_attendances_contact_id_contacts')),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name=op.f('fk_attendances_event_id_events')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'event_id', name='uq_contact_event_attendance')
    )
    
    # Create indexes as specified in the schema
    op.create_index(op.f('ix_attendances_id'), 'contact_event_attendances', ['id'], unique=False)
    op.create_index('idx_attendance_contact', 'contact_event_attendances', ['contact_id'], unique=False)
    op.create_index('idx_attendance_event', 'contact_event_attendances', ['event_id'], unique=False)
    op.create_index('idx_attendance_status', 'contact_event_attendances', ['attendance_status'], unique=False)


def downgrade():
    op.drop_index('idx_attendance_status', table_name='contact_event_attendances')
    op.drop_index('idx_attendance_event', table_name='contact_event_attendances')
    op.drop_index('idx_attendance_contact', table_name='contact_event_attendances')
    op.drop_index(op.f('ix_attendances_id'), table_name='contact_event_attendances')
    op.drop_table('contact_event_attendances')