from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps import get_tenant_context
from app.core.enhanced_settings import get_settings
from app.models.user import User
from app.schemas.gift_system import (
    GiftSystemConfig,
    GiftIntegrationSettings,
    GiftSystemPermissions,
    GiftSystemStatus,
    GiftCategoryReference,
    GiftOccasionReference,
    GiftBudgetRangeReference
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