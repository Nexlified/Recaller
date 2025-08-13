from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY, Date, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class NetworkingInsight(Base):
    __tablename__ = "networking_insights"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Insight Metadata
    insight_type = Column(String(50), nullable=False)  # network_growth, relationship_health, engagement_pattern, opportunity
    insight_category = Column(String(50))  # networking, relationship_maintenance, growth_opportunity
    priority = Column(String(20), default='medium')  # high, medium, low
    
    # Insight Content
    title = Column(String(255), nullable=False)
    description = Column(Text)
    metrics = Column(JSONB)  # Supporting data and calculations
    actionable_recommendations = Column(ARRAY(Text), default=list)
    
    # AI/Analytics Metadata
    confidence_score = Column(Numeric(3,2))
    data_sources = Column(ARRAY(Text), default=list)
    calculation_method = Column(String(50))
    
    # Lifecycle
    insight_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    status = Column(String(20), default='active')  # active, dismissed, acted_upon
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="networking_insights")
    user = relationship(lambda: User, back_populates="networking_insights")

# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User

class DailyNetworkMetric(Base):
    __tablename__ = "daily_network_metrics"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    
    # Contact Metrics
    total_contacts = Column(Integer)
    active_contacts = Column(Integer)
    new_contacts_added = Column(Integer)
    contacts_archived = Column(Integer)
    
    # Relationship Strength Distribution
    strong_relationships = Column(Integer)  # 7-10
    moderate_relationships = Column(Integer)  # 4-6
    weak_relationships = Column(Integer)  # 1-3
    avg_connection_strength = Column(Numeric(3,2))
    
    # Interaction Metrics
    total_interactions = Column(Integer)
    new_interactions = Column(Integer)
    avg_interaction_quality = Column(Numeric(3,2))
    interaction_types = Column(JSONB)  # Breakdown by type
    
    # Follow-up Metrics
    overdue_follow_ups = Column(Integer)
    completed_follow_ups = Column(Integer)
    pending_follow_ups = Column(Integer)
    
    # Network Growth
    network_growth_rate = Column(Numeric(5,4))  # Daily growth rate
    engagement_rate = Column(Numeric(5,4))  # Interactions per contact
    response_rate = Column(Numeric(5,4))  # Contact response rate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="daily_metrics")
    
    # Constraints
    __table_args__ = (
        {'schema': None},  # Default schema
    )

# Materialized view representations (for SQLAlchemy ORM access)
class ContactAnalyticsSummary(Base):
    __tablename__ = "contact_analytics_summary"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), primary_key=True, index=True)
    total_contacts = Column(Integer)
    active_contacts = Column(Integer)
    strong_relationships = Column(Integer)
    moderate_relationships = Column(Integer)
    weak_relationships = Column(Integer)
    avg_connection_strength = Column(Numeric(5,2))
    avg_interactions_per_contact = Column(Numeric(8,2))
    recent_interactions = Column(Integer)
    overdue_follow_ups = Column(Integer)
    high_priority_follow_ups = Column(Integer)
    
    # Note: This represents a materialized view, actual view creation happens in migrations

class InteractionAnalytics(Base):
    __tablename__ = "interaction_analytics"
    
    contact_id = Column(Integer, ForeignKey("contacts.id"), primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)
    total_interactions = Column(Integer)
    in_person_meetings = Column(Integer)
    phone_calls = Column(Integer)
    emails = Column(Integer)
    text_messages = Column(Integer)
    avg_interaction_quality = Column(Numeric(3,2))
    avg_interaction_duration = Column(Numeric(8,2))
    last_interaction_date = Column(DateTime(timezone=True))
    interactions_last_30_days = Column(Integer)
    interactions_initiated_by_user = Column(Integer)
    interactions_initiated_by_contact = Column(Integer)
    
    # Note: This represents a view, actual view creation happens in migrations

class OrganizationNetworkAnalytics(Base):
    __tablename__ = "organization_network_analytics"
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True, index=True)
    organization_name = Column(String(200))
    organization_type = Column(String(50))
    industry = Column(String(100))
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)
    current_contacts = Column(Integer)
    alumni_contacts = Column(Integer)
    avg_connection_strength = Column(Numeric(3,2))
    high_value_contacts = Column(Integer)
    total_interactions = Column(Integer)
    
    # Note: This represents a view, actual view creation happens in migrations

class SocialGroupAnalytics(Base):
    __tablename__ = "social_group_analytics"
    
    group_id = Column(Integer, ForeignKey("social_groups.id"), primary_key=True, index=True)
    group_name = Column(String(200))
    group_type = Column(String(50))
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)
    member_count = Column(Integer)
    active_members = Column(Integer)
    avg_member_connection_strength = Column(Numeric(3,2))
    total_activities = Column(Integer)
    avg_activity_attendance = Column(Numeric(8,2))
    last_activity_date = Column(DateTime(timezone=True))
    
    # Note: This represents a view, actual view creation happens in migrations
