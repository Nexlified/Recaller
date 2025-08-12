"""create event_follow_ups table

Revision ID: 008_create_event_follow_ups
Revises: 007_create_event_tags
Create Date: 2025-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_create_event_follow_ups'
down_revision = '007_create_event_tags'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_follow_ups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        
        sa.Column('follow_up_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True, default='medium'),
        sa.Column('status', sa.String(50), nullable=True, default='pending'),
        
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('completion_notes', sa.Text(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name=op.f('fk_event_follow_ups_event_id_events')),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE', name=op.f('fk_event_follow_ups_contact_id_contacts')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_event_follow_ups_created_by_user_id_users')),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(op.f('ix_event_follow_ups_id'), 'event_follow_ups', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_event_follow_ups_id'), table_name='event_follow_ups')
    op.drop_table('event_follow_ups')