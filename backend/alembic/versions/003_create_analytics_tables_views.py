"""create analytics tables and views

Revision ID: 003
Revises: 002
Create Date: 2025-08-11 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Create networking_insights table
    op.create_table(
        'networking_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(50), nullable=False),
        sa.Column('insight_category', sa.String(50), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True, default='medium'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metrics', JSONB(), nullable=True),
        sa.Column('actionable_recommendations', ARRAY(sa.Text()), nullable=True, default=[]),
        sa.Column('confidence_score', sa.Numeric(3,2), nullable=True),
        sa.Column('data_sources', ARRAY(sa.Text()), nullable=True, default=[]),
        sa.Column('calculation_method', sa.String(50), nullable=True),
        sa.Column('insight_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_networking_insights_tenant_id_tenants'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_networking_insights_user_id_users'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_networking_insights_id'), 'networking_insights', ['id'], unique=False)
    op.create_index(op.f('ix_networking_insights_tenant_id'), 'networking_insights', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_networking_insights_insight_type'), 'networking_insights', ['insight_type'], unique=False)
    op.create_index(op.f('ix_networking_insights_insight_date'), 'networking_insights', ['insight_date'], unique=False)

    # Create daily_network_metrics table
    op.create_table(
        'daily_network_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('total_contacts', sa.Integer(), nullable=True),
        sa.Column('active_contacts', sa.Integer(), nullable=True),
        sa.Column('new_contacts_added', sa.Integer(), nullable=True),
        sa.Column('contacts_archived', sa.Integer(), nullable=True),
        sa.Column('strong_relationships', sa.Integer(), nullable=True),
        sa.Column('moderate_relationships', sa.Integer(), nullable=True),
        sa.Column('weak_relationships', sa.Integer(), nullable=True),
        sa.Column('avg_connection_strength', sa.Numeric(3,2), nullable=True),
        sa.Column('total_interactions', sa.Integer(), nullable=True),
        sa.Column('new_interactions', sa.Integer(), nullable=True),
        sa.Column('avg_interaction_quality', sa.Numeric(3,2), nullable=True),
        sa.Column('interaction_types', JSONB(), nullable=True),
        sa.Column('overdue_follow_ups', sa.Integer(), nullable=True),
        sa.Column('completed_follow_ups', sa.Integer(), nullable=True),
        sa.Column('pending_follow_ups', sa.Integer(), nullable=True),
        sa.Column('network_growth_rate', sa.Numeric(5,4), nullable=True),
        sa.Column('engagement_rate', sa.Numeric(5,4), nullable=True),
        sa.Column('response_rate', sa.Numeric(5,4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_daily_network_metrics_tenant_id_tenants'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'metric_date', name='uq_daily_network_metrics_tenant_date')
    )
    op.create_index(op.f('ix_daily_network_metrics_id'), 'daily_network_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_daily_network_metrics_metric_date'), 'daily_network_metrics', ['metric_date'], unique=False)

    # Create Contact Analytics Summary Materialized View
    op.execute("""
        CREATE MATERIALIZED VIEW contact_analytics_summary AS
        SELECT 
            tenant_id,
            COUNT(*) as total_contacts,
            COUNT(CASE WHEN is_active = true THEN 1 END) as active_contacts,
            COUNT(CASE WHEN connection_strength >= 7 THEN 1 END) as strong_relationships,
            COUNT(CASE WHEN connection_strength BETWEEN 4 AND 6 THEN 1 END) as moderate_relationships,
            COUNT(CASE WHEN connection_strength <= 3 THEN 1 END) as weak_relationships,
            AVG(connection_strength) as avg_connection_strength,
            AVG(total_interactions) as avg_interactions_per_contact,
            COUNT(CASE WHEN last_meaningful_interaction > CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as recent_interactions,
            COUNT(CASE WHEN next_suggested_contact_date < CURRENT_DATE THEN 1 END) as overdue_follow_ups,
            COUNT(CASE WHEN follow_up_urgency = 'high' THEN 1 END) as high_priority_follow_ups
        FROM contacts 
        GROUP BY tenant_id;
    """)

    # Create Interaction Analytics View
    op.execute("""
        CREATE VIEW interaction_analytics AS
        SELECT 
            ci.contact_id,
            c.tenant_id,
            COUNT(*) as total_interactions,
            COUNT(CASE WHEN ci.interaction_type = 'meeting' THEN 1 END) as in_person_meetings,
            COUNT(CASE WHEN ci.interaction_type = 'call' THEN 1 END) as phone_calls,
            COUNT(CASE WHEN ci.interaction_type = 'email' THEN 1 END) as emails,
            COUNT(CASE WHEN ci.interaction_type = 'text' THEN 1 END) as text_messages,
            AVG(ci.interaction_quality) as avg_interaction_quality,
            AVG(ci.duration_minutes) as avg_interaction_duration,
            MAX(ci.interaction_date) as last_interaction_date,
            COUNT(CASE WHEN ci.interaction_date > CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as interactions_last_30_days,
            COUNT(CASE WHEN ci.initiated_by = 'me' THEN 1 END) as interactions_initiated_by_user,
            COUNT(CASE WHEN ci.initiated_by = 'them' THEN 1 END) as interactions_initiated_by_contact
        FROM contact_interactions ci
        JOIN contacts c ON ci.contact_id = c.id
        GROUP BY ci.contact_id, c.tenant_id;
    """)

    # Create Organization Network Analytics View
    op.execute("""
        CREATE VIEW organization_network_analytics AS
        SELECT 
            o.id as organization_id,
            o.name as organization_name,
            o.organization_type,
            o.industry,
            o.tenant_id,
            COUNT(CASE WHEN c.current_organization_id = o.id THEN 1 END) as current_contacts,
            COUNT(CASE WHEN c.alma_mater_id = o.id THEN 1 END) as alumni_contacts,
            AVG(CASE WHEN c.current_organization_id = o.id THEN c.connection_strength END) as avg_connection_strength,
            COUNT(CASE WHEN c.current_organization_id = o.id AND c.networking_value = 'high' THEN 1 END) as high_value_contacts,
            SUM(CASE WHEN c.current_organization_id = o.id THEN c.total_interactions ELSE 0 END) as total_interactions
        FROM organizations o
        LEFT JOIN contacts c ON (c.current_organization_id = o.id OR c.alma_mater_id = o.id)
        GROUP BY o.id, o.name, o.organization_type, o.industry, o.tenant_id;
    """)

    # Create Social Group Analytics View
    op.execute("""
        CREATE VIEW social_group_analytics AS
        SELECT 
            sg.id as group_id,
            sg.name as group_name,
            sg.group_type,
            sg.tenant_id,
            sg.member_count,
            COUNT(csgm.contact_id) as active_members,
            AVG(c.connection_strength) as avg_member_connection_strength,
            COUNT(sga.id) as total_activities,
            AVG(sga.actual_attendees) as avg_activity_attendance,
            MAX(sga.scheduled_date) as last_activity_date
        FROM social_groups sg
        LEFT JOIN contact_social_group_memberships csgm ON sg.id = csgm.social_group_id AND csgm.membership_status = 'active'
        LEFT JOIN contacts c ON csgm.contact_id = c.id
        LEFT JOIN social_group_activities sga ON sg.id = sga.social_group_id
        GROUP BY sg.id, sg.name, sg.group_type, sg.tenant_id, sg.member_count;
    """)

    # Create indexes for materialized view
    op.execute("CREATE UNIQUE INDEX ON contact_analytics_summary (tenant_id);")

def downgrade():
    # Drop views and materialized views
    op.execute("DROP VIEW IF EXISTS social_group_analytics;")
    op.execute("DROP VIEW IF EXISTS organization_network_analytics;")
    op.execute("DROP VIEW IF EXISTS interaction_analytics;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS contact_analytics_summary;")
    
    # Drop tables
    op.drop_table('daily_network_metrics')
    op.drop_table('networking_insights')