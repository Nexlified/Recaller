from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, date
from decimal import Decimal

class GiftPrivacyMode(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    STRICT = "strict"

class GiftSuggestionEngine(str, Enum):
    BASIC = "basic"
    ENHANCED = "enhanced"
    AI_POWERED = "ai_powered"


class GiftStatus(str, Enum):
    IDEA = "idea"
    PLANNED = "planned"
    PURCHASED = "purchased"
    WRAPPED = "wrapped"
    GIVEN = "given"
    RETURNED = "returned"


class GiftPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class GiftSystemConfigBase(BaseModel):
    """Base schema for gift system configuration"""
    enabled: bool = Field(default=True, description="Whether gift system is enabled")
    default_budget_currency: str = Field(default="USD", description="Default currency for gift budgets")
    max_budget_amount: int = Field(default=10000, description="Maximum budget amount allowed")
    suggestion_engine: GiftSuggestionEngine = Field(default=GiftSuggestionEngine.BASIC, description="Gift suggestion engine type")
    reminder_advance_days: List[int] = Field(default=[7, 3, 1], description="Days in advance to send reminders")
    auto_create_tasks: bool = Field(default=True, description="Automatically create tasks for gift shopping")
    privacy_mode: GiftPrivacyMode = Field(default=GiftPrivacyMode.PERSONAL, description="Privacy mode for gift data")
    image_storage_enabled: bool = Field(default=True, description="Whether to allow image storage for gifts")
    external_links_enabled: bool = Field(default=True, description="Whether to allow external links for gifts")

    @validator('max_budget_amount')
    def validate_max_budget(cls, v):
        if v <= 0:
            raise ValueError('Maximum budget must be greater than 0')
        if v > 100000:  # $100k sanity check
            raise ValueError('Maximum budget cannot exceed $100,000')
        return v

    @validator('reminder_advance_days')
    def validate_reminder_days(cls, v):
        if not v:
            return [7, 3, 1]  # Default fallback
        # Ensure all values are positive and unique
        days = sorted(set([day for day in v if day > 0]), reverse=True)
        if not days:
            return [7, 3, 1]  # Default fallback
        return days

class GiftSystemConfig(GiftSystemConfigBase):
    """Gift system configuration with additional computed fields"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tenant_id: Optional[int] = None

    class Config:
        from_attributes = True

class GiftIntegrationSettings(BaseModel):
    """Integration settings for gift system with other modules"""
    
    # Contact integration
    contact_integration_enabled: bool = Field(default=True, description="Enable contact system integration")
    auto_suggest_from_relationships: bool = Field(default=True, description="Auto-suggest gifts based on relationships")
    use_contact_preferences: bool = Field(default=True, description="Use contact preferences for gift suggestions")
    
    # Financial integration
    financial_integration_enabled: bool = Field(default=True, description="Enable financial system integration")
    track_gift_expenses: bool = Field(default=True, description="Track gift purchases as expenses")
    budget_alerts_enabled: bool = Field(default=True, description="Enable budget alerts for gift spending")
    
    # Reminder integration
    reminder_integration_enabled: bool = Field(default=True, description="Enable reminder system integration")
    create_occasion_reminders: bool = Field(default=True, description="Create reminders for gift occasions")
    create_shopping_reminders: bool = Field(default=True, description="Create reminders for gift shopping")
    
    # Task integration
    task_integration_enabled: bool = Field(default=True, description="Enable task system integration")
    create_shopping_tasks: bool = Field(default=True, description="Create tasks for gift shopping")
    create_wrapping_tasks: bool = Field(default=False, description="Create tasks for gift wrapping")

class GiftCategoryReference(BaseModel):
    """Reference data for gift categories"""
    key: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    price_range: Optional[str] = None
    suggested_budget_min: Optional[int] = None
    suggested_budget_max: Optional[int] = None
    tags: List[str] = Field(default_factory=list)

class GiftOccasionReference(BaseModel):
    """Reference data for gift occasions"""
    key: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    frequency: Optional[str] = None  # annual, milestone, spontaneous
    advance_reminder_days: List[int] = Field(default_factory=list)
    budget_importance: Optional[str] = None  # low, medium, high
    date: Optional[str] = None  # For fixed date occasions like Christmas
    tags: List[str] = Field(default_factory=list)

class GiftBudgetRangeReference(BaseModel):
    """Reference data for gift budget ranges"""
    key: str
    display_name: str
    description: Optional[str] = None
    min_amount: int
    max_amount: Optional[int] = None
    currency: str = "USD"
    color: Optional[str] = None
    suggested_categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class GiftSystemPermissions(BaseModel):
    """Permissions for gift system features"""
    can_view_gifts: bool = Field(default=True, description="Can view gift information")
    can_create_gifts: bool = Field(default=True, description="Can create new gifts")
    can_edit_gifts: bool = Field(default=True, description="Can edit existing gifts")
    can_delete_gifts: bool = Field(default=False, description="Can delete gifts")
    can_manage_budgets: bool = Field(default=True, description="Can manage gift budgets")
    can_view_others_gifts: bool = Field(default=False, description="Can view other users' gifts in same tenant")
    can_export_gift_data: bool = Field(default=False, description="Can export gift data")
    can_configure_system: bool = Field(default=False, description="Can configure gift system settings")

class GiftSystemStatus(BaseModel):
    """Status information for gift system"""
    is_enabled: bool
    configuration_valid: bool
    integration_status: Dict[str, bool]
    last_updated: Optional[datetime] = None
    version: str = "1.0.0"
    
    # Statistics
    total_gift_categories: Optional[int] = None
    total_gift_occasions: Optional[int] = None
    total_budget_ranges: Optional[int] = None


# Gift Database Models Schemas

class GiftBase(BaseModel):
    """Base schema for gift"""
    title: str = Field(..., max_length=255, description="Gift title")
    description: Optional[str] = Field(None, description="Gift description")
    category: Optional[str] = Field(None, max_length=100, description="Gift category")
    recipient_name: Optional[str] = Field(None, max_length=255, description="Recipient name if not a contact")
    occasion: Optional[str] = Field(None, max_length=100, description="Occasion for the gift")
    occasion_date: Optional[date] = Field(None, description="Date of the occasion")
    budget_amount: Optional[Decimal] = Field(None, description="Budget amount for the gift")
    actual_amount: Optional[Decimal] = Field(None, description="Actual amount spent")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    status: GiftStatus = Field(default=GiftStatus.IDEA, description="Gift status")
    priority: GiftPriority = Field(default=GiftPriority.MEDIUM, description="Gift priority")
    store_name: Optional[str] = Field(None, max_length=255, description="Store name")
    purchase_url: Optional[str] = Field(None, description="Purchase URL")
    purchase_date: Optional[date] = Field(None, description="Purchase date")
    gift_details: Dict[str, Any] = Field(default_factory=dict, description="Additional gift details")
    tracking_number: Optional[str] = Field(None, max_length=255, description="Tracking number")
    delivery_date: Optional[date] = Field(None, description="Delivery date")
    notes: Optional[str] = Field(None, description="Additional notes")
    image_url: Optional[str] = Field(None, description="Gift image URL")
    reminder_dates: Dict[str, Any] = Field(default_factory=dict, description="Reminder dates")
    task_id: Optional[int] = Field(None, description="Associated task ID")
    transaction_id: Optional[int] = Field(None, description="Associated transaction ID")
    is_surprise: bool = Field(default=False, description="Whether this is a surprise gift")


class GiftCreate(GiftBase):
    """Schema for creating a gift"""
    recipient_contact_id: Optional[int] = Field(None, description="ID of recipient contact")


class GiftUpdate(BaseModel):
    """Schema for updating a gift"""
    title: Optional[str] = Field(None, max_length=255, description="Gift title")
    description: Optional[str] = Field(None, description="Gift description")
    category: Optional[str] = Field(None, max_length=100, description="Gift category")
    recipient_contact_id: Optional[int] = Field(None, description="ID of recipient contact")
    recipient_name: Optional[str] = Field(None, max_length=255, description="Recipient name")
    occasion: Optional[str] = Field(None, max_length=100, description="Occasion")
    occasion_date: Optional[date] = Field(None, description="Occasion date")
    budget_amount: Optional[Decimal] = Field(None, description="Budget amount")
    actual_amount: Optional[Decimal] = Field(None, description="Actual amount")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    status: Optional[GiftStatus] = Field(None, description="Gift status")
    priority: Optional[GiftPriority] = Field(None, description="Gift priority")
    store_name: Optional[str] = Field(None, max_length=255, description="Store name")
    purchase_url: Optional[str] = Field(None, description="Purchase URL")
    purchase_date: Optional[date] = Field(None, description="Purchase date")
    gift_details: Optional[Dict[str, Any]] = Field(None, description="Gift details")
    tracking_number: Optional[str] = Field(None, max_length=255, description="Tracking number")
    delivery_date: Optional[date] = Field(None, description="Delivery date")
    notes: Optional[str] = Field(None, description="Notes")
    image_url: Optional[str] = Field(None, description="Image URL")
    reminder_dates: Optional[Dict[str, Any]] = Field(None, description="Reminder dates")
    task_id: Optional[int] = Field(None, description="Task ID")
    transaction_id: Optional[int] = Field(None, description="Transaction ID")
    is_surprise: Optional[bool] = Field(None, description="Is surprise gift")


class Gift(GiftBase):
    """Schema for gift with database fields"""
    id: int
    tenant_id: int
    user_id: int
    recipient_contact_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GiftIdeaBase(BaseModel):
    """Base schema for gift idea"""
    title: str = Field(..., max_length=255, description="Gift idea title")
    description: Optional[str] = Field(None, description="Gift idea description")
    category: Optional[str] = Field(None, max_length=100, description="Gift category")
    target_demographic: Optional[str] = Field(None, max_length=100, description="Target demographic")
    suitable_occasions: List[str] = Field(default_factory=list, description="Suitable occasions")
    price_range_min: Optional[Decimal] = Field(None, description="Minimum price range")
    price_range_max: Optional[Decimal] = Field(None, description="Maximum price range")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    idea_details: Dict[str, Any] = Field(default_factory=dict, description="Idea details")
    source_url: Optional[str] = Field(None, description="Source URL")
    source_description: Optional[str] = Field(None, description="Source description")
    image_url: Optional[str] = Field(None, description="Image URL")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5 stars)")
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    is_favorite: bool = Field(default=False, description="Is favorite idea")


class GiftIdeaCreate(GiftIdeaBase):
    """Schema for creating a gift idea"""
    target_contact_id: Optional[int] = Field(None, description="ID of target contact")


class GiftIdeaUpdate(BaseModel):
    """Schema for updating a gift idea"""
    title: Optional[str] = Field(None, max_length=255, description="Gift idea title")
    description: Optional[str] = Field(None, description="Description")
    category: Optional[str] = Field(None, max_length=100, description="Category")
    target_contact_id: Optional[int] = Field(None, description="Target contact ID")
    target_demographic: Optional[str] = Field(None, max_length=100, description="Target demographic")
    suitable_occasions: Optional[List[str]] = Field(None, description="Suitable occasions")
    price_range_min: Optional[Decimal] = Field(None, description="Min price range")
    price_range_max: Optional[Decimal] = Field(None, description="Max price range")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    idea_details: Optional[Dict[str, Any]] = Field(None, description="Idea details")
    source_url: Optional[str] = Field(None, description="Source URL")
    source_description: Optional[str] = Field(None, description="Source description")
    image_url: Optional[str] = Field(None, description="Image URL")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5)")
    notes: Optional[str] = Field(None, description="Notes")
    tags: Optional[List[str]] = Field(None, description="Tags")
    is_favorite: Optional[bool] = Field(None, description="Is favorite")


class GiftIdea(GiftIdeaBase):
    """Schema for gift idea with database fields"""
    id: int
    tenant_id: int
    user_id: int
    target_contact_id: Optional[int] = None
    times_gifted: int = 0
    last_gifted_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True