"""
Analytics API Endpoints

This module provides comprehensive analytics endpoints for the Recaller application,
offering insights into contact relationships, network growth, interaction patterns,
and networking effectiveness.

The analytics system is designed to help users:
- Track network growth and relationship health
- Understand interaction patterns and effectiveness
- Get actionable insights for network maintenance
- Compare performance across different time periods
- Generate reports and export data

Key Features:
- Multi-tenant analytics with proper data isolation
- Real-time and historical analytics
- Predictive insights and recommendations
- Comprehensive reporting and export capabilities
- Performance benchmarking
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_context
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    NetworkGrowthResponse, 
    RelationshipHealthResponse,
    ContactAnalyticsSummaryResponse,
    InteractionAnalyticsResponse,
    InsightGenerationRequest,
    CustomReportRequest,
    PeriodComparisonRequest,
    GroupComparisonRequest
)
from app.crud.analytics import AnalyticsService
from app.models.analytics import (
    ContactAnalyticsSummary,
    InteractionAnalytics,
    OrganizationNetworkAnalytics,
    SocialGroupAnalytics,
    NetworkingInsight,
    DailyNetworkMetric
)
from app.models.contact import Contact

router = APIRouter()

# =============================================================================
# CORE ANALYTICS ENDPOINTS
# =============================================================================
# These endpoints provide high-level overview metrics and summaries that give
# users a quick understanding of their network health and recent activity.

@router.get("/overview", response_model=Dict[str, Any])
def get_analytics_overview(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics overview dashboard
    
    This endpoint provides a high-level summary of all networking analytics,
    designed for dashboard views and quick network health assessment.
    
    Returns:
        Dict containing:
        - summary: Basic network metrics (total contacts, active relationships)
        - network_health: Overall health scores and key indicators
        - recent_activity: Recent interactions and network changes
        - growth_metrics: Network expansion and trend data
        - recommendations: Top actionable insights
    
    Use Case:
        Perfect for main dashboard widgets and executive summaries.
        Shows the most important metrics at a glance.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    return analytics_service.get_overview_analytics()

@router.get("/summary", response_model=Dict[str, Any])
def get_analytics_summary(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get quick summary statistics from materialized views
    
    This endpoint provides fast access to key metrics using pre-calculated
    data from materialized views, ensuring quick response times for
    frequently accessed summary data.
    
    Returns:
        Dict containing:
        - total_contacts: Total number of contacts in network
        - active_contacts: Currently active relationships
        - relationship_distribution: Strong/moderate/weak breakdown
        - interaction_metrics: Average interactions and engagement
        - follow_up_status: Overdue and high-priority follow-ups
    
    Performance Note:
        Uses materialized views for optimal performance. Data refreshed
        periodically via background tasks.
    
    Use Case:
        Ideal for widgets that need to load quickly and show basic stats.
    """
    tenant_id = get_tenant_context(request)
    
    # Get summary from materialized view for optimal performance
    summary = db.query(ContactAnalyticsSummary).filter(
        ContactAnalyticsSummary.tenant_id == tenant_id
    ).first()
    
    if not summary:
        return {
            "total_contacts": 0,
            "active_contacts": 0,
            "strong_relationships": 0,
            "moderate_relationships": 0,
            "weak_relationships": 0,
            "avg_connection_strength": 0.0,
            "avg_interactions_per_contact": 0.0,
            "recent_interactions": 0,
            "overdue_follow_ups": 0,
            "high_priority_follow_ups": 0
        }
    
    return {
        "total_contacts": summary.total_contacts or 0,
        "active_contacts": summary.active_contacts or 0,
        "strong_relationships": summary.strong_relationships or 0,
        "moderate_relationships": summary.moderate_relationships or 0,
        "weak_relationships": summary.weak_relationships or 0,
        "avg_connection_strength": float(summary.avg_connection_strength or 0),
        "avg_interactions_per_contact": float(summary.avg_interactions_per_contact or 0),
        "recent_interactions": summary.recent_interactions or 0,
        "overdue_follow_ups": summary.overdue_follow_ups or 0,
        "high_priority_follow_ups": summary.high_priority_follow_ups or 0
    }

@router.get("/trends", response_model=List[Dict[str, Any]])
def get_analytics_trends(
    request: Request,
    period: int = Query(default=30, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get trending metrics over time for network growth analysis
    
    This endpoint provides time-series data showing how network metrics
    have changed over a specified period, enabling trend analysis and
    pattern recognition.
    
    Args:
        period: Number of days to analyze (7-365 days)
                - 7-30 days: Good for recent activity trends
                - 30-90 days: Quarterly performance analysis
                - 90-365 days: Long-term growth patterns
    
    Returns:
        List of daily metrics containing:
        - date: Date of the metric
        - total_contacts: Network size on that date
        - active_contacts: Active relationships
        - new_contacts: New contacts added that day
        - total_interactions: Total interactions that day
        - engagement_metrics: Quality and frequency data
        - growth_rates: Network expansion rates
    
    Use Case:
        Perfect for creating charts showing network growth over time,
        identifying seasonal patterns, and tracking progress against goals.
    """
    tenant_id = get_tenant_context(request)
    
    # Calculate date range for the specified period
    end_date = date.today()
    start_date = date.fromordinal(end_date.toordinal() - period)
    
    # Fetch daily metrics ordered chronologically
    metrics = db.query(DailyNetworkMetric).filter(
        DailyNetworkMetric.tenant_id == tenant_id,
        DailyNetworkMetric.metric_date >= start_date,
        DailyNetworkMetric.metric_date <= end_date
    ).order_by(DailyNetworkMetric.metric_date).all()
    
    return [
        {
            "date": metric.metric_date.isoformat(),
            "total_contacts": metric.total_contacts or 0,
            "active_contacts": metric.active_contacts or 0,
            "new_contacts": metric.new_contacts_added or 0,
            "total_interactions": metric.total_interactions or 0,
            "avg_connection_strength": float(metric.avg_connection_strength or 0),
            "network_growth_rate": float(metric.network_growth_rate or 0),
            "engagement_rate": float(metric.engagement_rate or 0)
        }
        for metric in metrics
    ]

@router.get("/kpis", response_model=Dict[str, Any])
def get_key_performance_indicators(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get key performance indicators for network management
    
    This endpoint calculates and returns the most important KPIs for
    effective network management, providing metrics that correlate
    with networking success and relationship quality.
    
    Key Performance Indicators:
        - network_size: Total number of meaningful connections
        - network_health_score: Overall relationship quality (0-10)
        - engagement_rate: Percentage of contacts actively engaged
        - growth_rate: Rate of network expansion over time
        - response_rate: How often contacts respond to outreach
        - strong_relationships_ratio: Percentage of high-quality relationships
        - follow_up_completion_rate: Success rate of follow-up activities
    
    Returns:
        Dict with KPIs and their current values, typically used for
        scorecards and performance dashboards.
    
    Use Case:
        Essential for tracking networking effectiveness against goals,
        identifying areas for improvement, and measuring ROI of networking activities.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    overview = analytics_service.get_overview_analytics()
    
    return {
        "network_size": overview["summary"]["total_contacts"],
        "network_health_score": overview["network_health"]["overall_score"],
        "engagement_rate": overview["network_health"]["engagement_rate"],
        "growth_rate": overview["network_health"]["growth_rate"],
        "response_rate": overview["network_health"]["response_rate"],
        "strong_relationships_ratio": (
            overview["summary"]["strong_relationships"] / 
            max(overview["summary"]["total_contacts"], 1)
        ),
        "follow_up_completion_rate": 0.85  # Mock - would calculate from actual data
    }

# =============================================================================
# NETWORK ANALYTICS ENDPOINTS
# =============================================================================
# These endpoints focus on network structure, growth patterns, and overall
# relationship health. They help users understand their network composition
# and identify opportunities for growth and strengthening relationships.

@router.get("/network/overview", response_model=Dict[str, Any])
def get_network_overview(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive network size, strength, and growth overview
    
    This endpoint provides a high-level view of the user's professional
    network, focusing on quantitative metrics that indicate network health
    and effectiveness.
    
    Network Overview Metrics:
        - network_size: Total number of contacts in the network
        - active_contacts: Contacts with recent meaningful interactions
        - network_health: Overall health score based on relationship quality
        - growth_metrics: Recent expansion and trend data
    
    Returns:
        Dict containing current network status and key growth indicators
    
    Use Case:
        Essential for understanding network maturity and identifying
        opportunities for expansion or relationship strengthening.
        
    Best Practice:
        Review monthly to track progress toward networking goals and
        identify shifts in network dynamics.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    overview = analytics_service.get_overview_analytics()
    return {
        "network_size": overview["summary"]["total_contacts"],
        "active_contacts": overview["summary"]["active_contacts"],
        "network_health": overview["network_health"],
        "growth_metrics": {
            "total_growth_30_days": overview["recent_activity"]["new_contacts_last_30_days"],
            "growth_rate": overview["network_health"]["growth_rate"]
        }
    }

@router.get("/network/distribution", response_model=Dict[str, Any])
def get_network_distribution(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get relationship strength distribution across the network
    
    This endpoint analyzes how relationships are distributed across
    different strength levels, providing insights into network quality
    and opportunities for relationship development.
    
    Distribution Categories:
        - Strong (8-10): Deep, trusted relationships with frequent contact
        - Moderate (5-7): Regular professional relationships
        - Weak (1-4): Acquaintances and infrequent contacts
    
    Returns:
        Dict with counts and percentages for each strength category
    
    Use Case:
        Helps users understand if their network is balanced and identify
        opportunities to strengthen moderate relationships or maintain
        strong ones.
        
    Optimization Tip:
        Aim for 15-20% strong relationships, 40-50% moderate, and 30-45% weak
        for a healthy, manageable network distribution.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    health_analytics = analytics_service.get_relationship_health_analytics()
    return health_analytics["overall_health"]["distribution"]

@router.get("/network/growth", response_model=Dict[str, Any])
def get_network_growth(
    request: Request,
    period: int = Query(default=90, ge=30, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed network growth analysis over time
    
    This endpoint provides comprehensive analysis of how the network
    has grown and evolved over the specified period, including growth
    patterns, velocity, and predictive insights.
    
    Args:
        period: Analysis period in days
                - 30 days: Recent growth trends
                - 90 days: Quarterly growth patterns (recommended)
                - 180+ days: Long-term growth analysis
    
    Growth Metrics:
        - total_growth: Net new contacts added
        - growth_velocity: Rate of contact acquisition
        - growth_quality: Strength of new relationships
        - seasonal_patterns: Growth variations over time
        - predictions: Forecasted growth for next period
    
    Returns:
        Comprehensive growth analytics with trends and predictions
    
    Use Case:
        Essential for understanding networking effectiveness and planning
        future networking activities. Helps identify successful strategies
        and optimal networking periods.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    return analytics_service.get_network_growth_analytics(period)

@router.get("/network/health", response_model=Dict[str, Any])
def get_network_health(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive network health assessment
    
    This endpoint provides a holistic evaluation of network health,
    combining multiple factors to generate an overall health score
    and specific recommendations for improvement.
    
    Health Factors:
        - Relationship strength distribution
        - Interaction frequency and quality
        - Response rates and engagement
        - Follow-up consistency
        - Network diversity and coverage
    
    Health Score (0-10):
        - 9-10: Excellent - Highly engaged, well-maintained network
        - 7-8: Good - Strong network with minor improvement areas
        - 5-6: Fair - Adequate network needing attention
        - 3-4: Poor - Significant maintenance required
        - 0-2: Critical - Major network health issues
    
    Returns:
        Dict containing overall health score, factor breakdowns,
        specific recommendations, and priority actions
    
    Use Case:
        Regular health checks (monthly) to ensure network remains
        engaged and productive. Critical for maintaining relationship
        quality at scale.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    return analytics_service.get_relationship_health_analytics()

# =============================================================================
# INTERACTION ANALYTICS ENDPOINTS
# =============================================================================
# These endpoints analyze communication patterns, interaction quality, and
# engagement effectiveness. They help users optimize their communication
# strategies and improve relationship maintenance.

@router.get("/interactions/overview", response_model=Dict[str, Any])
def get_interactions_overview(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive interaction patterns and trends analysis
    
    This endpoint provides an overview of all interaction activities,
    helping users understand their communication patterns, effectiveness,
    and areas for improvement.
    
    Interaction Metrics:
        - total_interactions: All recorded interactions across channels
        - avg_quality: Average quality score (1-10) of interactions
        - avg_duration: Average length of meaningful interactions
        - interaction_frequency: Average interactions per contact
        - recent_activity: Interactions in the last 30 days
    
    Quality Scoring (1-10):
        - 9-10: Deep, meaningful conversations with clear outcomes
        - 7-8: Productive interactions with good engagement
        - 5-6: Standard interactions, basic information exchange
        - 3-4: Brief or superficial interactions
        - 1-2: Minimal engagement or failed attempts
    
    Returns:
        Dict with interaction summary statistics and trends
    
    Use Case:
        Essential for understanding communication effectiveness and
        identifying patterns that lead to stronger relationships.
        Review weekly to optimize outreach strategies.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    interactions = analytics_service.get_interaction_analytics()
    
    if not interactions:
        return {
            "total_interactions": 0,
            "avg_quality": 0.0,
            "avg_duration": 0.0,
            "interaction_frequency": 0.0,
            "recent_activity": 0
        }
    
    # Calculate aggregate metrics across all contacts
    total_interactions = sum(i["total_interactions"] for i in interactions)
    avg_quality = sum(i["avg_interaction_quality"] for i in interactions) / len(interactions)
    avg_duration = sum(i["avg_interaction_duration"] for i in interactions) / len(interactions)
    recent_activity = sum(i["interactions_last_30_days"] for i in interactions)
    
    return {
        "total_interactions": total_interactions,
        "avg_quality": avg_quality,
        "avg_duration": avg_duration,
        "interaction_frequency": total_interactions / max(len(interactions), 1),
        "recent_activity": recent_activity
    }

@router.get("/interactions/types", response_model=Dict[str, Any])
def get_interaction_types_breakdown(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get detailed breakdown of interactions by communication channel
    
    This endpoint analyzes how interactions are distributed across
    different communication channels, helping users understand their
    preferred communication methods and their effectiveness.
    
    Channel Types:
        - meetings: Face-to-face or video meetings (highest impact)
        - calls: Phone conversations (high personal touch)
        - emails: Email communications (good for detailed discussions)
        - texts: Text messages and instant messaging (quick touch points)
    
    Channel Effectiveness Tips:
        - Meetings: Best for building trust and complex discussions
        - Calls: Ideal for urgent matters and personal check-ins
        - Emails: Perfect for detailed information sharing
        - Texts: Great for quick updates and casual contact
    
    Returns:
        Dict with interaction counts by channel type
    
    Use Case:
        Helps optimize communication strategy by understanding which
        channels are most/least used and planning channel diversification
        for stronger relationship building.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    interactions = analytics_service.get_interaction_analytics()
    
    return {
        "meetings": sum(i["in_person_meetings"] for i in interactions),
        "calls": sum(i["phone_calls"] for i in interactions),
        "emails": sum(i["emails"] for i in interactions),
        "texts": sum(i["text_messages"] for i in interactions)
    }

@router.get("/interactions/quality", response_model=Dict[str, Any])
def get_interaction_quality_trends(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get interaction quality trends and improvement insights
    
    This endpoint analyzes the quality of interactions over time,
    helping users understand what makes conversations more meaningful
    and productive.
    
    Quality Metrics:
        - avg_quality: Overall average quality score
        - quality_trend: Whether quality is improving, stable, or declining
        - high_quality_interactions: Count of exceptional interactions (8+)
    
    Quality Improvement Tips:
        - Prepare talking points before important conversations
        - Ask open-ended questions to encourage deeper discussion
        - Follow up on previous conversations to show continuity
        - Set clear objectives for each interaction
    
    Returns:
        Dict with quality metrics and trend analysis
    
    Use Case:
        Track communication effectiveness improvement over time and
        identify strategies that lead to higher quality interactions.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    interactions = analytics_service.get_interaction_analytics()
    
    if not interactions:
        return {"avg_quality": 0.0, "quality_trend": "stable", "high_quality_interactions": 0}
    
    avg_quality = sum(i["avg_interaction_quality"] for i in interactions) / len(interactions)
    high_quality = sum(1 for i in interactions if i["avg_interaction_quality"] >= 8.0)
    
    return {
        "avg_quality": avg_quality,
        "quality_trend": "improving",  # Would calculate from historical data
        "high_quality_interactions": high_quality
    }

@router.get("/interactions/frequency", response_model=Dict[str, Any])
def get_interaction_frequency_analysis(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive interaction frequency analysis
    
    This endpoint analyzes how often users interact with their network,
    identifying patterns, optimal frequencies, and opportunities for
    more consistent engagement.
    
    Frequency Metrics:
        - interactions_last_30_days: Recent interaction volume
        - avg_interactions_per_contact: Contact engagement rate
        - frequency_trend: Whether interactions are increasing/decreasing
        - most_active_period: Peak interaction times/days
    
    Optimal Frequency Guidelines:
        - Strong relationships: Weekly to monthly contact
        - Moderate relationships: Monthly to quarterly contact
        - Weak relationships: Quarterly to bi-annual contact
    
    Returns:
        Dict with frequency statistics and trend analysis
    
    Use Case:
        Helps maintain consistent network engagement and identifies
        when interaction frequency drops below optimal levels.
        Essential for relationship maintenance planning.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    interactions = analytics_service.get_interaction_analytics()
    recent_interactions = sum(i["interactions_last_30_days"] for i in interactions)
    
    return {
        "interactions_last_30_days": recent_interactions,
        "avg_interactions_per_contact": recent_interactions / max(len(interactions), 1),
        "frequency_trend": "stable",  # Would calculate from historical data
        "most_active_period": "Tuesday afternoons"  # Mock data
    }

@router.get("/interactions/response-rate", response_model=Dict[str, Any])
def get_response_rate_analysis(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get detailed contact response patterns and engagement analysis
    
    This endpoint analyzes how contacts respond to outreach efforts,
    providing insights into engagement effectiveness and optimal
    communication strategies.
    
    Response Metrics:
        - overall_response_rate: Percentage of outreach that gets responses
        - user_initiated: Communications started by the user
        - contact_initiated: Communications started by contacts
        - response_time_avg: Average time contacts take to respond
        - best_response_days: Days with highest response rates
    
    Response Rate Benchmarks:
        - 70%+: Excellent - Strong network engagement
        - 50-70%: Good - Healthy response rates
        - 30-50%: Fair - Room for improvement
        - <30%: Poor - Need strategy adjustment
    
    Improvement Strategies:
        - Personalize outreach messages
        - Reference recent shared experiences
        - Provide value in each communication
        - Use preferred communication channels
    
    Returns:
        Dict with response rate metrics and timing analysis
    
    Use Case:
        Critical for optimizing outreach effectiveness and understanding
        network engagement levels. Helps identify the best times and
        methods for contacting different types of relationships.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    interactions = analytics_service.get_interaction_analytics()
    
    user_initiated = sum(i["interactions_initiated_by_user"] for i in interactions)
    contact_initiated = sum(i["interactions_initiated_by_contact"] for i in interactions)
    total = user_initiated + contact_initiated
    
    return {
        "overall_response_rate": contact_initiated / max(total, 1),
        "user_initiated": user_initiated,
        "contact_initiated": contact_initiated,
        "response_time_avg": "2.5 hours",  # Mock data
        "best_response_days": ["Tuesday", "Wednesday"]  # Mock data
    }

# Relationship Analytics Endpoints
@router.get("/relationships/strength", response_model=Dict[str, Any])
def get_relationship_strength_analytics(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get relationship strength analytics"""
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    return analytics_service.get_relationship_health_analytics()

@router.get("/relationships/lifecycle", response_model=Dict[str, Any])
def get_relationship_lifecycle_analysis(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get relationship lifecycle stages"""
    # Mock implementation - would analyze relationship progression over time
    return {
        "new_relationships": 12,
        "developing_relationships": 34,
        "established_relationships": 156,
        "mature_relationships": 89,
        "dormant_relationships": 23,
        "lifecycle_trends": {
            "avg_time_to_establish": "4.2 months",
            "retention_rate": 0.87,
            "reactivation_success": 0.34
        }
    }

@router.get("/relationships/trends", response_model=Dict[str, Any])
def get_relationship_trends(
    request: Request,
    period: int = Query(default=90, ge=30, le=365),
    db: Session = Depends(get_db)
):
    """Get relationship trend analysis"""
    # Mock implementation - would analyze relationship strength changes over time
    return {
        "strengthening_relationships": 23,
        "weakening_relationships": 8,
        "stable_relationships": 187,
        "trend_factors": [
            "increased interaction frequency",
            "higher quality meetings",
            "mutual introductions"
        ],
        "prediction": {
            "next_30_days": {
                "expected_strengthening": 15,
                "at_risk": 5
            }
        }
    }

@router.get("/relationships/maintenance", response_model=Dict[str, Any])
def get_relationship_maintenance_insights(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get relationship maintenance insights"""
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    health_analytics = analytics_service.get_relationship_health_analytics()
    return {
        "overdue_follow_ups": len([r for r in health_analytics["recommendations"] if r["type"] == "immediate_action"]),
        "maintenance_schedule": health_analytics["recommendations"],
        "optimal_contact_frequency": {
            "strong_relationships": "monthly",
            "moderate_relationships": "quarterly", 
            "weak_relationships": "bi-annually"
        }
    }

# Organization & Group Analytics
@router.get("/organizations/network", response_model=List[Dict[str, Any]])
def get_organization_network_analysis(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get organization network analysis"""
    tenant_id = get_tenant_context(request)
    
    analytics = db.query(OrganizationNetworkAnalytics).filter(
        OrganizationNetworkAnalytics.tenant_id == tenant_id
    ).all()
    
    return [
        {
            "organization_id": a.organization_id,
            "organization_name": a.organization_name,
            "organization_type": a.organization_type,
            "industry": a.industry,
            "current_contacts": a.current_contacts or 0,
            "alumni_contacts": a.alumni_contacts or 0,
            "avg_connection_strength": float(a.avg_connection_strength or 0),
            "high_value_contacts": a.high_value_contacts or 0,
            "total_interactions": a.total_interactions or 0
        }
        for a in analytics
    ]

@router.get("/organizations/influence", response_model=Dict[str, Any])
def get_organization_influence_metrics(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get organization influence metrics"""
    # Mock implementation
    return {
        "most_influential_orgs": [
            {"name": "TechCorp", "influence_score": 8.5, "contact_count": 23},
            {"name": "University ABC", "influence_score": 7.8, "contact_count": 15}
        ],
        "industry_distribution": {
            "technology": 45,
            "finance": 32,
            "healthcare": 18,
            "education": 25
        },
        "network_reach": {
            "companies": 34,
            "universities": 8,
            "nonprofits": 12
        }
    }

@router.get("/social-groups/engagement", response_model=List[Dict[str, Any]])
def get_social_group_engagement(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get social group engagement analytics"""
    tenant_id = get_tenant_context(request)
    
    analytics = db.query(SocialGroupAnalytics).filter(
        SocialGroupAnalytics.tenant_id == tenant_id
    ).all()
    
    return [
        {
            "group_id": a.group_id,
            "group_name": a.group_name,
            "group_type": a.group_type,
            "member_count": a.member_count or 0,
            "active_members": a.active_members or 0,
            "avg_connection_strength": float(a.avg_member_connection_strength or 0),
            "engagement_rate": (a.active_members or 0) / max(a.member_count or 1, 1),
            "last_activity": a.last_activity_date
        }
        for a in analytics
    ]

@router.get("/social-groups/activity", response_model=Dict[str, Any])
def get_social_group_activity_analytics(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get group activity analytics"""
    tenant_id = get_tenant_context(request)
    
    analytics = db.query(SocialGroupAnalytics).filter(
        SocialGroupAnalytics.tenant_id == tenant_id
    ).all()
    
    total_activities = sum(a.total_activities or 0 for a in analytics)
    avg_attendance = sum(a.avg_activity_attendance or 0 for a in analytics) / max(len(analytics), 1)
    
    return {
        "total_activities": total_activities,
        "avg_attendance": avg_attendance,
        "most_active_groups": [
            {"group_name": a.group_name, "activity_count": a.total_activities or 0}
            for a in sorted(analytics, key=lambda x: x.total_activities or 0, reverse=True)[:5]
        ],
        "attendance_trends": "stable"  # Mock
    }

# =============================================================================
# AI INSIGHTS & RECOMMENDATIONS ENDPOINTS
# =============================================================================
# These endpoints provide AI-generated insights and actionable recommendations
# based on network analysis, helping users make data-driven decisions about
# their networking strategies and relationship management.

@router.get("/insights", response_model=List[Dict[str, Any]])
def get_networking_insights(
    request: Request,
    limit: int = Query(default=10, ge=1, le=50),
    insight_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get AI-generated networking insights and recommendations
    
    This endpoint provides intelligent insights based on network analysis,
    interaction patterns, and relationship health. The AI identifies patterns,
    opportunities, and potential issues to help optimize networking effectiveness.
    
    Args:
        limit: Maximum number of insights to return (1-50)
        insight_type: Filter by specific insight category:
                     - 'opportunity': Growth and expansion opportunities
                     - 'maintenance': Relationship maintenance needs
                     - 'engagement': Interaction optimization suggestions
                     - 'health': Network health improvement areas
                     - 'prediction': Trend-based predictions
    
    Insight Categories:
        - Opportunity Insights: New connections, introductions, events
        - Maintenance Insights: Overdue follow-ups, relationship decay
        - Engagement Insights: Communication optimization, timing
        - Health Insights: Network balance, strength distribution
        - Predictive Insights: Future trends, potential issues
    
    Insight Prioritization:
        - High Priority: Immediate action required (relationship at risk)
        - Medium Priority: Important improvements (growth opportunities)
        - Low Priority: Optimization suggestions (efficiency gains)
    
    Returns:
        List of insights with priority, confidence, and actionable recommendations
    
    Use Case:
        Review insights weekly to stay proactive about network management
        and identify high-impact actions. Essential for maintaining and
        growing network effectiveness.
    """
    tenant_id = get_tenant_context(request)
    
    query = db.query(NetworkingInsight).filter(
        NetworkingInsight.tenant_id == tenant_id,
        NetworkingInsight.status == 'active'
    )
    
    if insight_type:
        query = query.filter(NetworkingInsight.insight_type == insight_type)
    
    insights = query.order_by(
        NetworkingInsight.priority.desc(),
        NetworkingInsight.confidence_score.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": i.id,
            "insight_type": i.insight_type,
            "insight_category": i.insight_category,
            "priority": i.priority,
            "title": i.title,
            "description": i.description,
            "metrics": i.metrics,
            "actionable_recommendations": i.actionable_recommendations or [],
            "confidence_score": float(i.confidence_score or 0),
            "insight_date": i.insight_date,
            "status": i.status
        }
        for i in insights
    ]

@router.post("/insights/generate", response_model=List[Dict[str, Any]])
def generate_insights(
    request: Request,
    insight_request: InsightGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger on-demand insight generation for specific analysis areas
    
    This endpoint allows users to request fresh analysis and insight generation
    for specific areas of their network, providing real-time recommendations
    based on current data.
    
    Request Parameters:
        insight_types: List of insight categories to generate:
                      - 'network_growth': Expansion opportunities and strategies
                      - 'relationship_health': Relationship maintenance needs
                      - 'interaction_optimization': Communication improvements
                      - 'follow_up_recommendations': Overdue contact suggestions
                      - 'networking_opportunities': Event and introduction suggestions
    
    Generation Process:
        1. Analyzes current network state and patterns
        2. Identifies gaps, opportunities, and risks
        3. Generates prioritized, actionable recommendations
        4. Calculates confidence scores based on data quality
        5. Saves insights for future reference and tracking
    
    Insight Quality Factors:
        - Data completeness and recency
        - Pattern consistency over time
        - Network size and diversity
        - Interaction frequency and quality
    
    Returns:
        List of newly generated insights with recommendations and confidence scores
    
    Use Case:
        Generate fresh insights before important networking periods,
        quarterly planning sessions, or when making strategic networking
        decisions. Useful for getting targeted advice for specific challenges.
        
    Best Practice:
        Generate insights monthly or before major networking events to
        ensure recommendations are current and relevant.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    # Generate insights based on requested types
    insights = analytics_service.generate_insights(insight_request.insight_types)
    
    # Save generated insights to database for future reference
    for insight_data in insights:
        db_insight = NetworkingInsight(
            tenant_id=tenant_id,
            user_id=1,  # Would get from authenticated user
            **insight_data,
            insight_date=date.today()
        )
        db.add(db_insight)
    
    db.commit()
    
    return insights

# Follow-up & Engagement Analytics
@router.get("/follow-ups/performance", response_model=Dict[str, Any])
def get_follow_up_performance(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get follow-up completion rates"""
    tenant_id = get_tenant_context(request)
    
    # Mock implementation - would calculate from actual follow-up data
    return {
        "completion_rate": 0.78,
        "avg_response_time": "2.3 days",
        "overdue_count": 12,
        "completed_last_30_days": 45,
        "success_rate_by_type": {
            "email": 0.85,
            "call": 0.72,
            "meeting": 0.91
        }
    }

@router.get("/follow-ups/overdue", response_model=Dict[str, Any])
def get_overdue_follow_ups(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get overdue follow-up analysis"""
    tenant_id = get_tenant_context(request)
    
    overdue_contacts = db.query(Contact).filter(
        and_(
            Contact.tenant_id == tenant_id,
            Contact.next_suggested_contact_date < date.today(),
            Contact.is_active == True
        )
    ).all()
    
    return {
        "total_overdue": len(overdue_contacts),
        "overdue_by_urgency": {
            "high": sum(1 for c in overdue_contacts if c.follow_up_urgency == 'high'),
            "medium": sum(1 for c in overdue_contacts if c.follow_up_urgency == 'medium'),
            "low": sum(1 for c in overdue_contacts if c.follow_up_urgency == 'low')
        },
        "avg_days_overdue": 7.5,  # Mock calculation
        "overdue_contacts": [
            {
                "contact_id": c.id,
                "name": f"{c.first_name} {c.last_name}",
                "days_overdue": (date.today() - (c.next_suggested_contact_date or date.today())).days,
                "urgency": c.follow_up_urgency,
                "connection_strength": float(c.connection_strength or 0)
            }
            for c in overdue_contacts[:10]  # Limit to top 10
        ]
    }

@router.get("/engagement/patterns", response_model=Dict[str, Any])
def get_engagement_patterns(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get engagement pattern analysis"""
    # Mock implementation
    return {
        "best_contact_days": ["Tuesday", "Wednesday"],
        "best_contact_times": ["10:00-11:00", "14:00-15:00"],
        "response_rate_by_channel": {
            "email": 0.68,
            "phone": 0.82,
            "linkedin": 0.45
        },
        "engagement_trends": {
            "increasing": 34,
            "stable": 187,
            "decreasing": 23
        }
    }

@router.get("/engagement/effectiveness", response_model=Dict[str, Any])
def get_engagement_effectiveness(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get engagement effectiveness metrics"""
    # Mock implementation
    return {
        "overall_effectiveness": 7.3,
        "top_performing_strategies": [
            {"strategy": "Personal referrals", "success_rate": 0.89},
            {"strategy": "Industry events", "success_rate": 0.76},
            {"strategy": "LinkedIn outreach", "success_rate": 0.43}
        ],
        "conversion_metrics": {
            "contact_to_meeting": 0.34,
            "meeting_to_opportunity": 0.18,
            "opportunity_to_partnership": 0.07
        }
    }

# Predictive Analytics
@router.get("/predictions/churn", response_model=Dict[str, Any])
def get_churn_prediction(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get relationship churn prediction"""
    tenant_id = get_tenant_context(request)
    
    # Mock churn prediction based on interaction patterns
    at_risk_contacts = db.query(Contact).filter(
        and_(
            Contact.tenant_id == tenant_id,
            Contact.is_active == True,
            Contact.connection_strength < 4
        )
    ).all()
    
    return {
        "churn_risk_summary": {
            "high_risk": len([c for c in at_risk_contacts if c.connection_strength and c.connection_strength < 2]),
            "medium_risk": len([c for c in at_risk_contacts if c.connection_strength and 2 <= c.connection_strength < 4]),
            "total_at_risk": len(at_risk_contacts)
        },
        "predicted_churn_30_days": len(at_risk_contacts) // 3,
        "retention_recommendations": [
            "Schedule check-in calls with high-risk contacts",
            "Send personalized updates or articles",
            "Invite to relevant events or meetups"
        ],
        "at_risk_contacts": [
            {
                "contact_id": c.id,
                "name": f"{c.first_name} {c.last_name}",
                "churn_risk": "high" if c.connection_strength and c.connection_strength < 2 else "medium",
                "connection_strength": float(c.connection_strength or 0),
                "last_interaction": c.last_meaningful_interaction.isoformat() if c.last_meaningful_interaction else None
            }
            for c in at_risk_contacts[:10]
        ]
    }

@router.get("/predictions/growth", response_model=Dict[str, Any])
def get_growth_predictions(
    request: Request,
    period_days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get network growth predictions"""
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    growth_analytics = analytics_service.get_network_growth_analytics(90)  # Use 90 days for prediction
    
    return {
        "prediction_period_days": period_days,
        "predicted_new_contacts": growth_analytics["predictions"]["next_30_days"] * (period_days / 30),
        "confidence": growth_analytics["predictions"]["confidence"],
        "growth_drivers": [
            "Historical networking patterns",
            "Scheduled events and meetings",
            "Seasonal networking trends"
        ],
        "scenarios": {
            "conservative": growth_analytics["predictions"]["next_30_days"] * 0.7 * (period_days / 30),
            "expected": growth_analytics["predictions"]["next_30_days"] * (period_days / 30),
            "optimistic": growth_analytics["predictions"]["next_30_days"] * 1.3 * (period_days / 30)
        }
    }

@router.get("/predictions/opportunities", response_model=Dict[str, Any])
def get_networking_opportunities(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get networking opportunities prediction"""
    # Mock implementation
    return {
        "opportunity_score": 8.2,
        "top_opportunities": [
            {
                "type": "mutual_connection",
                "description": "3 contacts work at companies where you have strong relationships",
                "potential_contacts": 3,
                "confidence": 0.85
            },
            {
                "type": "industry_expansion",
                "description": "Healthcare industry shows high engagement rates",
                "potential_contacts": 8,
                "confidence": 0.72
            }
        ],
        "recommended_actions": [
            "Ask Sarah Chen for introductions at TechCorp",
            "Attend the Healthcare Innovation Summit",
            "Reconnect with dormant contacts in finance sector"
        ]
    }

@router.get("/predictions/maintenance", response_model=Dict[str, Any])
def get_maintenance_predictions(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get relationship maintenance recommendations"""
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    health_analytics = analytics_service.get_relationship_health_analytics()
    
    return {
        "maintenance_priority": health_analytics["recommendations"],
        "optimal_schedule": {
            "weekly": "5-7 strong relationship contacts",
            "monthly": "15-20 moderate relationship contacts", 
            "quarterly": "All weak relationship contacts"
        },
        "automated_suggestions": [
            "Send birthday reminders for key contacts",
            "Schedule quarterly check-ins with dormant contacts",
            "Follow up on shared interests and hobbies"
        ],
        "success_metrics": {
            "target_interaction_frequency": "2.5 interactions per contact per month",
            "relationship_strength_goal": "Move 20% of weak relationships to moderate"
        }
    }

# Comparative Analytics
@router.get("/compare/periods", response_model=Dict[str, Any])
def compare_periods(
    request: Request,
    period1_days: int = Query(default=30, ge=7, le=365),
    period2_days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Compare different time periods"""
    tenant_id = get_tenant_context(request)
    
    # Calculate periods
    end_date = date.today()
    period1_start = end_date - timedelta(days=period1_days)
    period2_start = period1_start - timedelta(days=period2_days)
    period2_end = period1_start
    
    # Get metrics for both periods
    period1_metrics = db.query(DailyNetworkMetric).filter(
        and_(
            DailyNetworkMetric.tenant_id == tenant_id,
            DailyNetworkMetric.metric_date >= period1_start,
            DailyNetworkMetric.metric_date <= end_date
        )
    ).all()
    
    period2_metrics = db.query(DailyNetworkMetric).filter(
        and_(
            DailyNetworkMetric.tenant_id == tenant_id,
            DailyNetworkMetric.metric_date >= period2_start,
            DailyNetworkMetric.metric_date <= period2_end
        )
    ).all()
    
    # Calculate averages
    def calc_averages(metrics):
        if not metrics:
            return {"contacts": 0, "interactions": 0, "growth_rate": 0}
        return {
            "contacts": sum(m.total_contacts or 0 for m in metrics) / len(metrics),
            "interactions": sum(m.total_interactions or 0 for m in metrics) / len(metrics),
            "growth_rate": sum(m.network_growth_rate or 0 for m in metrics) / len(metrics)
        }
    
    period1_avg = calc_averages(period1_metrics)
    period2_avg = calc_averages(period2_metrics)
    
    return {
        "period1": {
            "start_date": period1_start.isoformat(),
            "end_date": end_date.isoformat(),
            "averages": period1_avg
        },
        "period2": {
            "start_date": period2_start.isoformat(), 
            "end_date": period2_end.isoformat(),
            "averages": period2_avg
        },
        "comparison": {
            "contact_growth": period1_avg["contacts"] - period2_avg["contacts"],
            "interaction_change": period1_avg["interactions"] - period2_avg["interactions"],
            "growth_rate_change": period1_avg["growth_rate"] - period2_avg["growth_rate"]
        }
    }

@router.get("/compare/groups", response_model=Dict[str, Any])
def compare_groups(
    request: Request,
    group_type: str = Query(..., description="Type of groups to compare: contacts, organizations, social_groups"),
    group_ids: str = Query(..., description="Comma-separated list of group IDs"),
    db: Session = Depends(get_db)
):
    """Compare different contact groups"""
    tenant_id = get_tenant_context(request)
    
    group_id_list = [int(id.strip()) for id in group_ids.split(",")]
    
    if group_type == "organizations":
        analytics = db.query(OrganizationNetworkAnalytics).filter(
            and_(
                OrganizationNetworkAnalytics.tenant_id == tenant_id,
                OrganizationNetworkAnalytics.organization_id.in_(group_id_list)
            )
        ).all()
        
        return {
            "group_type": group_type,
            "comparison": [
                {
                    "group_id": a.organization_id,
                    "group_name": a.organization_name,
                    "contacts": a.current_contacts + a.alumni_contacts,
                    "avg_strength": float(a.avg_connection_strength or 0),
                    "interactions": a.total_interactions
                }
                for a in analytics
            ]
        }
    
    elif group_type == "social_groups":
        analytics = db.query(SocialGroupAnalytics).filter(
            and_(
                SocialGroupAnalytics.tenant_id == tenant_id,
                SocialGroupAnalytics.group_id.in_(group_id_list)
            )
        ).all()
        
        return {
            "group_type": group_type,
            "comparison": [
                {
                    "group_id": a.group_id,
                    "group_name": a.group_name,
                    "active_members": a.active_members,
                    "avg_strength": float(a.avg_member_connection_strength or 0),
                    "activities": a.total_activities
                }
                for a in analytics
            ]
        }
    
    else:
        return {"error": f"Unsupported group type: {group_type}"}

@router.get("/benchmarks", response_model=Dict[str, Any])
def get_analytics_benchmarks(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get industry/usage benchmarks"""
    # Mock implementation with industry benchmarks
    return {
        "industry_benchmarks": {
            "network_size": {
                "small_business": {"min": 50, "avg": 150, "max": 300},
                "mid_market": {"min": 200, "avg": 500, "max": 1000},
                "enterprise": {"min": 500, "avg": 1500, "max": 5000}
            },
            "interaction_frequency": {
                "quarterly": 0.25,
                "monthly": 1.0,
                "weekly": 4.0,
                "daily": 20.0
            },
            "relationship_distribution": {
                "strong": 0.15,
                "moderate": 0.45,
                "weak": 0.40
            }
        },
        "user_percentile": {
            "network_size": 75,
            "interaction_frequency": 68,
            "relationship_quality": 82
        },
        "improvement_areas": [
            "Increase interaction frequency with moderate relationships",
            "Expand network in underrepresented industries",
            "Improve follow-up consistency"
        ]
    }

# Export & Reporting
@router.get("/reports/monthly", response_model=Dict[str, Any])
def get_monthly_report(
    request: Request,
    year: int = Query(default=datetime.now().year),
    month: int = Query(default=datetime.now().month, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Get monthly analytics report"""
    from app.services.analytics import AnalyticsExportService
    
    tenant_id = get_tenant_context(request)
    export_service = AnalyticsExportService(db, tenant_id)
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    return export_service.export_custom_report({
        "report_type": "network_growth",
        "date_range": {"start": start_date, "end": end_date}
    })

@router.get("/reports/quarterly", response_model=Dict[str, Any])
def get_quarterly_report(
    request: Request,
    year: int = Query(default=datetime.now().year),
    quarter: int = Query(default=((datetime.now().month - 1) // 3) + 1, ge=1, le=4),
    db: Session = Depends(get_db)
):
    """Get quarterly analytics report"""
    from app.services.analytics import AnalyticsExportService
    
    tenant_id = get_tenant_context(request)
    export_service = AnalyticsExportService(db, tenant_id)
    
    # Calculate date range for the quarter
    start_month = (quarter - 1) * 3 + 1
    start_date = date(year, start_month, 1)
    
    if quarter == 4:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_month = quarter * 3 + 1
        end_date = date(year, end_month, 1) - timedelta(days=1)
    
    return export_service.export_custom_report({
        "report_type": "relationship_health",
        "date_range": {"start": start_date, "end": end_date}
    })

@router.post("/reports/custom", response_model=Dict[str, Any])
def generate_custom_report(
    request: Request,
    report_request: CustomReportRequest,
    db: Session = Depends(get_db)
):
    """Generate custom report"""
    from app.services.analytics import AnalyticsExportService
    
    tenant_id = get_tenant_context(request)
    export_service = AnalyticsExportService(db, tenant_id)
    
    return export_service.export_custom_report({
        "report_type": report_request.report_type,
        "date_range": report_request.date_range,
        "filters": report_request.filters
    })

@router.get("/export", response_model=Dict[str, Any])
def export_analytics_data(
    request: Request,
    format: str = Query(default="json", description="Export format: json, csv"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    metrics: Optional[str] = Query(default=None, description="Comma-separated list of metrics to export"),
    db: Session = Depends(get_db)
):
    """Export analytics data"""
    from app.services.analytics import AnalyticsExportService
    
    tenant_id = get_tenant_context(request)
    export_service = AnalyticsExportService(db, tenant_id)
    
    # Parse date range
    date_range = None
    if start_date and end_date:
        date_range = {"start": start_date, "end": end_date}
    
    # Parse metrics list
    metrics_list = None
    if metrics:
        metrics_list = [m.strip() for m in metrics.split(",")]
    
    return export_service.export_analytics_data(
        export_format=format,
        date_range=date_range,
        metrics=metrics_list
    )

@router.get("/recommendations", response_model=List[Dict[str, Any]])
def get_actionable_recommendations(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get prioritized, actionable recommendations for network improvement
    
    This endpoint provides concrete, actionable steps users can take to
    improve their network health, strengthen relationships, and achieve
    better networking outcomes.
    
    Recommendation Categories:
        - Immediate Actions: Urgent follow-ups and relationship maintenance
        - Growth Opportunities: Network expansion and new connection strategies
        - Optimization: Communication and engagement improvements
        - Maintenance: Regular relationship care and nurturing activities
        - Strategic: Long-term networking goal alignment
    
    Recommendation Prioritization:
        - Priority 1 (Critical): Address relationship risks, overdue follow-ups
        - Priority 2 (High): Growth opportunities with high success probability
        - Priority 3 (Medium): Optimization and efficiency improvements
        - Priority 4 (Low): Strategic enhancements and nice-to-haves
    
    Action Types:
        - Contact specific individuals (with suggested talking points)
        - Attend networking events or industry gatherings
        - Strengthen existing relationships through value-add activities
        - Introduce contacts to each other for mutual benefit
        - Adjust communication frequency or channels
        - Update contact information and relationship context
    
    Returns:
        List of prioritized recommendations with specific action steps,
        expected outcomes, and success tracking metrics
    
    Use Case:
        Essential for daily/weekly networking planning. Provides clear,
        actionable steps to maintain and grow network effectiveness.
        
    Implementation Tip:
        Focus on 3-5 top recommendations per week for sustainable progress.
        Track completion and outcomes to refine future recommendations.
    """
    tenant_id = get_tenant_context(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    health_analytics = analytics_service.get_relationship_health_analytics()
    return health_analytics["recommendations"]