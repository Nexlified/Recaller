from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal

from app.api import deps
from app.api.deps import get_tenant_context
from app.core.enhanced_settings import get_settings
from app.models.user import User
from app.crud import gift as gift_crud
from app.services.gift_recommendation import GiftRecommendationService
from app.services.gift_integration import GiftIntegrationService
from app.schemas.gift_system import (
    GiftSystemConfig,
    GiftIntegrationSettings,
    GiftSystemPermissions,
    GiftSystemStatus,
    GiftCategoryReference,
    GiftOccasionReference,
    GiftBudgetRangeReference,
    Gift,
    GiftCreate,
    GiftUpdate,
    GiftIdea,
    GiftIdeaCreate,
    GiftIdeaUpdate
)

router = APIRouter()

@router.get("/gift-system/config", response_model=GiftSystemConfig)
def get_gift_system_config(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current gift system configuration.
    """
    settings = get_settings()
    
    return GiftSystemConfig(
        enabled=settings.GIFT_SYSTEM_ENABLED,
        default_budget_currency=settings.GIFT_DEFAULT_CURRENCY,
        max_budget_amount=settings.GIFT_MAX_BUDGET,
        suggestion_engine=settings.GIFT_SUGGESTION_ENGINE,
        reminder_advance_days=settings.get_gift_reminder_days(),
        auto_create_tasks=settings.GIFT_AUTO_CREATE_TASKS,
        privacy_mode=settings.GIFT_PRIVACY_MODE,
        image_storage_enabled=settings.GIFT_IMAGE_STORAGE,
        external_links_enabled=settings.GIFT_EXTERNAL_LINKS,
        tenant_id=get_tenant_context(request)
    )

@router.get("/gift-system/integration-settings", response_model=GiftIntegrationSettings)
def get_gift_integration_settings(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get gift system integration settings with other modules.
    """
    settings = get_settings()
    
    # Default integration settings based on system configuration
    return GiftIntegrationSettings(
        contact_integration_enabled=settings.GIFT_SYSTEM_ENABLED,
        auto_suggest_from_relationships=settings.GIFT_SYSTEM_ENABLED,
        use_contact_preferences=settings.GIFT_SYSTEM_ENABLED,
        financial_integration_enabled=settings.GIFT_SYSTEM_ENABLED,
        track_gift_expenses=settings.GIFT_SYSTEM_ENABLED,
        budget_alerts_enabled=settings.GIFT_SYSTEM_ENABLED,
        reminder_integration_enabled=settings.GIFT_SYSTEM_ENABLED,
        create_occasion_reminders=settings.GIFT_AUTO_CREATE_TASKS,
        create_shopping_reminders=settings.GIFT_AUTO_CREATE_TASKS,
        task_integration_enabled=settings.GIFT_SYSTEM_ENABLED,
        create_shopping_tasks=settings.GIFT_AUTO_CREATE_TASKS,
        create_wrapping_tasks=False  # Optional feature
    )

@router.get("/gift-system/permissions", response_model=GiftSystemPermissions)
def get_gift_system_permissions(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get gift system permissions for current user.
    Based on tenant context and user role.
    """
    settings = get_settings()
    
    # For now, basic permissions based on system being enabled
    # In future, this would check user roles and tenant settings
    if not settings.GIFT_SYSTEM_ENABLED:
        return GiftSystemPermissions(
            can_view_gifts=False,
            can_create_gifts=False,
            can_edit_gifts=False,
            can_delete_gifts=False,
            can_manage_budgets=False,
            can_view_others_gifts=False,
            can_export_gift_data=False,
            can_configure_system=False
        )
    
    # Default permissions for enabled system
    # Users have full access to their own gift data within their tenant
    return GiftSystemPermissions(
        can_view_gifts=True,
        can_create_gifts=True,
        can_edit_gifts=True,
        can_delete_gifts=True,  # Users can delete their own gifts
        can_manage_budgets=True,
        can_view_others_gifts=False,  # Privacy-first approach
        can_export_gift_data=True,
        can_configure_system=False  # Only admins should configure system
    )

@router.get("/gift-system/status", response_model=GiftSystemStatus)
def get_gift_system_status(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get gift system status and health information.
    """
    settings = get_settings()
    
    # Check integration status
    integration_status = {
        "contacts": settings.GIFT_SYSTEM_ENABLED,
        "financial": settings.GIFT_SYSTEM_ENABLED,
        "reminders": settings.GIFT_SYSTEM_ENABLED,
        "tasks": settings.GIFT_SYSTEM_ENABLED and settings.GIFT_AUTO_CREATE_TASKS,
        "storage": settings.GIFT_IMAGE_STORAGE,
        "external_links": settings.GIFT_EXTERNAL_LINKS
    }
    
    # Basic configuration validation
    configuration_valid = (
        settings.GIFT_DEFAULT_CURRENCY is not None and
        settings.GIFT_MAX_BUDGET > 0 and
        len(settings.get_gift_reminder_days()) > 0
    )
    
    return GiftSystemStatus(
        is_enabled=settings.GIFT_SYSTEM_ENABLED,
        configuration_valid=configuration_valid,
        integration_status=integration_status,
        version="1.0.0",
        # Reference data counts would be populated from database in real implementation
        total_gift_categories=8,  # Based on our reference data
        total_gift_occasions=12,
        total_budget_ranges=6
    )

@router.get("/gift-system/reference-data/categories", response_model=List[GiftCategoryReference])
def get_gift_categories(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get gift category reference data.
    This would typically load from the configuration system or database.
    """
    settings = get_settings()
    
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    # Mock data - in real implementation, this would load from configuration system
    categories = [
        GiftCategoryReference(
            key="electronics",
            display_name="Electronics",
            description="Electronic devices and gadgets",
            icon="device",
            color="#2196F3",
            price_range="medium_to_high",
            tags=["electronics", "gadgets", "technology"]
        ),
        GiftCategoryReference(
            key="clothing",
            display_name="Clothing & Accessories",
            description="Fashion items and accessories",
            icon="shirt",
            color="#E91E63",
            price_range="low_to_high",
            tags=["fashion", "clothing", "style"]
        ),
        GiftCategoryReference(
            key="books",
            display_name="Books & Media",
            description="Books, magazines, and educational materials",
            icon="book",
            color="#795548",
            price_range="low_to_medium",
            tags=["books", "education", "entertainment"]
        )
        # More categories would be loaded from reference data
    ]
    
    return categories

@router.get("/gift-system/reference-data/occasions", response_model=List[GiftOccasionReference])
def get_gift_occasions(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get gift occasion reference data.
    """
    settings = get_settings()
    
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    # Mock data - in real implementation, this would load from configuration system
    occasions = [
        GiftOccasionReference(
            key="birthday",
            display_name="Birthday",
            description="Annual birthday celebrations",
            icon="cake",
            color="#FF5722",
            frequency="annual",
            advance_reminder_days=settings.get_gift_reminder_days(),
            budget_importance="high",
            tags=["birthday", "celebration", "annual"]
        ),
        GiftOccasionReference(
            key="christmas",
            display_name="Christmas",
            description="Christmas holiday gifts",
            icon="tree",
            color="#4CAF50",
            frequency="annual",
            date="12-25",
            advance_reminder_days=[60, 30, 14, 7],
            budget_importance="high",
            tags=["christmas", "holiday", "winter"]
        )
        # More occasions would be loaded from reference data
    ]
    
    return occasions

@router.get("/gift-system/reference-data/budget-ranges", response_model=List[GiftBudgetRangeReference])
def get_gift_budget_ranges(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get gift budget range reference data.
    """
    settings = get_settings()
    
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    # Mock data - in real implementation, this would load from configuration system
    budget_ranges = [
        GiftBudgetRangeReference(
            key="under_25",
            display_name="Under $25",
            description="Small thoughtful gifts and tokens",
            min_amount=0,
            max_amount=25,
            currency=settings.GIFT_DEFAULT_CURRENCY,
            color="#4CAF50",
            suggested_categories=["books", "food", "small_accessories"],
            tags=["budget", "small", "thoughtful"]
        ),
        GiftBudgetRangeReference(
            key="50_to_100",
            display_name="$50 - $100",
            description="Nice gifts for friends and family",
            min_amount=50,
            max_amount=100,
            currency=settings.GIFT_DEFAULT_CURRENCY,
            color="#2196F3",
            suggested_categories=["electronics", "clothing", "hobbies"],
            tags=["budget", "friends", "family"]
        )
        # More budget ranges would be loaded from reference data
    ]
    
    return budget_ranges


# Gift CRUD Endpoints

@router.get("/gifts/", response_model=List[Gift])
def list_gifts(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    status: Optional[str] = Query(None, description="Filter by gift status"),
    category: Optional[str] = Query(None, description="Filter by gift category"),
    occasion: Optional[str] = Query(None, description="Filter by occasion"),
    recipient_contact_id: Optional[int] = Query(None, description="Filter by recipient contact ID")
) -> Any:
    """
    Retrieve gifts for the current user.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gifts = gift_crud.get_gifts(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        occasion=occasion,
        recipient_contact_id=recipient_contact_id
    )
    return gifts


@router.get("/gifts/{gift_id}", response_model=Gift)
def get_gift(
    request: Request,
    gift_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get gift by ID.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gift = gift_crud.get_gift_with_user_access(
        db, 
        gift_id=gift_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    return gift


@router.post("/gifts/", response_model=Gift)
def create_gift(
    request: Request,
    gift_in: GiftCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new gift.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gift = gift_crud.create_gift(
        db, 
        obj_in=gift_in, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    return gift


@router.put("/gifts/{gift_id}", response_model=Gift)
def update_gift(
    request: Request,
    gift_id: int,
    gift_in: GiftUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update gift. Only the gift owner can update it.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gift = gift_crud.get_gift_with_user_access(
        db, 
        gift_id=gift_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    
    gift = gift_crud.update_gift(db, db_obj=gift, obj_in=gift_in)
    return gift


@router.delete("/gifts/{gift_id}", response_model=Gift)
def delete_gift(
    request: Request,
    gift_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete gift (soft delete).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gift = gift_crud.get_gift_with_user_access(
        db, 
        gift_id=gift_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    
    gift = gift_crud.delete_gift(db, db_obj=gift)
    return gift


# Gift Ideas CRUD Endpoints

@router.get("/gift-ideas/", response_model=List[GiftIdea])
def list_gift_ideas(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    target_contact_id: Optional[int] = Query(None, description="Filter by target contact ID"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating filter")
) -> Any:
    """
    Retrieve gift ideas for the current user.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    ideas = gift_crud.get_gift_ideas(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        category=category,
        target_contact_id=target_contact_id,
        is_favorite=is_favorite,
        min_rating=min_rating
    )
    return ideas


@router.get("/gift-ideas/search/", response_model=List[GiftIdea])
def search_gift_ideas(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return")
) -> Any:
    """
    Search gift ideas by title, description, tags, or category.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    # Sanitize search query
    from app.core.validation import InputSanitizer
    try:
        sanitized_query = InputSanitizer.sanitize_search_query(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    ideas = gift_crud.search_gift_ideas(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        query=sanitized_query,
        skip=skip,
        limit=limit
    )
    return ideas


@router.get("/gift-ideas/popular/", response_model=List[GiftIdea])
def get_popular_gift_ideas(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    limit: int = Query(10, ge=1, le=50, description="Maximum records to return")
) -> Any:
    """
    Get most popular gift ideas (by times gifted).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    ideas = gift_crud.get_popular_gift_ideas(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        limit=limit
    )
    return ideas


@router.get("/gift-ideas/{idea_id}", response_model=GiftIdea)
def get_gift_idea(
    request: Request,
    idea_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get gift idea by ID.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    idea = gift_crud.get_gift_idea_with_user_access(
        db, 
        idea_id=idea_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not idea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    return idea


@router.post("/gift-ideas/", response_model=GiftIdea)
def create_gift_idea(
    request: Request,
    idea_in: GiftIdeaCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new gift idea.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    idea = gift_crud.create_gift_idea(
        db, 
        obj_in=idea_in, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    return idea


@router.put("/gift-ideas/{idea_id}", response_model=GiftIdea)
def update_gift_idea(
    request: Request,
    idea_id: int,
    idea_in: GiftIdeaUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update gift idea. Only the idea owner can update it.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    idea = gift_crud.get_gift_idea_with_user_access(
        db, 
        idea_id=idea_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not idea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    
    idea = gift_crud.update_gift_idea(db, db_obj=idea, obj_in=idea_in)
    return idea


@router.delete("/gift-ideas/{idea_id}", response_model=GiftIdea)
def delete_gift_idea(
    request: Request,
    idea_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete gift idea (soft delete).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    idea = gift_crud.get_gift_idea_with_user_access(
        db, 
        idea_id=idea_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not idea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    
    idea = gift_crud.delete_gift_idea(db, db_obj=idea)
    return idea


@router.post("/gift-ideas/{idea_id}/mark-as-gifted", response_model=GiftIdea)
def mark_gift_idea_as_gifted(
    request: Request,
    idea_id: int,
    gifted_date: Optional[date] = Query(None, description="Date when gift was given"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Mark gift idea as gifted (increment usage counter).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    idea = gift_crud.get_gift_idea_with_user_access(
        db, 
        idea_id=idea_id, 
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    if not idea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    
    idea = gift_crud.mark_gift_idea_as_gifted(db, db_obj=idea, gifted_date=gifted_date)
    return idea


# Analytics and Recommendations

@router.get("/analytics/", response_model=Dict[str, Any])
def get_gift_analytics(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get gift analytics for the current user.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    analytics = gift_crud.get_gift_analytics(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    return analytics


@router.get("/analytics/budget-insights/", response_model=Dict[str, Any])
def get_budget_insights(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get budget insights and spending patterns.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    recommendation_service = GiftRecommendationService(
        db, current_user.id, current_user.tenant_id
    )
    insights = recommendation_service.get_budget_insights()
    return insights


@router.get("/analytics/gift-patterns/", response_model=Dict[str, Any])
def get_gift_giving_patterns(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get gift-giving patterns and preferences analysis.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    recommendation_service = GiftRecommendationService(
        db, current_user.id, current_user.tenant_id
    )
    patterns = recommendation_service.get_gift_giving_patterns()
    return patterns


@router.get("/recommendations/upcoming-occasions/", response_model=List[Dict[str, Any]])
def get_upcoming_occasions(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to look ahead")
) -> Any:
    """
    Get upcoming gift occasions and reminders.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    recommendation_service = GiftRecommendationService(
        db, current_user.id, current_user.tenant_id
    )
    occasions = recommendation_service.get_upcoming_occasions(days_ahead)
    return occasions


@router.get("/recommendations/for-contact/{contact_id}", response_model=List[Dict[str, Any]])
def get_gift_recommendations_for_contact(
    request: Request,
    contact_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    occasion: Optional[str] = Query(None, description="Filter by occasion"),
    budget_max: Optional[Decimal] = Query(None, description="Maximum budget filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendations to return")
) -> Any:
    """
    Get gift recommendations for a specific contact.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    recommendation_service = GiftRecommendationService(
        db, current_user.id, current_user.tenant_id
    )
    recommendations = recommendation_service.get_gift_suggestions_for_contact(
        contact_id=contact_id,
        occasion=occasion,
        budget_max=budget_max,
        limit=limit
    )
    return recommendations


@router.get("/recommendations/reminders/", response_model=List[Dict[str, Any]])
def get_reminder_suggestions(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    days_ahead: int = Query(60, ge=1, le=365, description="Number of days to look ahead for reminders")
) -> Any:
    """
    Get suggestions for setting up gift reminders.
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    recommendation_service = GiftRecommendationService(
        db, current_user.id, current_user.tenant_id
    )
    suggestions = recommendation_service.get_reminder_suggestions(days_ahead)
    return suggestions


# Integration Endpoints

@router.get("/gifts/by-recipient/{contact_id}", response_model=List[Gift])
def get_gifts_by_recipient(
    request: Request,
    contact_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return")
) -> Any:
    """
    Get gifts for a specific recipient (contact integration).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gifts = gift_crud.get_gifts_by_recipient(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        recipient_contact_id=contact_id,
        skip=skip,
        limit=limit
    )
    return gifts


@router.get("/gifts/by-date-range/", response_model=List[Gift])
def get_gifts_by_date_range(
    request: Request,
    start_date: date = Query(..., description="Start date for occasion filter"),
    end_date: date = Query(..., description="End date for occasion filter"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get gifts within a date range (reminder integration).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    gifts = gift_crud.get_gifts_by_occasion_date_range(
        db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    return gifts


# Advanced Integration Endpoints

@router.get("/integration/contacts-with-gifts/", response_model=List[Dict[str, Any]])
def get_contacts_with_gifts(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get contacts and their associated gifts (contact system integration).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    integration_service = GiftIntegrationService(
        db, current_user.id, current_user.tenant_id
    )
    contacts_data = integration_service.get_contacts_with_gifts()
    return contacts_data


@router.get("/integration/financial-summary/", response_model=Dict[str, Any])
def get_gift_financial_summary(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    year: Optional[int] = Query(None, description="Year for financial summary")
) -> Any:
    """
    Get financial summary of gift spending (financial system integration).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    integration_service = GiftIntegrationService(
        db, current_user.id, current_user.tenant_id
    )
    summary = integration_service.get_financial_summary(year)
    return summary


@router.get("/integration/reminder-data/", response_model=List[Dict[str, Any]])
def get_gift_reminder_data(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead for reminders")
) -> Any:
    """
    Get gift reminder data (reminder system integration).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    integration_service = GiftIntegrationService(
        db, current_user.id, current_user.tenant_id
    )
    reminder_data = integration_service.get_reminder_data(days_ahead)
    return reminder_data


@router.post("/integration/create-from-contact-occasion/", response_model=Gift)
def create_gift_from_contact_occasion(
    request: Request,
    contact_id: int = Query(..., description="Contact ID"),
    occasion: str = Query(..., description="Occasion name"),
    occasion_date: date = Query(..., description="Occasion date"),
    budget_amount: Optional[float] = Query(None, description="Budget amount"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a gift from contact occasion data (contact system integration).
    """
    settings = get_settings()
    if not settings.GIFT_SYSTEM_ENABLED:
        raise HTTPException(status_code=404, detail="Gift system is not enabled")
    
    integration_service = GiftIntegrationService(
        db, current_user.id, current_user.tenant_id
    )
    
    gift = integration_service.create_gift_from_contact_occasion(
        contact_id=contact_id,
        occasion=occasion,
        occasion_date=occasion_date,
        budget_amount=budget_amount
    )
    
    if not gift:
        raise HTTPException(status_code=404, detail="Contact not found or gift creation failed")
    
    return gift