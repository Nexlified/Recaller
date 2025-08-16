from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.gift import Gift, GiftIdea, GiftStatus
from app.models.contact import Contact
from app.crud import gift as gift_crud


class GiftIntegrationService:
    """Service for integrating gifts with other systems (contacts, reminders, financial)"""
    
    def __init__(self, db: Session, user_id: int, tenant_id: int):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id
    
    def create_gift_from_contact_occasion(
        self,
        contact_id: int,
        occasion: str,
        occasion_date: date,
        budget_amount: Optional[float] = None
    ) -> Optional[Gift]:
        """Create a gift based on a contact's upcoming occasion"""
        
        # Get contact information
        contact = self.db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.tenant_id == self.tenant_id
        ).first()
        
        if not contact:
            return None
        
        # Create gift with contact information
        from app.schemas.gift_system import GiftCreate
        from decimal import Decimal
        
        gift_data = GiftCreate(
            title=f"{occasion.title()} gift for {contact.first_name}",
            description=f"Gift for {contact.first_name} {contact.last_name or ''}".strip(),
            recipient_contact_id=contact_id,
            recipient_name=f"{contact.first_name} {contact.last_name or ''}".strip(),
            occasion=occasion,
            occasion_date=occasion_date,
            budget_amount=Decimal(str(budget_amount)) if budget_amount else None,
            status=GiftStatus.IDEA.value
        )
        
        gift = gift_crud.create_gift(
            db=self.db,
            obj_in=gift_data,
            user_id=self.user_id,
            tenant_id=self.tenant_id
        )
        
        return gift
    
    def get_contacts_with_gifts(self) -> List[Dict[str, Any]]:
        """Get contacts and their associated gifts for relationship insights"""
        
        # Get all contacts for the user's tenant
        contacts = self.db.query(Contact).filter(
            Contact.tenant_id == self.tenant_id,
            Contact.is_active == True
        ).all()
        
        contact_gift_data = []
        
        for contact in contacts:
            # Get gifts for this contact
            gifts = gift_crud.get_gifts_by_recipient(
                self.db,
                user_id=self.user_id,
                tenant_id=self.tenant_id,
                recipient_contact_id=contact.id
            )
            
            # Get gift ideas for this contact
            ideas = gift_crud.get_gift_ideas_for_contact(
                self.db,
                user_id=self.user_id,
                tenant_id=self.tenant_id,
                contact_id=contact.id
            )
            
            contact_gift_data.append({
                "contact_id": contact.id,
                "contact_name": f"{contact.first_name} {contact.last_name or ''}".strip(),
                "contact_email": contact.email,
                "total_gifts": len(gifts),
                "total_ideas": len(ideas),
                "recent_gifts": [
                    {
                        "id": gift.id,
                        "title": gift.title,
                        "occasion": gift.occasion,
                        "occasion_date": gift.occasion_date,
                        "status": gift.status,
                        "amount": float(gift.actual_amount) if gift.actual_amount else None
                    }
                    for gift in gifts[:3]  # Last 3 gifts
                ],
                "gift_ideas_count": len([idea for idea in ideas if idea.is_active])
            })
        
        return contact_gift_data
    
    def get_financial_summary(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get financial summary of gift spending for integration with financial systems"""
        
        from sqlalchemy import func, extract
        
        query = self.db.query(
            func.sum(Gift.actual_amount).label('total_spent'),
            func.sum(Gift.budget_amount).label('total_budgeted'),
            func.count(Gift.id).label('total_gifts'),
            func.avg(Gift.actual_amount).label('avg_spent')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.actual_amount.isnot(None)
        )
        
        if year:
            query = query.filter(extract('year', Gift.purchase_date) == year)
        
        result = query.first()
        
        # Get spending by month for the year
        monthly_query = self.db.query(
            extract('month', Gift.purchase_date).label('month'),
            func.sum(Gift.actual_amount).label('spent'),
            func.count(Gift.id).label('count')
        ).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.is_active == True,
            Gift.actual_amount.isnot(None),
            Gift.purchase_date.isnot(None)
        )
        
        if year:
            monthly_query = monthly_query.filter(extract('year', Gift.purchase_date) == year)
        
        monthly_data = monthly_query.group_by(extract('month', Gift.purchase_date)).all()
        
        return {
            "summary": {
                "total_spent": float(result.total_spent or 0),
                "total_budgeted": float(result.total_budgeted or 0),
                "total_gifts": result.total_gifts or 0,
                "average_spent": float(result.avg_spent or 0),
                "budget_variance": float((result.total_budgeted or 0) - (result.total_spent or 0))
            },
            "monthly_breakdown": [
                {
                    "month": int(row.month),
                    "spent": float(row.spent),
                    "gift_count": row.count
                }
                for row in monthly_data
            ],
            "year": year or date.today().year
        }
    
    def get_reminder_data(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get gift reminder data for integration with reminder systems"""
        
        end_date = date.today() + timedelta(days=days_ahead)
        
        # Get gifts with upcoming occasions
        upcoming_gifts = self.db.query(Gift).filter(
            Gift.user_id == self.user_id,
            Gift.tenant_id == self.tenant_id,
            Gift.occasion_date >= date.today(),
            Gift.occasion_date <= end_date,
            Gift.is_active == True,
            Gift.status.in_([GiftStatus.IDEA.value, GiftStatus.PLANNED.value])
        ).order_by(Gift.occasion_date).all()
        
        reminders = []
        
        for gift in upcoming_gifts:
            days_until = (gift.occasion_date - date.today()).days
            
            # Calculate reminder dates based on how far out the occasion is
            reminder_dates = []
            
            if days_until > 14:
                reminder_dates.append({
                    "type": "planning_reminder",
                    "date": date.today() + timedelta(days=days_until - 14),
                    "message": f"Start planning gift for {gift.recipient_name or 'recipient'}"
                })
            
            if days_until > 7:
                reminder_dates.append({
                    "type": "purchase_reminder", 
                    "date": date.today() + timedelta(days=days_until - 7),
                    "message": f"Purchase gift for {gift.recipient_name or 'recipient'} ({gift.occasion})"
                })
            
            if days_until > 2:
                reminder_dates.append({
                    "type": "preparation_reminder",
                    "date": date.today() + timedelta(days=days_until - 2),
                    "message": f"Prepare gift for {gift.recipient_name or 'recipient'} - {gift.occasion} is in 2 days"
                })
            
            reminders.append({
                "gift_id": gift.id,
                "gift_title": gift.title,
                "occasion": gift.occasion,
                "occasion_date": gift.occasion_date,
                "recipient_name": gift.recipient_name,
                "recipient_contact_id": gift.recipient_contact_id,
                "days_until": days_until,
                "status": gift.status,
                "budget_amount": float(gift.budget_amount) if gift.budget_amount else None,
                "reminder_dates": reminder_dates
            })
        
        return reminders
    
    def sync_contact_occasions(self, contact_id: int, occasions: List[Dict[str, Any]]) -> List[Gift]:
        """Sync contact occasions with gift planning (for contact system integration)"""
        
        created_gifts = []
        
        for occasion_data in occasions:
            occasion_name = occasion_data.get('name')
            occasion_date = occasion_data.get('date')
            importance = occasion_data.get('importance', 'medium')
            
            if not occasion_name or not occasion_date:
                continue
            
            # Check if gift already exists for this occasion
            existing_gift = self.db.query(Gift).filter(
                Gift.user_id == self.user_id,
                Gift.tenant_id == self.tenant_id,
                Gift.recipient_contact_id == contact_id,
                Gift.occasion == occasion_name,
                Gift.occasion_date == occasion_date,
                Gift.is_active == True
            ).first()
            
            if existing_gift:
                continue  # Gift already exists
            
            # Determine budget based on importance
            budget_mapping = {
                'high': 100.0,
                'medium': 50.0,
                'low': 25.0
            }
            suggested_budget = budget_mapping.get(importance, 50.0)
            
            # Create new gift
            gift = self.create_gift_from_contact_occasion(
                contact_id=contact_id,
                occasion=occasion_name,
                occasion_date=occasion_date,
                budget_amount=suggested_budget
            )
            
            if gift:
                created_gifts.append(gift)
        
        return created_gifts