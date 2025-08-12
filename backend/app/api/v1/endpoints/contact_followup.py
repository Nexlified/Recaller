from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.api import deps
from app import crud
from app.schemas import contact as contact_schema
from app.models.user import User

router = APIRouter()

# Follow-up Management Endpoints

@router.get("/follow-up-needed", response_model=List[contact_schema.Contact])
def get_contacts_needing_followup(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get contacts that need follow-up.
    """
    contacts = crud.contact.get_follow_up_needed(
        db, tenant_id=tenant_id, skip=skip, limit=limit
    )
    return contacts

@router.get("/overdue-contacts", response_model=List[contact_schema.Contact])
def get_overdue_contacts(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get overdue contact list.
    """
    # Get contacts where next suggested contact date is in the past
    today = date.today()
    contacts = crud.contact.get_multi_by_tenant(db, tenant_id=tenant_id, skip=0, limit=1000)
    overdue_contacts = [
        contact for contact in contacts
        if contact.next_suggested_contact_date and contact.next_suggested_contact_date < today
    ]
    # Sort by how overdue they are
    overdue_contacts.sort(key=lambda x: x.next_suggested_contact_date or date.min)
    return overdue_contacts[skip:skip+limit]

@router.get("/{contact_id}/follow-up-suggestions")
def get_followup_suggestions(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get AI follow-up suggestions for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Get recent interactions to inform suggestions
    recent_interactions = crud.contact_interaction.get_recent_by_contact(db, contact_id=contact_id, days=60)
    suggestions = []
    # Generate suggestions based on contact data and interaction history
    if contact.communication_preference == "email":
        suggestions.append({
            "type": "email_check_in",
            "title": "Send a friendly email check-in",
            "description": f"Send a casual email to {contact.first_name} to see how they're doing.",
            "urgency": "medium",
            "suggested_content": f"Hi {contact.first_name}, hope you're doing well! Wanted to check in and see how things are going.",
            "estimated_time": "5 minutes"
        })
    if contact.preferred_meeting_type == "coffee":
        suggestions.append({
            "type": "coffee_meeting",
            "title": "Suggest a coffee meetup",
            "description": f"Invite {contact.first_name} for a coffee since they prefer casual meetings.",
            "urgency": "low",
            "suggested_content": f"Hey {contact.first_name}, would love to catch up over coffee sometime soon. Are you free this week?",
            "estimated_time": "1 hour"
        })
    # Add suggestions based on conversation topics
    if contact.conversation_topics:
        topic = contact.conversation_topics[0] if contact.conversation_topics else "recent updates"
        suggestions.append({
            "type": "topic_based",
            "title": f"Share something about {topic}",
            "description": f"Send them something interesting related to {topic} since they enjoy discussing it.",
            "urgency": "low",
            "suggested_content": f"Saw this article about {topic} and thought you might find it interesting!",
            "estimated_time": "3 minutes"
        })
    return {
        "contact_id": contact_id,
        "contact_name": f"{contact.first_name} {contact.last_name}",
        "last_interaction": recent_interactions[0].interaction_date if recent_interactions else None,
        "follow_up_urgency": contact.follow_up_urgency,
        "suggestions": suggestions
    }

@router.post("/{contact_id}/follow-up-complete")
def mark_followup_complete(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mark follow-up as completed for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Update follow-up dates
    today = date.today()
    contact.last_follow_up_date = today
    # Calculate next suggested contact date based on frequency goal
    if contact.follow_up_frequency:
        contact.next_suggested_contact_date = today + timedelta(days=contact.follow_up_frequency)
    else:
        contact.next_suggested_contact_date = today + timedelta(days=30)  # Default 30 days
    # Reset urgency
    contact.follow_up_urgency = "normal"
    db.add(contact)
    db.commit()
    return {"message": "Follow-up marked as complete", "next_contact_date": contact.next_suggested_contact_date}

# Smart Recommendation Endpoints

@router.get("/recommendations/reconnect", response_model=List[contact_schema.Contact])
def get_reconnection_recommendations(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get contacts to reconnect with.
    """
    # Get contacts with good relationship strength but haven't interacted recently
    contacts = crud.contact.get_by_relationship_strength(
        db, tenant_id=tenant_id, min_strength=6, skip=0, limit=500
    )
    cutoff_date = date.today() - timedelta(days=90)
    reconnect_candidates = [
        contact for contact in contacts
        if not contact.last_meaningful_interaction or contact.last_meaningful_interaction < cutoff_date
    ]
    # Sort by connection strength and networking value
    reconnect_candidates.sort(key=lambda x: (x.connection_strength, x.networking_value == "high"), reverse=True)
    return reconnect_candidates[skip:skip+limit]

@router.get("/recommendations/strengthen", response_model=List[contact_schema.Contact])
def get_relationship_strengthening_recommendations(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get relationships to strengthen.
    """
    # Get contacts with medium connection strength and high collaboration potential
    all_contacts = crud.contact.get_multi_by_tenant(db, tenant_id=tenant_id, skip=0, limit=1000)
    strengthen_candidates = [
        contact for contact in all_contacts
        if (contact.connection_strength >= 4 and contact.connection_strength <= 7) and
           contact.collaboration_potential == "high"
    ]
    # Sort by priority score and collaboration potential
    strengthen_candidates.sort(key=lambda x: float(x.priority_score), reverse=True)
    return strengthen_candidates[skip:skip+limit]

@router.get("/recommendations/introductions")
def get_introduction_opportunities(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get introduction opportunities.
    """
    # Get high-value contacts for potential introductions
    high_value_contacts = crud.contact.get_by_networking_value(
        db, tenant_id=tenant_id, networking_value="high", skip=0, limit=200
    )
    opportunities = []
    # Simple algorithm to find potential introduction opportunities
    for contact in high_value_contacts:
        if contact.referral_potential == "high" and contact.connection_strength >= 7:
            # Look for other contacts who might benefit from introduction
            other_contacts = [c for c in high_value_contacts if c.id != contact.id and c.career_stage == contact.career_stage][:3]
            
            if other_contacts:
                opportunities.append({
                    "connector": {
                        "id": contact.id,
                        "name": f"{contact.first_name} {contact.last_name}",
                        "organization": contact.current_organization.name if contact.current_organization else None,
                        "networking_value": contact.networking_value,
                        "referral_potential": contact.referral_potential
                    },
                    "potential_connections": [
                        {
                            "id": c.id,
                            "name": f"{c.first_name} {c.last_name}",
                            "organization": c.current_organization.name if c.current_organization else None,
                            "reason": f"Both in {c.career_stage} career stage"
                        }
                        for c in other_contacts
                    ],
                    "introduction_reason": f"{contact.first_name} has high referral potential and strong network",
                    "confidence": 0.7
                })
    return {
        "total_opportunities": len(opportunities),
        "opportunities": opportunities[skip:skip+limit]
    }

# Contact Lifecycle Management

@router.get("/lifecycle/new", response_model=List[contact_schema.Contact])
def get_new_contacts_needing_attention(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    days: int = 14,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get recently added contacts needing attention.
    """
    cutoff_date = date.today() - timedelta(days=days)
    contacts = crud.contact.get_multi_by_tenant(db, tenant_id=tenant_id, skip=0, limit=1000)
    new_contacts = [
        contact for contact in contacts
        if contact.created_at.date() >= cutoff_date and contact.total_interactions < 3
    ]
    new_contacts.sort(key=lambda x: x.created_at, reverse=True)
    return new_contacts[skip:skip+limit]

@router.get("/lifecycle/declining", response_model=List[contact_schema.Contact])
def get_declining_relationships(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get relationships that need attention.
    """
    contacts = crud.contact.get_multi_by_tenant(db, tenant_id=tenant_id, skip=0, limit=1000)
    declining_contacts = [
        contact for contact in contacts
        if contact.relationship_trend == "declining" or contact.interaction_quality_trend == "declining"
    ]
    # Sort by priority score (highest priority first)
    declining_contacts.sort(key=lambda x: float(x.priority_score), reverse=True)
    return declining_contacts[skip:skip+limit]