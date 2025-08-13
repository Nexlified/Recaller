from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# Base Transaction schema
class TransactionBase(BaseModel):
    type: str = Field(..., regex="^(credit|debit)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    description: Optional[str] = None
    transaction_date: date
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    account_id: Optional[int] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    is_recurring: bool = False
    recurring_template_id: Optional[int] = None
    attachments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Create Transaction schema
class TransactionCreate(TransactionBase):
    pass

# Update Transaction schema
class TransactionUpdate(BaseModel):
    type: Optional[str] = Field(None, regex="^(credit|debit)$")
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    currency: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    account_id: Optional[int] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    is_recurring: Optional[bool] = None
    recurring_template_id: Optional[int] = None
    attachments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Transaction schema with relationships
class TransactionInDBBase(TransactionBase):
    id: int
    user_id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Transaction(TransactionInDBBase):
    pass

class TransactionInDB(TransactionInDBBase):
    pass

# Transaction with details (includes category, account info)
class TransactionWithDetails(Transaction):
    category: Optional['TransactionCategory'] = None
    subcategory: Optional['TransactionSubcategory'] = None
    account: Optional['FinancialAccount'] = None
    recurring_template: Optional['RecurringTransaction'] = None

# Update forward references
from app.schemas.transaction_category import TransactionCategory
from app.schemas.transaction_subcategory import TransactionSubcategory
from app.schemas.financial_account import FinancialAccount
from app.schemas.recurring_transaction import RecurringTransaction as RecurringTransactionSchema

TransactionWithDetails.model_rebuild()