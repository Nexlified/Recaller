"""Create shared activities tables

Revision ID: 021_create_shared_activities
Revises: 020_create_work_experience
Create Date: 2025-01-15 19:18:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '021_create_shared_activities'
down_revision = '020_create_work_experience'
branch_labels = None
depends_on = None


def upgrade():
    # Create shared_activities table
    op.create_table(
        'shared_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        
        # Activity Details
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(500), nullable=True),
        
        # Timing
        sa.Column('activity_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        
        # Financial
        sa.Column('cost_per_person', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        
        # Quality & Memory
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('photos', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('memorable_moments', sa.Text(), nullable=True),
        
        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='planned'),
        sa.Column('is_private', sa.Boolean(), nullable=False, server_default='false'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_shared_activities_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_shared_activities_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 10)', name='check_quality_rating_range')
    )
    
    # Create shared_activity_participants table
    op.create_table(
        'shared_activity_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Participation Details
        sa.Column('participation_level', sa.String(20), nullable=False),
        sa.Column('attendance_status', sa.String(20), nullable=False),
        
        # Individual Notes
        sa.Column('participant_notes', sa.Text(), nullable=True),
        sa.Column('satisfaction_rating', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.ForeignKeyConstraint(['activity_id'], ['shared_activities.id'], name=op.f('fk_shared_activity_participants_activity_id_shared_activities'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_shared_activity_participants_contact_id_contacts'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_shared_activity_participants_tenant_id_tenants')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('activity_id', 'contact_id', name='uq_activity_participant'),
        sa.CheckConstraint('satisfaction_rating IS NULL OR (satisfaction_rating >= 1 AND satisfaction_rating <= 10)', name='check_satisfaction_rating_range')
    )
    
    # Create indexes for shared_activities
    op.create_index(op.f('ix_shared_activities_id'), 'shared_activities', ['id'], unique=False)
    op.create_index(op.f('ix_shared_activities_tenant_id'), 'shared_activities', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_shared_activities_created_by_user_id'), 'shared_activities', ['created_by_user_id'], unique=False)
    op.create_index(op.f('ix_shared_activities_activity_type'), 'shared_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_shared_activities_activity_date'), 'shared_activities', ['activity_date'], unique=False)
    op.create_index(op.f('ix_shared_activities_status'), 'shared_activities', ['status'], unique=False)
    op.create_index(op.f('ix_shared_activities_quality_rating'), 'shared_activities', ['quality_rating'], unique=False)
    
    # Create indexes for shared_activity_participants
    op.create_index(op.f('ix_shared_activity_participants_id'), 'shared_activity_participants', ['id'], unique=False)
    op.create_index(op.f('ix_shared_activity_participants_activity_id'), 'shared_activity_participants', ['activity_id'], unique=False)
    op.create_index(op.f('ix_shared_activity_participants_contact_id'), 'shared_activity_participants', ['contact_id'], unique=False)
    op.create_index(op.f('ix_shared_activity_participants_tenant_id'), 'shared_activity_participants', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_shared_activity_participants_participation_level'), 'shared_activity_participants', ['participation_level'], unique=False)
    op.create_index(op.f('ix_shared_activity_participants_attendance_status'), 'shared_activity_participants', ['attendance_status'], unique=False)
    
    # Composite indexes for common queries
    op.create_index('ix_shared_activities_tenant_date', 'shared_activities', ['tenant_id', 'activity_date'], unique=False)
    op.create_index('ix_shared_activities_user_date', 'shared_activities', ['created_by_user_id', 'activity_date'], unique=False)
    op.create_index('ix_shared_activity_participants_contact_status', 'shared_activity_participants', ['contact_id', 'attendance_status'], unique=False)


def downgrade():
    # Drop indexes for shared_activity_participants
    op.drop_index('ix_shared_activity_participants_contact_status', table_name='shared_activity_participants')
    op.drop_index(op.f('ix_shared_activity_participants_attendance_status'), table_name='shared_activity_participants')
    op.drop_index(op.f('ix_shared_activity_participants_participation_level'), table_name='shared_activity_participants')
    op.drop_index(op.f('ix_shared_activity_participants_tenant_id'), table_name='shared_activity_participants')
    op.drop_index(op.f('ix_shared_activity_participants_contact_id'), table_name='shared_activity_participants')
    op.drop_index(op.f('ix_shared_activity_participants_activity_id'), table_name='shared_activity_participants')
    op.drop_index(op.f('ix_shared_activity_participants_id'), table_name='shared_activity_participants')
    
    # Drop indexes for shared_activities
    op.drop_index('ix_shared_activities_user_date', table_name='shared_activities')
    op.drop_index('ix_shared_activities_tenant_date', table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_quality_rating'), table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_status'), table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_activity_date'), table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_activity_type'), table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_created_by_user_id'), table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_tenant_id'), table_name='shared_activities')
    op.drop_index(op.f('ix_shared_activities_id'), table_name='shared_activities')
    
    # Drop tables
    op.drop_table('shared_activity_participants')
    op.drop_table('shared_activities')