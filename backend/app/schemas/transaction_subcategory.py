from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# Base Transaction Subcategory schema
class TransactionSubcategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    budget_limit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)

# Create Transaction Subcategory schema
class TransactionSubcategoryCreate(TransactionSubcategoryBase):
    category_id: int

# Update Transaction Subcategory schema
class TransactionSubcategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    budget_limit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)

# Transaction Subcategory schema with database fields
class TransactionSubcategoryInDBBase(TransactionSubcategoryBase):
    id: int
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionSubcategory(TransactionSubcategoryInDBBase):
    pass

class TransactionSubcategoryInDB(TransactionSubcategoryInDBBase):
    pass