from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

# Base Budget schema
class BudgetBase(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    budget_amount: Decimal = Field(..., gt=0, decimal_places=2)
    period: str = Field(..., pattern="^(monthly|quarterly|yearly)$")
    start_date: date
    end_date: Optional[date] = None
    alert_percentage: int = Field(default=80, ge=0, le=100)
    is_active: bool = True

    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and info.data.get('start_date') and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

# Create Budget schema
class BudgetCreate(BudgetBase):
    pass

# Update Budget schema
class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    budget_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    period: Optional[str] = Field(None, pattern="^(monthly|quarterly|yearly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    alert_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None

# Budget schema with database fields
class BudgetInDBBase(BudgetBase):
    id: int
    user_id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Budget(BudgetInDBBase):
    pass

class BudgetInDB(BudgetInDBBase):
    pass

# Budget with spending summary
class BudgetWithSummary(Budget):
    spent_amount: Decimal
    remaining_amount: Decimal
    spent_percentage: float
    is_over_budget: bool
    days_remaining: int