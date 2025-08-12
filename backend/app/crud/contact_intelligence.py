from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, datetime
from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.models.contact_interaction import ContactInteraction
from app.models.contact_relationship_score import ContactRelationshipScore
from app.models.contact_ai_insight import ContactAIInsight
from app.schemas.contact_intelligence import (
    ContactInteractionCreate, ContactInteractionUpdate,
    ContactRelationshipScoreCreate, ContactRelationshipScoreUpdate,
    ContactAIInsightCreate, ContactAIInsightUpdate
)

class CRUDContactInteraction(CRUDBase[ContactInteraction, ContactInteractionCreate, ContactInteractionUpdate]):
    def get_by_contact(
        self, db: Session, *, contact_id: int, skip: int = 0, limit: int = 100
    ) -> List[ContactInteraction]:
        return db.query(ContactInteraction).filter(
            ContactInteraction.contact_id == contact_id
        ).order_by(desc(ContactInteraction.interaction_date)).offset(skip).limit(limit).all()

    def create_with_user(
        self, db: Session, *, obj_in: ContactInteractionCreate, user_id: int
    ) -> ContactInteraction:
        obj_in_data = obj_in.dict()
        db_obj = ContactInteraction(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_recent_by_contact(
        self, db: Session, *, contact_id: int, days: int = 30
    ) -> List[ContactInteraction]:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return db.query(ContactInteraction).filter(
            ContactInteraction.contact_id == contact_id,
            ContactInteraction.interaction_date >= cutoff_date
        ).order_by(desc(ContactInteraction.interaction_date)).all()

class CRUDContactRelationshipScore(CRUDBase[ContactRelationshipScore, ContactRelationshipScoreCreate, ContactRelationshipScoreUpdate]):
    def get_by_contact(
        self, db: Session, *, contact_id: int, skip: int = 0, limit: int = 100
    ) -> List[ContactRelationshipScore]:
        return db.query(ContactRelationshipScore).filter(
            ContactRelationshipScore.contact_id == contact_id
        ).order_by(desc(ContactRelationshipScore.score_date)).offset(skip).limit(limit).all()

    def get_latest_by_contact(
        self, db: Session, *, contact_id: int
    ) -> Optional[ContactRelationshipScore]:
        return db.query(ContactRelationshipScore).filter(
            ContactRelationshipScore.contact_id == contact_id
        ).order_by(desc(ContactRelationshipScore.score_date)).first()

class CRUDContactAIInsight(CRUDBase[ContactAIInsight, ContactAIInsightCreate, ContactAIInsightUpdate]):
    def get_by_contact(
        self, db: Session, *, contact_id: int, status: str = "active", skip: int = 0, limit: int = 100
    ) -> List[ContactAIInsight]:
        query = db.query(ContactAIInsight).filter(
            ContactAIInsight.contact_id == contact_id
        )
        if status:
            query = query.filter(ContactAIInsight.status == status)
        return query.order_by(desc(ContactAIInsight.created_at)).offset(skip).limit(limit).all()

    def dismiss_insight(
        self, db: Session, *, insight_id: int
    ) -> Optional[ContactAIInsight]:
        db_obj = db.query(ContactAIInsight).filter(ContactAIInsight.id == insight_id).first()
        if db_obj:
            db_obj.status = "dismissed"
            db_obj.dismissed_at = datetime.now()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_by_priority(
        self, db: Session, *, priority: str, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[ContactAIInsight]:
        return db.query(ContactAIInsight).join(ContactAIInsight.contact).filter(
            ContactAIInsight.priority == priority,
            ContactAIInsight.status == "active",
            Contact.tenant_id == tenant_id
        ).order_by(desc(ContactAIInsight.created_at)).offset(skip).limit(limit).all()

contact_interaction = CRUDContactInteraction(ContactInteraction)
contact_relationship_score = CRUDContactRelationshipScore(ContactRelationshipScore)
contact_ai_insight = CRUDContactAIInsight(ContactAIInsight)