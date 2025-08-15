from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Base Currency schema
class CurrencyBase(BaseModel):
    code: str = Field(..., max_length=3, min_length=3, description="ISO 4217 currency code")
    name: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=10)
    decimal_places: int = Field(default=2, ge=0, le=4)
    is_active: bool = True
    is_default: bool = False
    country_codes: Optional[List[str]] = None

# Create Currency schema
class CurrencyCreate(CurrencyBase):
    pass

# Update Currency schema
class CurrencyUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=3, min_length=3)
    name: Optional[str] = Field(None, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    decimal_places: Optional[int] = Field(None, ge=0, le=4)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    country_codes: Optional[List[str]] = None

# Currency schema with database fields
class CurrencyInDBBase(CurrencyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Currency(CurrencyInDBBase):
    pass

class CurrencyInDB(CurrencyInDBBase):
    pass

# Response schema for list endpoints
class CurrencyList(BaseModel):
    currencies: List[Currency]
    total: int
    active_count: int
    default_currency: Optional[Currency] = None