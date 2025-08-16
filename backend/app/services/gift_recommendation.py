from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, extract
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.models.gift import Gift, GiftIdea, GiftStatus, GiftPriority
from app.models.contact import Contact
from app.crud import gift as gift_crud


class GiftRecommendationService:
    """Service for generating gift recommendations and analytics"""
    
    def __init__(self, db: Session, user_id: int, tenant_id: int):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id
    
    def get_upcoming_occasions(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming gift occasions from contact information and existing gifts"""
        end_date = date.today() + timedelta(days=days_ahead)
        
        # Get gifts with upcoming occasion dates
        upcoming_gifts = self.db.query(Gift).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.occasion_date >= date.today(),
            Gift.occasion_date <= end_date,
            Gift.is_active == True
        ).order_by(Gift.occasion_date).all()
        
        occasions = []
        for gift in upcoming_gifts:
            occasions.append({
                "date": gift.occasion_date,
                "occasion": gift.occasion,
                "recipient_name": gift.recipient_name,
                "recipient_contact_id": gift.recipient_contact_id,
                "gift_id": gift.id,
                "gift_title": gift.title,
                "status": gift.status,
                "days_until": (gift.occasion_date - date.today()).days if gift.occasion_date else None
            })
        
        return occasions
    
    def get_gift_suggestions_for_contact(
        self,
        contact_id: int,
        occasion: Optional[str] = None,
        budget_max: Optional[Decimal] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get gift suggestions for a specific contact based on history and preferences"""
        
        # Get existing gift ideas for this contact
        contact_ideas = gift_crud.get_gift_ideas_for_contact(
            self.db,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            contact_id=contact_id,
            limit=limit
        )
        
        suggestions = []
        for idea in contact_ideas:
            # Filter by occasion if specified
            if occasion and occasion not in idea.suitable_occasions:
                continue
                
            # Filter by budget if specified
            if budget_max and idea.price_range_min and idea.price_range_min > budget_max:
                continue
                
            suggestions.append({
                "idea_id": idea.id,
                "title": idea.title,
                "description": idea.description,
                "category": idea.category,
                "price_range_min": float(idea.price_range_min) if idea.price_range_min else None,
                "price_range_max": float(idea.price_range_max) if idea.price_range_max else None,
                "rating": idea.rating,
                "times_gifted": idea.times_gifted,
                "suitable_occasions": idea.suitable_occasions,
                "tags": idea.tags,
                "recommendation_reason": self._get_recommendation_reason(idea, contact_id, occasion)
            })
        
        # If we don't have enough contact-specific ideas, get general suggestions
        if len(suggestions) < limit:
            general_ideas = self._get_general_gift_suggestions(
                occasion=occasion,
                budget_max=budget_max,
                exclude_ids=[s["idea_id"] for s in suggestions],
                limit=limit - len(suggestions)
            )
            suggestions.extend(general_ideas)
        
        return suggestions[:limit]
    
    def _get_recommendation_reason(
        self,
        idea: GiftIdea,
        contact_id: int,
        occasion: Optional[str] = None
    ) -> str:
        """Generate a reason for why this gift is recommended"""
        reasons = []
        
        if idea.target_contact_id == contact_id:
            reasons.append("specifically chosen for this contact")
        
        if occasion and occasion in idea.suitable_occasions:
            reasons.append(f"perfect for {occasion}")
        
        if idea.rating and idea.rating >= 4:
            reasons.append(f"highly rated ({idea.rating}/5 stars)")
        
        if idea.times_gifted > 0:
            reasons.append(f"successfully gifted {idea.times_gifted} time(s)")
        
        if not reasons:
            reasons.append("matches your preferences")
        
        return "; ".join(reasons)
    
    def _get_general_gift_suggestions(
        self,
        occasion: Optional[str] = None,
        budget_max: Optional[Decimal] = None,
        exclude_ids: List[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get general gift suggestions based on user's gift history"""
        query = self.db.query(GiftIdea).filter(
            GiftIdea.user_id == self.user_id,
            GiftIdea.tenant_id == self.tenant_id,
            GiftIdea.is_active == True
        )
        
        if exclude_ids:
            query = query.filter(~GiftIdea.id.in_(exclude_ids))
        
        if budget_max:
            query = query.filter(
                (GiftIdea.price_range_min.is_(None)) |
                (GiftIdea.price_range_min <= budget_max)
            )
        
        # Order by rating and popularity
        ideas = query.order_by(
            desc(GiftIdea.rating),
            desc(GiftIdea.times_gifted),
            desc(GiftIdea.created_at)
        ).limit(limit).all()
        
        suggestions = []
        for idea in ideas:
            if occasion and occasion not in idea.suitable_occasions:
                continue
                
            suggestions.append({
                "idea_id": idea.id,
                "title": idea.title,
                "description": idea.description,
                "category": idea.category,
                "price_range_min": float(idea.price_range_min) if idea.price_range_min else None,
                "price_range_max": float(idea.price_range_max) if idea.price_range_max else None,
                "rating": idea.rating,
                "times_gifted": idea.times_gifted,
                "suitable_occasions": idea.suitable_occasions,
                "tags": idea.tags,
                "recommendation_reason": "based on your gift preferences"
            })
        
        return suggestions
    
    def get_budget_insights(self) -> Dict[str, Any]:
        """Get budget insights for gift planning"""
        
        # Calculate spending by category
        category_spending = self.db.query(
            Gift.category,
            func.sum(Gift.actual_amount).label('total_spent'),
            func.avg(Gift.actual_amount).label('avg_spent'),
            func.count(Gift.id).label('gift_count')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.actual_amount.isnot(None),
            Gift.category.isnot(None)
        ).group_by(Gift.category).all()
        
        # Calculate spending by occasion
        occasion_spending = self.db.query(
            Gift.occasion,
            func.sum(Gift.actual_amount).label('total_spent'),
            func.avg(Gift.actual_amount).label('avg_spent'),
            func.count(Gift.id).label('gift_count')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.actual_amount.isnot(None),
            Gift.occasion.isnot(None)
        ).group_by(Gift.occasion).all()
        
        # Calculate monthly spending trend
        monthly_spending = self.db.query(
            extract('year', Gift.purchase_date).label('year'),
            extract('month', Gift.purchase_date).label('month'),
            func.sum(Gift.actual_amount).label('total_spent'),
            func.count(Gift.id).label('gift_count')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.actual_amount.isnot(None),
            Gift.purchase_date.isnot(None)
        ).group_by(
            extract('year', Gift.purchase_date),
            extract('month', Gift.purchase_date)
        ).order_by(
            extract('year', Gift.purchase_date),
            extract('month', Gift.purchase_date)
        ).all()
        
        return {
            "spending_by_category": [
                {
                    "category": row.category,
                    "total_spent": float(row.total_spent),
                    "average_spent": float(row.avg_spent),
                    "gift_count": row.gift_count
                }
                for row in category_spending
            ],
            "spending_by_occasion": [
                {
                    "occasion": row.occasion,
                    "total_spent": float(row.total_spent),
                    "average_spent": float(row.avg_spent),
                    "gift_count": row.gift_count
                }
                for row in occasion_spending
            ],
            "monthly_trend": [
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "total_spent": float(row.total_spent),
                    "gift_count": row.gift_count
                }
                for row in monthly_spending
            ]
        }
    
    def get_gift_giving_patterns(self) -> Dict[str, Any]:
        """Analyze gift-giving patterns and preferences"""
        
        # Most popular categories
        popular_categories = self.db.query(
            Gift.category,
            func.count(Gift.id).label('count')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.category.isnot(None)
        ).group_by(Gift.category).order_by(desc(func.count(Gift.id))).limit(5).all()
        
        # Most frequent occasions
        popular_occasions = self.db.query(
            Gift.occasion,
            func.count(Gift.id).label('count')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.occasion.isnot(None)
        ).group_by(Gift.occasion).order_by(desc(func.count(Gift.id))).limit(5).all()
        
        # Average planning time (days between creation and occasion)
        planning_time_data = self.db.query(
            Gift.occasion_date,
            Gift.created_at
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.occasion_date.isnot(None)
        ).all()
        
        planning_times = []
        for gift in planning_time_data:
            if gift.occasion_date and gift.created_at:
                days_ahead = (gift.occasion_date - gift.created_at.date()).days
                if days_ahead >= 0:  # Only count future planning
                    planning_times.append(days_ahead)
        
        avg_planning_time = sum(planning_times) / len(planning_times) if planning_times else 0
        
        return {
            "popular_categories": [
                {"category": row.category, "count": row.count}
                for row in popular_categories
            ],
            "popular_occasions": [
                {"occasion": row.occasion, "count": row.count}
                for row in popular_occasions
            ],
            "planning_insights": {
                "average_planning_days": round(avg_planning_time, 1),
                "total_gifts_analyzed": len(planning_times),
                "recommendation": self._get_planning_recommendation(avg_planning_time)
            }
        }
    
    def _get_planning_recommendation(self, avg_days: float) -> str:
        """Get planning recommendation based on average planning time"""
        if avg_days < 7:
            return "Consider planning gifts further in advance for better selection and pricing"
        elif avg_days < 30:
            return "Good planning timeframe! You typically plan gifts with adequate time"
        else:
            return "Excellent planning! You give yourself plenty of time for thoughtful gift selection"
    
    def get_reminder_suggestions(self, days_ahead: int = 60) -> List[Dict[str, Any]]:
        """Get suggestions for setting up gift reminders"""
        
        upcoming_occasions = self.get_upcoming_occasions(days_ahead)
        suggestions = []
        
        for occasion in upcoming_occasions:
            if occasion["status"] in [GiftStatus.IDEA.value, GiftStatus.PLANNED.value]:
                days_until = occasion["days_until"]
                
                # Suggest reminder timing based on planning patterns
                if days_until > 30:
                    reminder_date = date.today() + timedelta(days=days_until - 14)
                    suggestion_type = "Start planning reminder"
                elif days_until > 7:
                    reminder_date = date.today() + timedelta(days=days_until - 7)
                    suggestion_type = "Purchase reminder"
                else:
                    reminder_date = date.today() + timedelta(days=max(0, days_until - 2))
                    suggestion_type = "Urgent purchase reminder"
                
                suggestions.append({
                    "gift_id": occasion["gift_id"],
                    "occasion_date": occasion["date"],
                    "occasion": occasion["occasion"],
                    "recipient_name": occasion["recipient_name"],
                    "reminder_type": suggestion_type,
                    "suggested_reminder_date": reminder_date,
                    "days_until_occasion": days_until,
                    "priority": "high" if days_until <= 7 else "medium"
                })
        
        return suggestions