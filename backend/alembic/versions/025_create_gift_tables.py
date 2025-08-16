"""Create gifts and gift_ideas tables

Revision ID: 025_create_gift_tables
Revises: 024_add_personal_reminders
Create Date: 2025-01-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '025_create_gift_tables'
down_revision = '024_add_personal_reminders'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create gifts table
    op.create_table(
        'gifts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        
        # Basic Information
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        
        # Recipient Information
        sa.Column('recipient_contact_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=True),
        sa.Column('recipient_name', sa.String(255), nullable=True),
        
        # Occasion and Timing
        sa.Column('occasion', sa.String(100), nullable=True),
        sa.Column('occasion_date', sa.Date(), nullable=True),
        
        # Financial Information
        sa.Column('budget_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('actual_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        
        # Status and Priority
        sa.Column('status', sa.String(20), nullable=False, default='idea'),
        sa.Column('priority', sa.Integer(), nullable=False, default=2),
        
        # Purchase Information
        sa.Column('store_name', sa.String(255), nullable=True),
        sa.Column('purchase_url', sa.Text(), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        
        # Gift Details (JSON format)
        sa.Column('gift_details', sa.JSON().with_variant(postgresql.JSONB, "postgresql"), nullable=False, default={}),
        
        # Tracking Information
        sa.Column('tracking_number', sa.String(255), nullable=True),
        sa.Column('delivery_date', sa.Date(), nullable=True),
        
        # Notes and References
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        
        # Reminders and Notifications (JSON format)
        sa.Column('reminder_dates', sa.JSON().with_variant(postgresql.JSONB, "postgresql"), nullable=False, default={}),
        
        # Integration References
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_surprise', sa.Boolean(), nullable=False, default=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create gift_ideas table
    op.create_table(
        'gift_ideas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        
        # Basic Information
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        
        # Target Information
        sa.Column('target_contact_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=True),
        sa.Column('target_demographic', sa.String(100), nullable=True),
        
        # Occasion Context
        sa.Column('suitable_occasions', sa.JSON().with_variant(postgresql.JSONB, "postgresql"), nullable=False, default=[]),
        
        # Financial Information
        sa.Column('price_range_min', sa.Numeric(10, 2), nullable=True),
        sa.Column('price_range_max', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        
        # Idea Details (JSON format)
        sa.Column('idea_details', sa.JSON().with_variant(postgresql.JSONB, "postgresql"), nullable=False, default={}),
        
        # Sources and References
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        
        # Rating and Feedback
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Tracking
        sa.Column('times_gifted', sa.Integer(), nullable=False, default=0),
        sa.Column('last_gifted_date', sa.Date(), nullable=True),
        
        # Tags for searchability (JSON format)
        sa.Column('tags', sa.JSON().with_variant(postgresql.JSONB, "postgresql"), nullable=False, default=[]),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, default=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for gifts table - optimized for analytics and quick queries
    
    # Primary indexes for basic queries
    op.create_index('ix_gifts_id', 'gifts', ['id'])
    op.create_index('ix_gifts_tenant_id', 'gifts', ['tenant_id'])
    op.create_index('ix_gifts_user_id', 'gifts', ['user_id'])
    op.create_index('ix_gifts_recipient_contact_id', 'gifts', ['recipient_contact_id'])
    
    # Category and occasion indexes for filtering
    op.create_index('ix_gifts_category', 'gifts', ['category'])
    op.create_index('ix_gifts_occasion', 'gifts', ['occasion'])
    op.create_index('ix_gifts_occasion_date', 'gifts', ['occasion_date'])
    
    # Status and priority indexes for workflow management
    op.create_index('ix_gifts_status', 'gifts', ['status'])
    op.create_index('ix_gifts_priority', 'gifts', ['priority'])
    op.create_index('ix_gifts_is_active', 'gifts', ['is_active'])
    
    # Composite indexes for common query patterns
    op.create_index('ix_gifts_tenant_user_active', 'gifts', ['tenant_id', 'user_id', 'is_active'])
    op.create_index('ix_gifts_tenant_user_status', 'gifts', ['tenant_id', 'user_id', 'status'])
    op.create_index('ix_gifts_user_occasion_date', 'gifts', ['user_id', 'occasion_date'])
    op.create_index('ix_gifts_recipient_occasion', 'gifts', ['recipient_contact_id', 'occasion'])
    
    # Analytics-focused indexes
    op.create_index('ix_gifts_category_status', 'gifts', ['category', 'status'])
    op.create_index('ix_gifts_occasion_status', 'gifts', ['occasion', 'status'])
    op.create_index('ix_gifts_created_at', 'gifts', ['created_at'])
    
    # Create indexes for gift_ideas table
    
    # Primary indexes for basic queries
    op.create_index('ix_gift_ideas_id', 'gift_ideas', ['id'])
    op.create_index('ix_gift_ideas_tenant_id', 'gift_ideas', ['tenant_id'])
    op.create_index('ix_gift_ideas_user_id', 'gift_ideas', ['user_id'])
    op.create_index('ix_gift_ideas_target_contact_id', 'gift_ideas', ['target_contact_id'])
    
    # Category and filtering indexes
    op.create_index('ix_gift_ideas_category', 'gift_ideas', ['category'])
    op.create_index('ix_gift_ideas_is_active', 'gift_ideas', ['is_active'])
    op.create_index('ix_gift_ideas_is_favorite', 'gift_ideas', ['is_favorite'])
    
    # Rating and tracking indexes
    op.create_index('ix_gift_ideas_rating', 'gift_ideas', ['rating'])
    op.create_index('ix_gift_ideas_times_gifted', 'gift_ideas', ['times_gifted'])
    
    # Composite indexes for common query patterns
    op.create_index('ix_gift_ideas_tenant_user_active', 'gift_ideas', ['tenant_id', 'user_id', 'is_active'])
    op.create_index('ix_gift_ideas_user_favorite', 'gift_ideas', ['user_id', 'is_favorite'])
    op.create_index('ix_gift_ideas_target_category', 'gift_ideas', ['target_contact_id', 'category'])
    
    # Analytics-focused indexes  
    op.create_index('ix_gift_ideas_category_rating', 'gift_ideas', ['category', 'rating'])
    op.create_index('ix_gift_ideas_created_at', 'gift_ideas', ['created_at'])


def downgrade() -> None:
    # Drop indexes for gift_ideas table
    op.drop_index('ix_gift_ideas_created_at', 'gift_ideas')
    op.drop_index('ix_gift_ideas_category_rating', 'gift_ideas')
    op.drop_index('ix_gift_ideas_target_category', 'gift_ideas')
    op.drop_index('ix_gift_ideas_user_favorite', 'gift_ideas')
    op.drop_index('ix_gift_ideas_tenant_user_active', 'gift_ideas')
    op.drop_index('ix_gift_ideas_times_gifted', 'gift_ideas')
    op.drop_index('ix_gift_ideas_rating', 'gift_ideas')
    op.drop_index('ix_gift_ideas_is_favorite', 'gift_ideas')
    op.drop_index('ix_gift_ideas_is_active', 'gift_ideas')
    op.drop_index('ix_gift_ideas_category', 'gift_ideas')
    op.drop_index('ix_gift_ideas_target_contact_id', 'gift_ideas')
    op.drop_index('ix_gift_ideas_user_id', 'gift_ideas')
    op.drop_index('ix_gift_ideas_tenant_id', 'gift_ideas')
    op.drop_index('ix_gift_ideas_id', 'gift_ideas')
    
    # Drop indexes for gifts table
    op.drop_index('ix_gifts_created_at', 'gifts')
    op.drop_index('ix_gifts_occasion_status', 'gifts')
    op.drop_index('ix_gifts_category_status', 'gifts')
    op.drop_index('ix_gifts_recipient_occasion', 'gifts')
    op.drop_index('ix_gifts_user_occasion_date', 'gifts')
    op.drop_index('ix_gifts_tenant_user_status', 'gifts')
    op.drop_index('ix_gifts_tenant_user_active', 'gifts')
    op.drop_index('ix_gifts_is_active', 'gifts')
    op.drop_index('ix_gifts_priority', 'gifts')
    op.drop_index('ix_gifts_status', 'gifts')
    op.drop_index('ix_gifts_occasion_date', 'gifts')
    op.drop_index('ix_gifts_occasion', 'gifts')
    op.drop_index('ix_gifts_category', 'gifts')
    op.drop_index('ix_gifts_recipient_contact_id', 'gifts')
    op.drop_index('ix_gifts_user_id', 'gifts')
    op.drop_index('ix_gifts_tenant_id', 'gifts')
    op.drop_index('ix_gifts_id', 'gifts')
    
    # Drop tables
    op.drop_table('gift_ideas')
    op.drop_table('gifts')