from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud
from app.schemas import contact_intelligence
from app.schemas import contact as contact_schema
from app.models.user import User

router = APIRouter()

# Contact Interaction Endpoints

@router.get("/{contact_id}/interactions", response_model=List[contact_intelligence.ContactInteraction])
def get_contact_interactions(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get interaction history for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    interactions = crud.contact_interaction.get_by_contact(
        db, contact_id=contact_id, skip=skip, limit=limit
    )
    return interactions

@router.post("/{contact_id}/interactions", response_model=contact_intelligence.ContactInteraction)
def create_contact_interaction(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    interaction_in: contact_intelligence.ContactInteractionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Log new interaction with a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Ensure contact_id matches the URL parameter
    interaction_in.contact_id = contact_id
    interaction = crud.contact_interaction.create_with_user(
        db=db, obj_in=interaction_in, user_id=current_user.id
    )
    # Update contact interaction counts
    contact.total_interactions += 1
    if interaction_in.interaction_type in ["email", "text", "social_media"]:
        contact.digital_interactions += 1
    elif interaction_in.interaction_type in ["meeting", "call"]:
        contact.in_person_interactions += 1
    # Update last meaningful interaction if quality is good
    if interaction_in.interaction_quality and interaction_in.interaction_quality >= 7:
        contact.last_meaningful_interaction = interaction_in.interaction_date.date()
    db.add(contact)
    db.commit()
    return interaction

@router.put("/{contact_id}/interactions/{interaction_id}", response_model=contact_intelligence.ContactInteraction)
def update_contact_interaction(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    interaction_id: int,
    interaction_in: contact_intelligence.ContactInteractionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update interaction details.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    interaction = crud.contact_interaction.get(db=db, id=interaction_id)
    if not interaction or interaction.contact_id != contact_id:
        raise HTTPException(status_code=404, detail="Interaction not found")
    interaction = crud.contact_interaction.update(db=db, db_obj=interaction, obj_in=interaction_in)
    return interaction

# Contact Relationship Score Endpoints

@router.get("/{contact_id}/relationship-score", response_model=contact_intelligence.ContactRelationshipScore)
def get_current_relationship_score(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current relationship metrics for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    score = crud.contact_relationship_score.get_latest_by_contact(db, contact_id=contact_id)
    if not score:
        raise HTTPException(status_code=404, detail="No relationship scores found")
    return score

@router.put("/{contact_id}/relationship-score", response_model=contact_intelligence.ContactRelationshipScore)
def update_relationship_score(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    score_in: contact_intelligence.ContactRelationshipScoreCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update relationship scoring for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    score_in.contact_id = contact_id
    score = crud.contact_relationship_score.create(db=db, obj_in=score_in)
    return score

@router.get("/{contact_id}/score-history", response_model=List[contact_intelligence.ContactRelationshipScore])
def get_relationship_score_history(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get relationship score history for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    scores = crud.contact_relationship_score.get_by_contact(
        db, contact_id=contact_id, skip=skip, limit=limit
    )
    return scores

# Contact AI Insights Endpoints

@router.get("/{contact_id}/insights", response_model=List[contact_intelligence.ContactAIInsight])
def get_contact_insights(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    status: str = "active",
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get AI insights for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    insights = crud.contact_ai_insight.get_by_contact(
        db, contact_id=contact_id, status=status, skip=skip, limit=limit
    )
    return insights

@router.post("/{contact_id}/insights/dismiss", response_model=contact_intelligence.ContactAIInsight)
def dismiss_contact_insight(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    insight_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Dismiss specific AI insight.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    insight = crud.contact_ai_insight.dismiss_insight(db=db, insight_id=insight_id)
    if not insight or insight.contact_id != contact_id:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight

# Contact Analytics and Patterns

@router.get("/{contact_id}/interaction-patterns")
def get_interaction_patterns(
    *,
    tenant_id: int = Depends(deps.get_tenant_id),
    contact_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get interaction analysis for a contact.
    """
    contact = crud.contact.get(db=db, id=contact_id)
    if not contact or contact.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Get recent interactions for analysis
    interactions = crud.contact_interaction.get_recent_by_contact(db, contact_id=contact_id, days=90)
    # Analyze patterns
    interaction_types = {}
    quality_scores = []
    response_times = []
    for interaction in interactions:
        # Count interaction types
        interaction_types[interaction.interaction_type] = interaction_types.get(interaction.interaction_type, 0) + 1
        
        # Collect quality scores
        if interaction.interaction_quality:
            quality_scores.append(interaction.interaction_quality)
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
    return {
        "contact_id": contact_id,
        "analysis_period_days": 90,
        "total_interactions": len(interactions),
        "interaction_types": interaction_types,
        "average_quality": avg_quality,
        "quality_trend": "stable",  # TODO: Calculate actual trend
        "preferred_methods": sorted(interaction_types.items(), key=lambda x: x[1], reverse=True)[:3],
        "engagement_level": "high" if avg_quality and avg_quality >= 8 else "medium" if avg_quality and avg_quality >= 6 else "low"
    }