from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Base Transaction Category schema
class TransactionCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: Optional[str] = Field(None, pattern="^(income|expense|transfer)$")
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)

# Create Transaction Category schema
class TransactionCategoryCreate(TransactionCategoryBase):
    pass

# Update Transaction Category schema
class TransactionCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, pattern="^(income|expense|transfer)$")
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)

# Transaction Category schema with database fields
class TransactionCategoryInDBBase(TransactionCategoryBase):
    id: int
    user_id: Optional[int] = None
    tenant_id: int
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionCategory(TransactionCategoryInDBBase):
    pass

class TransactionCategoryInDB(TransactionCategoryInDBBase):
    pass

# Transaction Category with subcategories
class TransactionCategoryWithSubcategories(TransactionCategory):
    subcategories: List['TransactionSubcategory'] = []

# Update forward references  
from app.schemas.transaction_subcategory import TransactionSubcategory

TransactionCategoryWithSubcategories.model_rebuild()