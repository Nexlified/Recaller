from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# Base Financial Account schema
class FinancialAccountBase(BaseModel):
    account_name: str = Field(..., max_length=100)
    account_type: Optional[str] = Field(None, max_length=50)
    account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    current_balance: Decimal = Field(default=0, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    is_active: bool = True

# Create Financial Account schema
class FinancialAccountCreate(FinancialAccountBase):
    pass

# Update Financial Account schema
class FinancialAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, max_length=100)
    account_type: Optional[str] = Field(None, max_length=50)
    account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    current_balance: Optional[Decimal] = Field(None, decimal_places=2)
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None

# Financial Account schema with database fields
class FinancialAccountInDBBase(FinancialAccountBase):
    id: int
    user_id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FinancialAccount(FinancialAccountInDBBase):
    pass

class FinancialAccountInDB(FinancialAccountInDBBase):
    pass

# Financial Account with transaction summary
class FinancialAccountWithSummary(FinancialAccount):
    transaction_count: int
    total_credits: Decimal
    total_debits: Decimal
    last_transaction_date: Optional[datetime] = None