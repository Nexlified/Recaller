from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from decimal import Decimal

# Analytics Response Models
class AnalyticsOverviewResponse(BaseModel):
    summary: Dict[str, Any]
    network_health: Dict[str, Any]
    recent_activity: Dict[str, Any]
    top_insights: List[Dict[str, Any]]

class NetworkGrowthResponse(BaseModel):
    growth_metrics: Dict[str, Any]
    growth_timeline: List[Dict[str, Any]]
    growth_sources: Dict[str, Any]
    predictions: Dict[str, Any]

class RelationshipHealthResponse(BaseModel):
    overall_health: Dict[str, Any]
    health_factors: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

class ContactAnalyticsSummaryResponse(BaseModel):
    tenant_id: int
    total_contacts: int
    active_contacts: int
    strong_relationships: int
    moderate_relationships: int
    weak_relationships: int
    avg_connection_strength: float
    avg_interactions_per_contact: float
    recent_interactions: int
    overdue_follow_ups: int
    high_priority_follow_ups: int

class InteractionAnalyticsResponse(BaseModel):
    contact_id: int
    tenant_id: int
    total_interactions: int
    in_person_meetings: int
    phone_calls: int
    emails: int
    text_messages: int
    avg_interaction_quality: Optional[float]
    avg_interaction_duration: Optional[float]
    last_interaction_date: Optional[datetime]
    interactions_last_30_days: int
    interactions_initiated_by_user: int
    interactions_initiated_by_contact: int

class OrganizationNetworkResponse(BaseModel):
    organization_id: int
    organization_name: str
    organization_type: str
    industry: Optional[str]
    tenant_id: int
    current_contacts: int
    alumni_contacts: int
    avg_connection_strength: Optional[float]
    high_value_contacts: int
    total_interactions: int

class SocialGroupAnalyticsResponse(BaseModel):
    group_id: int
    group_name: str
    group_type: str
    tenant_id: int
    member_count: int
    active_members: int
    avg_member_connection_strength: Optional[float]
    total_activities: int
    avg_activity_attendance: Optional[float]
    last_activity_date: Optional[datetime]

class NetworkingInsightResponse(BaseModel):
    id: int
    insight_type: str
    insight_category: Optional[str]
    priority: str
    title: str
    description: Optional[str]
    metrics: Optional[Dict[str, Any]]
    actionable_recommendations: List[str]
    confidence_score: Optional[float]
    insight_date: date
    status: str

class DailyMetricsResponse(BaseModel):
    metric_date: date
    total_contacts: Optional[int]
    active_contacts: Optional[int]
    new_contacts_added: Optional[int]
    contacts_archived: Optional[int]
    strong_relationships: Optional[int]
    moderate_relationships: Optional[int]
    weak_relationships: Optional[int]
    avg_connection_strength: Optional[float]
    total_interactions: Optional[int]
    new_interactions: Optional[int]
    avg_interaction_quality: Optional[float]
    interaction_types: Optional[Dict[str, Any]]
    overdue_follow_ups: Optional[int]
    completed_follow_ups: Optional[int]
    pending_follow_ups: Optional[int]
    network_growth_rate: Optional[float]
    engagement_rate: Optional[float]
    response_rate: Optional[float]

# Request Models
class InsightGenerationRequest(BaseModel):
    insight_types: Optional[List[str]] = None
    force_regenerate: bool = False

class CustomReportRequest(BaseModel):
    report_type: str
    date_range: Dict[str, date]
    metrics: List[str]
    filters: Optional[Dict[str, Any]] = None
    format: str = "json"

class PeriodComparisonRequest(BaseModel):
    metric_type: str
    period1: Dict[str, date]
    period2: Dict[str, date]
    
class GroupComparisonRequest(BaseModel):
    group_type: str  # "contacts", "organizations", "social_groups"
    group_ids: List[int]
    metrics: List[str]