from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

class GiftPrivacyMode(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    STRICT = "strict"

class GiftSuggestionEngine(str, Enum):
    BASIC = "basic"
    ENHANCED = "enhanced"
    AI_POWERED = "ai_powered"

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