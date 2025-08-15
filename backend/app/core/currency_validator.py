"""
Currency validation utilities
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.crud import currency as crud_currency

def validate_currency_code(db: Session, currency_code: str) -> bool:
    """Validate if a currency code exists and is active"""
    return crud_currency.validate_currency_code(db, currency_code)

def get_default_currency_code(db: Session) -> Optional[str]:
    """Get the default currency code"""
    default = crud_currency.get_default_currency(db)
    return default.code if default else "USD"