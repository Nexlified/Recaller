from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud
from app.schemas import contact as contact_schema
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=contact_schema.Contact)
def create_contact(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_in: contact_schema.ContactCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new contact.
    """
    # Check if contact with email already exists
    if contact_in.email:
        contact = crud.contact.get_by_email(db, email=contact_in.email, tenant_id=tenant_id)
        if contact:
            raise HTTPException(
                status_code=400,
                detail="Contact with this email already exists.",
            )
    contact = crud.contact.create_with_tenant(db=db, obj_in=contact_in, tenant_id=tenant_id)
    return contact

@router.get("/", response_model=List[contact_schema.Contact])
def read_contacts(
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve contacts.
    """
    contacts = crud.contact.get_multi_by_tenant(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return contacts

@router.get("/{contact_id}", response_model=contact_schema.Contact)
def read_contact(
    *,
    contact_id: int,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get contact by ID.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=contact_schema.Contact)
def update_contact(
    *,
    contact_id: int,
    contact_in: contact_schema.ContactUpdate,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact = crud.contact.update(db=db, db_obj=contact, obj_in=contact_in)
    return contact

@router.delete("/{contact_id}", response_model=contact_schema.Contact)
def delete_contact(
    *,
    contact_id: int,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact = crud.contact.remove(db=db, id=contact_id)
    return contact

# Enhanced Contact Intelligence Endpoints

@router.get("/{contact_id}/full-profile", response_model=contact_schema.ContactFullProfile)
def get_contact_full_profile(
    *,
    contact_id: int,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get complete contact profile with intelligence.
    """
    contact = crud.contact.get_full_profile(db=db, contact_id=contact_id, tenant_id=tenant_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Build the full profile response
    intelligence_metrics = contact_schema.ContactIntelligenceMetrics(
        connection_strength=contact.connection_strength,
        engagement_score=contact.engagement_score,
        priority_score=contact.priority_score,
        relationship_trend=contact.relationship_trend,
        total_interactions=contact.total_interactions,
        last_meaningful_interaction=contact.last_meaningful_interaction,
        next_suggested_contact_date=contact.next_suggested_contact_date,
        follow_up_urgency=contact.follow_up_urgency
    )
    relationship_context = contact_schema.ContactRelationshipContext(
        personality_type=contact.personality_type,
        communication_preference=contact.communication_preference,
        life_stage=contact.life_stage,
        networking_value=contact.networking_value,
        collaboration_potential=contact.collaboration_potential
    )
    # Get recent interactions for summary
    recent_interactions = crud.contact_interaction.get_recent_by_contact(db, contact_id=contact_id)
    avg_quality = sum(i.interaction_quality for i in recent_interactions if i.interaction_quality) / len(recent_interactions) if recent_interactions else None
    interaction_summary = contact_schema.ContactInteractionSummary(
        total_interactions=contact.total_interactions,
        avg_interaction_quality=avg_quality,
        preferred_interaction_times=[contact.preferred_communication_time] if contact.preferred_communication_time else [],
        response_rate=None  # TODO: Calculate based on response patterns
    )
    # Get recent AI insights
    recent_insights = crud.contact_ai_insight.get_by_contact(db, contact_id=contact_id, limit=5)
    insights_data = [
        {
            "type": insight.insight_type,
            "title": insight.title,
            "description": insight.description,
            "priority": insight.priority,
            "confidence_score": float(insight.confidence_score) if insight.confidence_score else None
        }
        for insight in recent_insights
    ]
    # Build organization data if exists
    org_data = None
    if contact.current_organization:
        org_data = {
            "id": contact.current_organization.id,
            "name": contact.current_organization.name,
            "organization_type": contact.current_organization.organization_type
        }
    return contact_schema.ContactFullProfile(
        **contact.__dict__,
        intelligence=intelligence_metrics,
        context=relationship_context,
        interaction_summary=interaction_summary,
        current_organization=org_data,
        recent_insights=insights_data
    )

@router.put("/{contact_id}/intelligence", response_model=contact_schema.Contact)
def update_contact_intelligence(
    *,
    contact_id: int,
    intelligence_in: contact_schema.ContactIntelligenceUpdate,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update intelligence fields for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact = crud.contact.update_intelligence(db=db, db_obj=contact, obj_in=intelligence_in)
    return contact

@router.put("/{contact_id}/interaction-prefs", response_model=contact_schema.Contact)
def update_interaction_preferences(
    *,
    contact_id: int,
    prefs_in: contact_schema.ContactInteractionPreferences,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update interaction preferences for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Convert to intelligence update format
    intelligence_update = contact_schema.ContactIntelligenceUpdate(**prefs_in.dict(exclude_unset=True))
    contact = crud.contact.update_intelligence(db=db, db_obj=contact, obj_in=intelligence_update)
    return contact

@router.put("/{contact_id}/relationship-context", response_model=contact_schema.Contact)
def update_relationship_context(
    *,
    contact_id: int,
    context_in: contact_schema.ContactRelationshipContext,
    tenant_id: int = Depends(deps.get_tenant_id),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update relationship context for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Convert to intelligence update format
    intelligence_update = contact_schema.ContactIntelligenceUpdate(**context_in.dict(exclude_unset=True))
    contact = crud.contact.update_intelligence(db=db, db_obj=contact, obj_in=intelligence_update)
    return contact