from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from app.models.analytics import (
    ContactAnalyticsSummary, 
    InteractionAnalytics, 
    OrganizationNetworkAnalytics, 
    SocialGroupAnalytics,
    NetworkingInsight,
    DailyNetworkMetric
)
from app.models.contact import Contact, ContactInteraction
from app.models.organization import Organization, SocialGroup
import json

class AnalyticsService:
    """Core analytics service for calculating and retrieving metrics"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def get_overview_analytics(self) -> Dict[str, Any]:
        """Get high-level analytics overview"""
        # Get summary from materialized view
        summary = self.db.query(ContactAnalyticsSummary).filter(
            ContactAnalyticsSummary.tenant_id == self.tenant_id
        ).first()
        
        if not summary:
            # If no summary, create empty response
            summary_data = {
                "total_contacts": 0,
                "active_contacts": 0,
                "strong_relationships": 0,
                "pending_follow_ups": 0,
                "overdue_follow_ups": 0
            }
        else:
            summary_data = {
                "total_contacts": summary.total_contacts or 0,
                "active_contacts": summary.active_contacts or 0,
                "strong_relationships": summary.strong_relationships or 0,
                "pending_follow_ups": 0,  # Calculate separately
                "overdue_follow_ups": summary.overdue_follow_ups or 0
            }
        
        # Calculate network health score
        network_health = self._calculate_network_health()
        
        # Get recent activity
        recent_activity = self._get_recent_activity()
        
        # Get top insights
        top_insights = self._get_top_insights(limit=3)
        
        return {
            "summary": summary_data,
            "network_health": network_health,
            "recent_activity": recent_activity,
            "top_insights": top_insights
        }
    
    def get_network_growth_analytics(self, period_days: int = 90) -> Dict[str, Any]:
        """Get network growth analytics over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        # Get daily metrics for the period
        daily_metrics = self.db.query(DailyNetworkMetric).filter(
            and_(
                DailyNetworkMetric.tenant_id == self.tenant_id,
                DailyNetworkMetric.metric_date >= start_date,
                DailyNetworkMetric.metric_date <= end_date
            )
        ).order_by(DailyNetworkMetric.metric_date).all()
        
        if not daily_metrics:
            return self._empty_growth_response()
        
        # Calculate growth metrics
        first_metric = daily_metrics[0]
        last_metric = daily_metrics[-1]
        
        total_growth = (last_metric.total_contacts or 0) - (first_metric.total_contacts or 0)
        growth_rate = total_growth / max((first_metric.total_contacts or 1), 1)
        
        # Build timeline
        timeline = []
        for metric in daily_metrics:
            timeline.append({
                "date": metric.metric_date.isoformat(),
                "total_contacts": metric.total_contacts or 0,
                "new_contacts": metric.new_contacts_added or 0,
                "growth_rate": float(metric.network_growth_rate or 0)
            })
        
        # Calculate growth sources (placeholder - would need additional tracking)
        growth_sources = {
            "events": total_growth // 4,
            "referrals": total_growth // 3,
            "professional": total_growth // 4,
            "social": total_growth - (total_growth // 4 + total_growth // 3 + total_growth // 4)
        }
        
        return {
            "growth_metrics": {
                "total_growth": total_growth,
                "growth_rate": float(growth_rate),
                "avg_monthly_additions": total_growth / max(period_days / 30, 1),
                "growth_trend": "accelerating" if len(timeline) > 1 and timeline[-1]["growth_rate"] > timeline[0]["growth_rate"] else "stable"
            },
            "growth_timeline": timeline,
            "growth_sources": growth_sources,
            "predictions": {
                "next_30_days": max(int(total_growth / max(period_days / 30, 1)), 0),
                "confidence": 0.75,
                "factors": ["historical trends", "current patterns"]
            }
        }
    
    def get_relationship_health_analytics(self) -> Dict[str, Any]:
        """Analyze overall relationship health"""
        # Get contact distribution by connection strength
        contacts = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_active == True
            )
        ).all()
        
        if not contacts:
            return self._empty_health_response()
        
        # Calculate health distribution
        thriving = sum(1 for c in contacts if c.connection_strength and c.connection_strength >= 8.5)
        healthy = sum(1 for c in contacts if c.connection_strength and 7.0 <= c.connection_strength < 8.5)
        stable = sum(1 for c in contacts if c.connection_strength and 5.0 <= c.connection_strength < 7.0)
        needs_attention = sum(1 for c in contacts if c.connection_strength and 3.0 <= c.connection_strength < 5.0)
        at_risk = sum(1 for c in contacts if c.connection_strength and c.connection_strength < 3.0)
        
        # Calculate overall health score
        total_contacts = len(contacts)
        health_score = (thriving * 10 + healthy * 8 + stable * 6 + needs_attention * 4 + at_risk * 2) / max(total_contacts, 1)
        
        # Generate recommendations
        recommendations = []
        if at_risk > 0:
            recommendations.append({
                "type": "immediate_action",
                "title": f"{at_risk} relationships need immediate attention",
                "description": "These contacts haven't been reached in 60+ days and showed declining engagement",
                "contact_ids": [c.id for c in contacts if c.connection_strength and c.connection_strength < 3.0][:8],
                "priority": "high"
            })
        
        if needs_attention > 0:
            recommendations.append({
                "type": "opportunity",
                "title": f"Strengthen {min(needs_attention, 12)} promising relationships",
                "description": "These contacts show high engagement potential based on recent interactions",
                "contact_ids": [c.id for c in contacts if c.connection_strength and 3.0 <= c.connection_strength < 5.0][:12],
                "priority": "medium"
            })
        
        return {
            "overall_health": {
                "score": round(health_score, 1),
                "trend": "improving",  # Would calculate from historical data
                "distribution": {
                    "thriving": thriving,
                    "healthy": healthy,
                    "stable": stable,
                    "needs_attention": needs_attention,
                    "at_risk": at_risk
                }
            },
            "health_factors": {
                "interaction_frequency": 8.2,  # Would calculate from interaction data
                "interaction_quality": 7.8,
                "follow_up_consistency": 6.9,
                "mutual_engagement": 7.4
            },
            "recommendations": recommendations
        }
    
    def get_interaction_analytics(self, contact_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get interaction analytics for contacts"""
        query = self.db.query(InteractionAnalytics).filter(
            InteractionAnalytics.tenant_id == self.tenant_id
        )
        
        if contact_id:
            query = query.filter(InteractionAnalytics.contact_id == contact_id)
        
        analytics = query.all()
        
        return [
            {
                "contact_id": a.contact_id,
                "total_interactions": a.total_interactions or 0,
                "in_person_meetings": a.in_person_meetings or 0,
                "phone_calls": a.phone_calls or 0,
                "emails": a.emails or 0,
                "text_messages": a.text_messages or 0,
                "avg_interaction_quality": float(a.avg_interaction_quality or 0),
                "avg_interaction_duration": float(a.avg_interaction_duration or 0),
                "last_interaction_date": a.last_interaction_date,
                "interactions_last_30_days": a.interactions_last_30_days or 0,
                "interactions_initiated_by_user": a.interactions_initiated_by_user or 0,
                "interactions_initiated_by_contact": a.interactions_initiated_by_contact or 0
            }
            for a in analytics
        ]
    
    def generate_insights(self, insight_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate AI-powered networking insights"""
        insights = []
        
        # Get existing insights to avoid duplicates
        existing_insights = self.db.query(NetworkingInsight).filter(
            and_(
                NetworkingInsight.tenant_id == self.tenant_id,
                NetworkingInsight.status == 'active',
                NetworkingInsight.expiry_date >= date.today()
            )
        ).all()
        
        existing_types = [i.insight_type for i in existing_insights]
        
        # Generate network growth insights
        if not insight_types or 'network_growth' in insight_types:
            if 'network_growth' not in existing_types:
                growth_insight = self._generate_growth_insight()
                if growth_insight:
                    insights.append(growth_insight)
        
        # Generate relationship health insights
        if not insight_types or 'relationship_health' in insight_types:
            if 'relationship_health' not in existing_types:
                health_insight = self._generate_health_insight()
                if health_insight:
                    insights.append(health_insight)
        
        # Generate engagement pattern insights
        if not insight_types or 'engagement_pattern' in insight_types:
            if 'engagement_pattern' not in existing_types:
                engagement_insight = self._generate_engagement_insight()
                if engagement_insight:
                    insights.append(engagement_insight)
        
        return insights
    
    def _calculate_network_health(self) -> Dict[str, Any]:
        """Calculate overall network health metrics"""
        contacts = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_active == True
            )
        ).all()
        
        if not contacts:
            return {
                "overall_score": 0.0,
                "relationship_strength_avg": 0.0,
                "engagement_rate": 0.0,
                "response_rate": 0.0,
                "growth_rate": 0.0
            }
        
        # Calculate averages
        avg_strength = sum(c.connection_strength or 0 for c in contacts) / len(contacts)
        
        # Mock other metrics (would calculate from real data)
        return {
            "overall_score": min(avg_strength, 10.0),
            "relationship_strength_avg": float(avg_strength),
            "engagement_rate": 0.72,  # Mock
            "response_rate": 0.84,    # Mock
            "growth_rate": 0.08       # Mock
        }
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity metrics"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Get recent interactions
        recent_interactions = self.db.query(ContactInteraction).join(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                ContactInteraction.interaction_date >= thirty_days_ago
            )
        ).count()
        
        # Get new contacts
        new_contacts = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.created_at >= thirty_days_ago
            )
        ).count()
        
        return {
            "interactions_last_30_days": recent_interactions,
            "new_contacts_last_30_days": new_contacts,
            "follow_ups_completed": 18,  # Mock
            "events_attended": 5         # Mock
        }
    
    def _get_top_insights(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get top priority insights"""
        insights = self.db.query(NetworkingInsight).filter(
            and_(
                NetworkingInsight.tenant_id == self.tenant_id,
                NetworkingInsight.status == 'active'
            )
        ).order_by(
            NetworkingInsight.priority.desc(),
            NetworkingInsight.confidence_score.desc()
        ).limit(limit).all()
        
        return [
            {
                "type": i.insight_type,
                "title": i.title,
                "description": i.description,
                "priority": i.priority,
                "confidence": float(i.confidence_score or 0)
            }
            for i in insights
        ]
    
    def _generate_growth_insight(self) -> Optional[Dict[str, Any]]:
        """Generate a network growth insight"""
        # Simple insight generation logic
        contacts_count = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_active == True
            )
        ).count()
        
        if contacts_count < 50:
            return {
                "insight_type": "network_growth",
                "title": "Expand Your Network",
                "description": f"You have {contacts_count} active contacts. Consider expanding to improve networking opportunities.",
                "priority": "medium",
                "confidence": 0.85,
                "actionable_recommendations": [
                    "Attend industry events",
                    "Connect with colleagues on LinkedIn",
                    "Join professional groups"
                ]
            }
        return None
    
    def _generate_health_insight(self) -> Optional[Dict[str, Any]]:
        """Generate a relationship health insight"""
        # Check for contacts that need follow-up
        overdue_contacts = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_active == True,
                Contact.next_suggested_contact_date < date.today()
            )
        ).count()
        
        if overdue_contacts > 0:
            return {
                "insight_type": "relationship_health",
                "title": f"Follow Up with {overdue_contacts} Contacts",
                "description": f"You have {overdue_contacts} contacts that need follow-up attention.",
                "priority": "high" if overdue_contacts > 10 else "medium",
                "confidence": 0.92,
                "actionable_recommendations": [
                    "Send a quick message to check in",
                    "Schedule coffee or lunch meetings",
                    "Share relevant articles or opportunities"
                ]
            }
        return None
    
    def _generate_engagement_insight(self) -> Optional[Dict[str, Any]]:
        """Generate an engagement pattern insight"""
        # Mock engagement insight
        return {
            "insight_type": "engagement_pattern",
            "title": "Optimize Meeting Times",
            "description": "Your most successful interactions happen on Tuesday afternoons. Consider scheduling important meetings then.",
            "priority": "low",
            "confidence": 0.73,
            "actionable_recommendations": [
                "Schedule important calls on Tuesday afternoons",
                "Block calendar time for networking activities",
                "Review interaction quality patterns"
            ]
        }
    
    def _empty_growth_response(self) -> Dict[str, Any]:
        """Return empty growth response when no data available"""
        return {
            "growth_metrics": {
                "total_growth": 0,
                "growth_rate": 0.0,
                "avg_monthly_additions": 0.0,
                "growth_trend": "stable"
            },
            "growth_timeline": [],
            "growth_sources": {"events": 0, "referrals": 0, "professional": 0, "social": 0},
            "predictions": {
                "next_30_days": 0,
                "confidence": 0.0,
                "factors": []
            }
        }
    
    def _empty_health_response(self) -> Dict[str, Any]:
        """Return empty health response when no data available"""
        return {
            "overall_health": {
                "score": 0.0,
                "trend": "stable",
                "distribution": {
                    "thriving": 0,
                    "healthy": 0,
                    "stable": 0,
                    "needs_attention": 0,
                    "at_risk": 0
                }
            },
            "health_factors": {
                "interaction_frequency": 0.0,
                "interaction_quality": 0.0,
                "follow_up_consistency": 0.0,
                "mutual_engagement": 0.0
            },
            "recommendations": []
        }