from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

# Base Recurring Transaction schema
class RecurringTransactionBase(BaseModel):
    template_name: str = Field(..., max_length=200)
    type: str = Field(..., regex="^(credit|debit)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    description: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    account_id: Optional[int] = None
    frequency: str = Field(..., regex="^(daily|weekly|monthly|quarterly|yearly)$")
    interval_count: int = Field(default=1, ge=1)
    start_date: date
    end_date: Optional[date] = None
    reminder_days: int = Field(default=3, ge=0)
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and info.data.get('start_date') and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

# Create Recurring Transaction schema
class RecurringTransactionCreate(RecurringTransactionBase):
    pass

# Update Recurring Transaction schema
class RecurringTransactionUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=200)
    type: Optional[str] = Field(None, regex="^(credit|debit)$")
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    currency: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    account_id: Optional[int] = None
    frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly|quarterly|yearly)$")
    interval_count: Optional[int] = Field(None, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reminder_days: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

# Recurring Transaction schema with database fields
class RecurringTransactionInDBBase(RecurringTransactionBase):
    id: int
    user_id: int
    tenant_id: int
    next_due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RecurringTransaction(RecurringTransactionInDBBase):
    pass

class RecurringTransactionInDB(RecurringTransactionInDBBase):
    pass

# Recurring Transaction with next occurrence info
class RecurringTransactionWithNext(RecurringTransaction):
    next_occurrence_date: Optional[date] = None
    days_until_next: Optional[int] = None