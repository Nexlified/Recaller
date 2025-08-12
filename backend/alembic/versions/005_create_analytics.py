"""Create analytics tables and views

Revision ID: 005_create_analytics
Revises: 004_create_social_groups
Create Date: 2025-08-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '005_create_analytics'
down_revision = '004_create_social_groups'
branch_labels = None
depends_on = None

def upgrade():
    # Create contact_analytics_summary table
    op.create_table(
        'contact_analytics_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('total_interactions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_interaction_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interaction_frequency_score', sa.Float(), nullable=True),
        sa.Column('relationship_strength_score', sa.Float(), nullable=True),
        sa.Column('communication_patterns', JSONB(), nullable=True),
        sa.Column('network_influence_score', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_contact_analytics_summary_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_contact_analytics_summary_contact_id_contacts'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', name='uq_contact_analytics_summary_contact')
    )
    op.create_index(op.f('ix_contact_analytics_summary_id'), 'contact_analytics_summary', ['id'], unique=False)
    op.create_index(op.f('ix_contact_analytics_summary_tenant_id'), 'contact_analytics_summary', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_contact_analytics_summary_contact_id'), 'contact_analytics_summary', ['contact_id'], unique=False)

    # Create interaction_analytics table
    op.create_table(
        'interaction_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('interaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('response_time_hours', sa.Float(), nullable=True),
        sa.Column('initiated_by_user', sa.Boolean(), nullable=False),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_interaction_analytics_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_interaction_analytics_user_id_users')),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name=op.f('fk_interaction_analytics_contact_id_contacts'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interaction_analytics_id'), 'interaction_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_interaction_analytics_tenant_id'), 'interaction_analytics', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_interaction_analytics_user_id'), 'interaction_analytics', ['user_id'], unique=False)
    op.create_index(op.f('ix_interaction_analytics_contact_id'), 'interaction_analytics', ['contact_id'], unique=False)
    op.create_index(op.f('ix_interaction_analytics_interaction_date'), 'interaction_analytics', ['interaction_date'], unique=False)

    # Create organization_network_analytics table
    op.create_table(
        'organization_network_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('total_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_relationship_strength', sa.Float(), nullable=True),
        sa.Column('industry_influence_score', sa.Float(), nullable=True),
        sa.Column('network_reach_score', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_organization_network_analytics_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_organization_network_analytics_organization_id_organizations'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', name='uq_organization_network_analytics_organization')
    )
    op.create_index(op.f('ix_organization_network_analytics_id'), 'organization_network_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_organization_network_analytics_tenant_id'), 'organization_network_analytics', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_organization_network_analytics_organization_id'), 'organization_network_analytics', ['organization_id'], unique=False)

    # Create social_group_analytics table
    op.create_table(
        'social_group_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('social_group_id', sa.Integer(), nullable=False),
        sa.Column('total_members', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_members', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_activities', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_attendance_rate', sa.Float(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_social_group_analytics_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['social_group_id'], ['social_groups.id'], name=op.f('fk_social_group_analytics_social_group_id_social_groups'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('social_group_id', name='uq_social_group_analytics_social_group')
    )
    op.create_index(op.f('ix_social_group_analytics_id'), 'social_group_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_social_group_analytics_tenant_id'), 'social_group_analytics', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_social_group_analytics_social_group_id'), 'social_group_analytics', ['social_group_id'], unique=False)

    # Create networking_insights table
    op.create_table(
        'networking_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(50), nullable=False),
        sa.Column('insight_category', sa.String(50), nullable=True),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metrics', JSONB(), nullable=True),
        sa.Column('actionable_recommendations', JSONB(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_networking_insights_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_networking_insights_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_networking_insights_id'), 'networking_insights', ['id'], unique=False)
    op.create_index(op.f('ix_networking_insights_tenant_id'), 'networking_insights', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_networking_insights_user_id'), 'networking_insights', ['user_id'], unique=False)
    op.create_index(op.f('ix_networking_insights_insight_type'), 'networking_insights', ['insight_type'], unique=False)

    # Create daily_network_metrics table
    op.create_table(
        'daily_network_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('new_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interactions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('outreach_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('response_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('network_growth_rate', sa.Float(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_daily_network_metrics_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_daily_network_metrics_user_id_users')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_daily_network_metrics_user_date')
    )
    op.create_index(op.f('ix_daily_network_metrics_id'), 'daily_network_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_daily_network_metrics_tenant_id'), 'daily_network_metrics', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_daily_network_metrics_user_id'), 'daily_network_metrics', ['user_id'], unique=False)
    op.create_index(op.f('ix_daily_network_metrics_date'), 'daily_network_metrics', ['date'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_daily_network_metrics_date'), table_name='daily_network_metrics')
    op.drop_index(op.f('ix_daily_network_metrics_user_id'), table_name='daily_network_metrics')
    op.drop_index(op.f('ix_daily_network_metrics_tenant_id'), table_name='daily_network_metrics')
    op.drop_index(op.f('ix_daily_network_metrics_id'), table_name='daily_network_metrics')
    op.drop_table('daily_network_metrics')
    
    op.drop_index(op.f('ix_networking_insights_insight_type'), table_name='networking_insights')
    op.drop_index(op.f('ix_networking_insights_user_id'), table_name='networking_insights')
    op.drop_index(op.f('ix_networking_insights_tenant_id'), table_name='networking_insights')
    op.drop_index(op.f('ix_networking_insights_id'), table_name='networking_insights')
    op.drop_table('networking_insights')
    
    op.drop_index(op.f('ix_social_group_analytics_social_group_id'), table_name='social_group_analytics')
    op.drop_index(op.f('ix_social_group_analytics_tenant_id'), table_name='social_group_analytics')
    op.drop_index(op.f('ix_social_group_analytics_id'), table_name='social_group_analytics')
    op.drop_table('social_group_analytics')
    
    op.drop_index(op.f('ix_organization_network_analytics_organization_id'), table_name='organization_network_analytics')
    op.drop_index(op.f('ix_organization_network_analytics_tenant_id'), table_name='organization_network_analytics')
    op.drop_index(op.f('ix_organization_network_analytics_id'), table_name='organization_network_analytics')
    op.drop_table('organization_network_analytics')
    
    op.drop_index(op.f('ix_interaction_analytics_interaction_date'), table_name='interaction_analytics')
    op.drop_index(op.f('ix_interaction_analytics_contact_id'), table_name='interaction_analytics')
    op.drop_index(op.f('ix_interaction_analytics_user_id'), table_name='interaction_analytics')
    op.drop_index(op.f('ix_interaction_analytics_tenant_id'), table_name='interaction_analytics')
    op.drop_index(op.f('ix_interaction_analytics_id'), table_name='interaction_analytics')
    op.drop_table('interaction_analytics')
    
    op.drop_index(op.f('ix_contact_analytics_summary_contact_id'), table_name='contact_analytics_summary')
    op.drop_index(op.f('ix_contact_analytics_summary_tenant_id'), table_name='contact_analytics_summary')
    op.drop_index(op.f('ix_contact_analytics_summary_id'), table_name='contact_analytics_summary')
    op.drop_table('contact_analytics_summary')
