from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from app.models.contact import Contact, ContactInteraction
from app.models.organization import Organization, SocialGroup
from app.models.analytics import DailyNetworkMetric, NetworkingInsight
import json

class DailyMetricsCollector:
    """Service for collecting and calculating daily network metrics"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def collect_daily_metrics(self, target_date: date = None) -> DailyNetworkMetric:
        """Collect and store daily metrics for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        # Check if metrics already exist for this date
        existing_metric = self.db.query(DailyNetworkMetric).filter(
            and_(
                DailyNetworkMetric.tenant_id == self.tenant_id,
                DailyNetworkMetric.metric_date == target_date
            )
        ).first()
        
        if existing_metric:
            # Update existing metrics
            self._update_metrics(existing_metric, target_date)
            return existing_metric
        else:
            # Create new metrics
            return self._create_new_metrics(target_date)
    
    def _create_new_metrics(self, target_date: date) -> DailyNetworkMetric:
        """Create new daily metrics for the given date"""
        # Calculate contact metrics
        total_contacts = self.db.query(Contact).filter(
            Contact.tenant_id == self.tenant_id
        ).count()
        
        active_contacts = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_active == True
            )
        ).count()
        
        # Calculate new contacts added on this date
        new_contacts_added = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                func.date(Contact.created_at) == target_date
            )
        ).count()
        
        # Calculate archived contacts
        contacts_archived = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_archived == True,
                func.date(Contact.updated_at) == target_date
            )
        ).count()
        
        # Calculate relationship strength distribution
        strong_relationships = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.connection_strength >= 7,
                Contact.is_active == True
            )
        ).count()
        
        moderate_relationships = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.connection_strength >= 4,
                Contact.connection_strength < 7,
                Contact.is_active == True
            )
        ).count()
        
        weak_relationships = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.connection_strength < 4,
                Contact.is_active == True
            )
        ).count()
        
        # Calculate average connection strength
        avg_strength_result = self.db.query(func.avg(Contact.connection_strength)).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.is_active == True
            )
        ).scalar()
        avg_connection_strength = float(avg_strength_result or 0)
        
        # Calculate interaction metrics
        total_interactions = self.db.query(ContactInteraction).join(Contact).filter(
            Contact.tenant_id == self.tenant_id
        ).count()
        
        new_interactions = self.db.query(ContactInteraction).join(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                func.date(ContactInteraction.interaction_date) == target_date
            )
        ).count()
        
        # Calculate interaction types breakdown
        interaction_types = {}
        for interaction_type in ['meeting', 'call', 'email', 'text']:
            count = self.db.query(ContactInteraction).join(Contact).filter(
                and_(
                    Contact.tenant_id == self.tenant_id,
                    ContactInteraction.interaction_type == interaction_type,
                    func.date(ContactInteraction.interaction_date) == target_date
                )
            ).count()
            interaction_types[interaction_type] = count
        
        # Calculate follow-up metrics
        overdue_follow_ups = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.next_suggested_contact_date < target_date,
                Contact.is_active == True
            )
        ).count()
        
        pending_follow_ups = self.db.query(Contact).filter(
            and_(
                Contact.tenant_id == self.tenant_id,
                Contact.next_suggested_contact_date >= target_date,
                Contact.is_active == True
            )
        ).count()
        
        # Calculate growth rate (compared to previous day)
        previous_date = target_date - timedelta(days=1)
        previous_metric = self.db.query(DailyNetworkMetric).filter(
            and_(
                DailyNetworkMetric.tenant_id == self.tenant_id,
                DailyNetworkMetric.metric_date == previous_date
            )
        ).first()
        
        network_growth_rate = 0.0
        if previous_metric and previous_metric.total_contacts:
            network_growth_rate = (total_contacts - (previous_metric.total_contacts or 0)) / (previous_metric.total_contacts or 1)
        
        # Calculate engagement rate (interactions per contact)
        engagement_rate = new_interactions / max(active_contacts, 1) if active_contacts > 0 else 0.0
        
        # Create new metric record
        metric = DailyNetworkMetric(
            tenant_id=self.tenant_id,
            metric_date=target_date,
            total_contacts=total_contacts,
            active_contacts=active_contacts,
            new_contacts_added=new_contacts_added,
            contacts_archived=contacts_archived,
            strong_relationships=strong_relationships,
            moderate_relationships=moderate_relationships,
            weak_relationships=weak_relationships,
            avg_connection_strength=avg_connection_strength,
            total_interactions=total_interactions,
            new_interactions=new_interactions,
            interaction_types=interaction_types,
            overdue_follow_ups=overdue_follow_ups,
            pending_follow_ups=pending_follow_ups,
            network_growth_rate=network_growth_rate,
            engagement_rate=engagement_rate,
            response_rate=0.85  # Mock - would calculate from actual data
        )
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        
        return metric
    
    def _update_metrics(self, existing_metric: DailyNetworkMetric, target_date: date):
        """Update existing daily metrics"""
        # For now, just recalculate the metrics
        # In a production system, you might want to be more selective about what to update
        updated_metric = self._create_new_metrics(target_date)
        
        # Copy the updated values to the existing metric
        for attr in ['total_contacts', 'active_contacts', 'new_contacts_added', 'contacts_archived',
                     'strong_relationships', 'moderate_relationships', 'weak_relationships',
                     'avg_connection_strength', 'total_interactions', 'new_interactions',
                     'interaction_types', 'overdue_follow_ups', 'pending_follow_ups',
                     'network_growth_rate', 'engagement_rate', 'response_rate']:
            setattr(existing_metric, attr, getattr(updated_metric, attr))
        
        self.db.delete(updated_metric)  # Remove the temporary metric
        self.db.commit()
    
    def collect_metrics_for_date_range(self, start_date: date, end_date: date) -> List[DailyNetworkMetric]:
        """Collect metrics for a range of dates"""
        metrics = []
        current_date = start_date
        
        while current_date <= end_date:
            metric = self.collect_daily_metrics(current_date)
            metrics.append(metric)
            current_date += timedelta(days=1)
        
        return metrics
    
    def refresh_materialized_view(self):
        """Refresh the contact analytics summary materialized view"""
        try:
            self.db.execute(text("REFRESH MATERIALIZED VIEW contact_analytics_summary"))
            self.db.commit()
        except Exception as e:
            # Handle the case where the view doesn't exist (e.g., in testing)
            self.db.rollback()
            print(f"Could not refresh materialized view: {e}")

class AnalyticsExportService:
    """Service for exporting analytics data in various formats"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def export_analytics_data(self, 
                             export_format: str = "json",
                             date_range: Optional[Dict[str, date]] = None,
                             metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export analytics data in the specified format"""
        
        # Set default date range
        if not date_range:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            date_range = {"start": start_date, "end": end_date}
        
        # Set default metrics
        if not metrics:
            metrics = ["daily_metrics", "contact_summary", "interaction_analytics"]
        
        export_data = {}
        
        # Export daily metrics
        if "daily_metrics" in metrics:
            daily_metrics = self.db.query(DailyNetworkMetric).filter(
                and_(
                    DailyNetworkMetric.tenant_id == self.tenant_id,
                    DailyNetworkMetric.metric_date >= date_range["start"],
                    DailyNetworkMetric.metric_date <= date_range["end"]
                )
            ).order_by(DailyNetworkMetric.metric_date).all()
            
            export_data["daily_metrics"] = [
                {
                    "date": metric.metric_date.isoformat(),
                    "total_contacts": metric.total_contacts,
                    "active_contacts": metric.active_contacts,
                    "new_contacts": metric.new_contacts_added,
                    "strong_relationships": metric.strong_relationships,
                    "moderate_relationships": metric.moderate_relationships,
                    "weak_relationships": metric.weak_relationships,
                    "avg_connection_strength": float(metric.avg_connection_strength or 0),
                    "total_interactions": metric.total_interactions,
                    "new_interactions": metric.new_interactions,
                    "interaction_types": metric.interaction_types,
                    "network_growth_rate": float(metric.network_growth_rate or 0),
                    "engagement_rate": float(metric.engagement_rate or 0)
                }
                for metric in daily_metrics
            ]
        
        # Export contact summary
        if "contact_summary" in metrics:
            contacts = self.db.query(Contact).filter(
                Contact.tenant_id == self.tenant_id
            ).all()
            
            export_data["contact_summary"] = [
                {
                    "id": contact.id,
                    "name": f"{contact.first_name} {contact.last_name}",
                    "email": contact.email,
                    "connection_strength": float(contact.connection_strength or 0),
                    "networking_value": contact.networking_value,
                    "total_interactions": contact.total_interactions,
                    "last_meaningful_interaction": contact.last_meaningful_interaction.isoformat() if contact.last_meaningful_interaction else None,
                    "is_active": contact.is_active,
                    "created_at": contact.created_at.isoformat() if contact.created_at else None
                }
                for contact in contacts
            ]
        
        # Export interaction analytics
        if "interaction_analytics" in metrics:
            interactions = self.db.query(ContactInteraction).join(Contact).filter(
                and_(
                    Contact.tenant_id == self.tenant_id,
                    ContactInteraction.interaction_date >= datetime.combine(date_range["start"], datetime.min.time()),
                    ContactInteraction.interaction_date <= datetime.combine(date_range["end"], datetime.max.time())
                )
            ).all()
            
            export_data["interaction_analytics"] = [
                {
                    "id": interaction.id,
                    "contact_id": interaction.contact_id,
                    "interaction_type": interaction.interaction_type,
                    "interaction_date": interaction.interaction_date.isoformat(),
                    "duration_minutes": interaction.duration_minutes,
                    "interaction_quality": float(interaction.interaction_quality or 0),
                    "initiated_by": interaction.initiated_by,
                    "title": interaction.title,
                    "description": interaction.description
                }
                for interaction in interactions
            ]
        
        # Add metadata
        export_data["metadata"] = {
            "tenant_id": self.tenant_id,
            "export_date": datetime.now().isoformat(),
            "date_range": {
                "start": date_range["start"].isoformat(),
                "end": date_range["end"].isoformat()
            },
            "metrics_included": metrics,
            "format": export_format,
            "total_records": sum(len(data) if isinstance(data, list) else 1 for key, data in export_data.items() if key != "metadata")
        }
        
        return export_data
    
    def export_custom_report(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom analytics report based on configuration"""
        report_type = report_config.get("report_type", "summary")
        date_range = report_config.get("date_range", {})
        filters = report_config.get("filters", {})
        
        if report_type == "relationship_health":
            return self._generate_relationship_health_report(date_range, filters)
        elif report_type == "network_growth":
            return self._generate_network_growth_report(date_range, filters)
        elif report_type == "interaction_patterns":
            return self._generate_interaction_patterns_report(date_range, filters)
        else:
            return self._generate_summary_report(date_range, filters)
    
    def _generate_relationship_health_report(self, date_range: Dict[str, date], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a relationship health focused report"""
        contacts = self.db.query(Contact).filter(
            Contact.tenant_id == self.tenant_id,
            Contact.is_active == True
        )
        
        # Apply filters
        if filters.get("min_connection_strength"):
            contacts = contacts.filter(Contact.connection_strength >= filters["min_connection_strength"])
        
        contacts = contacts.all()
        
        # Calculate health metrics
        total_contacts = len(contacts)
        strong_relationships = sum(1 for c in contacts if c.connection_strength and c.connection_strength >= 7)
        at_risk_relationships = sum(1 for c in contacts if c.connection_strength and c.connection_strength < 4)
        
        return {
            "report_type": "relationship_health",
            "summary": {
                "total_contacts": total_contacts,
                "strong_relationships": strong_relationships,
                "at_risk_relationships": at_risk_relationships,
                "health_score": (strong_relationships / max(total_contacts, 1)) * 10
            },
            "details": [
                {
                    "contact_id": c.id,
                    "name": f"{c.first_name} {c.last_name}",
                    "connection_strength": float(c.connection_strength or 0),
                    "health_status": (
                        "strong" if c.connection_strength and c.connection_strength >= 7 else
                        "moderate" if c.connection_strength and c.connection_strength >= 4 else
                        "at_risk"
                    ),
                    "last_interaction": c.last_meaningful_interaction.isoformat() if c.last_meaningful_interaction else None
                }
                for c in contacts
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_network_growth_report(self, date_range: Dict[str, date], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a network growth focused report"""
        # Get daily metrics for the period
        if not date_range:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = date_range.get("start", date.today() - timedelta(days=30))
            end_date = date_range.get("end", date.today())
        
        metrics = self.db.query(DailyNetworkMetric).filter(
            and_(
                DailyNetworkMetric.tenant_id == self.tenant_id,
                DailyNetworkMetric.metric_date >= start_date,
                DailyNetworkMetric.metric_date <= end_date
            )
        ).order_by(DailyNetworkMetric.metric_date).all()
        
        if not metrics:
            return {"report_type": "network_growth", "error": "No data available for the specified period"}
        
        # Calculate growth metrics
        first_metric = metrics[0]
        last_metric = metrics[-1]
        
        total_growth = (last_metric.total_contacts or 0) - (first_metric.total_contacts or 0)
        period_days = (end_date - start_date).days
        daily_growth_rate = total_growth / max(period_days, 1)
        
        return {
            "report_type": "network_growth",
            "summary": {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "total_growth": total_growth,
                "daily_avg_growth": daily_growth_rate,
                "growth_percentage": (total_growth / max(first_metric.total_contacts or 1, 1)) * 100
            },
            "timeline": [
                {
                    "date": m.metric_date.isoformat(),
                    "total_contacts": m.total_contacts,
                    "new_contacts": m.new_contacts_added,
                    "growth_rate": float(m.network_growth_rate or 0)
                }
                for m in metrics
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_interaction_patterns_report(self, date_range: Dict[str, date], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an interaction patterns focused report"""
        # Implementation for interaction patterns report
        return {
            "report_type": "interaction_patterns",
            "summary": {"message": "Interaction patterns report - implementation pending"},
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_summary_report(self, date_range: Dict[str, date], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a general summary report"""
        return {
            "report_type": "summary",
            "summary": {"message": "Summary report - implementation pending"},
            "generated_at": datetime.now().isoformat()
        }