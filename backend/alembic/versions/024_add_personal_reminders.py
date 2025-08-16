"""Add personal reminders table

Revision ID: 024_add_personal_reminders
Revises: 023_configuration_import_system
Create Date: 2025-01-15 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '024_add_personal_reminders'
down_revision = '023_configuration_import_system'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create personal_reminders table
    op.create_table(
        'personal_reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reminder_type', sa.String(50), nullable=False),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, default=True),
        sa.Column('reminder_preferences', sa.JSON(), nullable=False, default={}),
        sa.Column('notification_methods', sa.JSON(), nullable=False, default={}),
        sa.Column('importance_level', sa.Integer(), nullable=False, default=3),
        sa.Column('last_celebrated_year', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_personal_reminders_id', 'personal_reminders', ['id'])
    op.create_index('ix_personal_reminders_tenant_id', 'personal_reminders', ['tenant_id'])
    op.create_index('ix_personal_reminders_user_id', 'personal_reminders', ['user_id'])
    op.create_index('ix_personal_reminders_contact_id', 'personal_reminders', ['contact_id'])
    op.create_index('ix_personal_reminders_event_date', 'personal_reminders', ['event_date'])
    op.create_index('ix_personal_reminders_reminder_type', 'personal_reminders', ['reminder_type'])
    op.create_index('ix_personal_reminders_is_active', 'personal_reminders', ['is_active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_personal_reminders_is_active', 'personal_reminders')
    op.drop_index('ix_personal_reminders_reminder_type', 'personal_reminders')
    op.drop_index('ix_personal_reminders_event_date', 'personal_reminders')
    op.drop_index('ix_personal_reminders_contact_id', 'personal_reminders')
    op.drop_index('ix_personal_reminders_user_id', 'personal_reminders')
    op.drop_index('ix_personal_reminders_tenant_id', 'personal_reminders')
    op.drop_index('ix_personal_reminders_id', 'personal_reminders')
    
    # Drop table
    op.drop_table('personal_reminders')