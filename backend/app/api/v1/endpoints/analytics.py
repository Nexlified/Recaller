from typing import Dict, Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
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

router = APIRouter()

def get_tenant_id(request: Request) -> int:
    """Get tenant ID from request state"""
    return getattr(request.state, 'tenant_id', 1)

@router.get("/overview", response_model=Dict[str, Any])
def get_analytics_overview(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get high-level dashboard metrics"""
    tenant_id = get_tenant_id(request)
    analytics_service = AnalyticsService(db, tenant_id)
    return analytics_service.get_overview_analytics()

@router.get("/summary", response_model=Dict[str, Any])
def get_analytics_summary(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get quick summary statistics"""
    tenant_id = get_tenant_id(request)
    
    # Get summary from materialized view
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
    """Get trending metrics over time"""
    tenant_id = get_tenant_id(request)
    
    # Get daily metrics for the period
    end_date = date.today()
    start_date = date.fromordinal(end_date.toordinal() - period)
    
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
    """Get key performance indicators"""
    tenant_id = get_tenant_id(request)
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

# Network Analytics Endpoints
@router.get("/network/overview", response_model=Dict[str, Any])
def get_network_overview(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get network size, strength, growth overview"""
    tenant_id = get_tenant_id(request)
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
    """Get relationship strength distribution"""
    tenant_id = get_tenant_id(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    health_analytics = analytics_service.get_relationship_health_analytics()
    return health_analytics["overall_health"]["distribution"]

@router.get("/network/growth", response_model=Dict[str, Any])
def get_network_growth(
    request: Request,
    period: int = Query(default=90, ge=30, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get network growth over time"""
    tenant_id = get_tenant_id(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    return analytics_service.get_network_growth_analytics(period)

@router.get("/network/health", response_model=Dict[str, Any])
def get_network_health(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get overall network health score"""
    tenant_id = get_tenant_id(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    return analytics_service.get_relationship_health_analytics()

# Interaction Analytics Endpoints
@router.get("/interactions/overview", response_model=Dict[str, Any])
def get_interactions_overview(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get interaction patterns and trends"""
    tenant_id = get_tenant_id(request)
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
    """Get breakdown by interaction type"""
    tenant_id = get_tenant_id(request)
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
    """Get interaction quality trends"""
    tenant_id = get_tenant_id(request)
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
    """Get interaction frequency analysis"""
    tenant_id = get_tenant_id(request)
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
    """Get contact response patterns"""
    tenant_id = get_tenant_id(request)
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
    tenant_id = get_tenant_id(request)
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
    tenant_id = get_tenant_id(request)
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
    tenant_id = get_tenant_id(request)
    
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
    tenant_id = get_tenant_id(request)
    
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
    tenant_id = get_tenant_id(request)
    
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

# Insights & Recommendations
@router.get("/insights", response_model=List[Dict[str, Any]])
def get_networking_insights(
    request: Request,
    limit: int = Query(default=10, ge=1, le=50),
    insight_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get AI-generated insights"""
    tenant_id = get_tenant_id(request)
    
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
    """Trigger insight generation"""
    tenant_id = get_tenant_id(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    insights = analytics_service.generate_insights(insight_request.insight_types)
    
    # Save generated insights to database
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

@router.get("/recommendations", response_model=List[Dict[str, Any]])
def get_actionable_recommendations(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get actionable recommendations"""
    tenant_id = get_tenant_id(request)
    analytics_service = AnalyticsService(db, tenant_id)
    
    health_analytics = analytics_service.get_relationship_health_analytics()
    return health_analytics["recommendations"]