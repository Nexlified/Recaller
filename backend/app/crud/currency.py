from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyUpdate

def get_currency(db: Session, currency_id: int) -> Optional[Currency]:
    """Get a single currency by ID"""
    return db.query(Currency).filter(Currency.id == currency_id).first()

def get_currency_by_code(db: Session, code: str) -> Optional[Currency]:
    """Get currency by ISO code"""
    return db.query(Currency).filter(Currency.code == code.upper()).first()

def get_currencies(db: Session, skip: int = 0, limit: int = 100) -> List[Currency]:
    """Get all currencies"""
    return (
        db.query(Currency)
        .order_by(Currency.code)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_active_currencies(db: Session, skip: int = 0, limit: int = 100) -> List[Currency]:
    """Get all active currencies"""
    return (
        db.query(Currency)
        .filter(Currency.is_active == True)
        .order_by(Currency.code)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_default_currency(db: Session) -> Optional[Currency]:
    """Get the default currency"""
    return db.query(Currency).filter(Currency.is_default == True).first()

def create_currency(db: Session, currency: CurrencyCreate) -> Currency:
    """Create a new currency"""
    db_currency = Currency(**currency.model_dump())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency

def update_currency(db: Session, currency_id: int, currency_update: CurrencyUpdate) -> Optional[Currency]:
    """Update an existing currency"""
    db_currency = get_currency(db, currency_id)
    if not db_currency:
        return None
    
    update_data = currency_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_currency, field, value)
    
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency

def set_default_currency(db: Session, currency_id: int) -> Optional[Currency]:
    """Set a currency as default (unsets all other defaults)"""
    # First, remove default from all currencies
    db.query(Currency).update({Currency.is_default: False})
    
    # Set the specified currency as default
    currency = get_currency(db, currency_id)
    if currency:
        currency.is_default = True
        db.add(currency)
        db.commit()
        db.refresh(currency)
    return currency

def get_currencies_by_country(db: Session, country_code: str) -> List[Currency]:
    """Get currencies used in a specific country"""
    return (
        db.query(Currency)
        .filter(Currency.country_codes.contains([country_code.upper()]))
        .filter(Currency.is_active == True)
        .order_by(Currency.code)
        .all()
    )

def count_active_currencies(db: Session) -> int:
    """Count active currencies"""
    return db.query(Currency).filter(Currency.is_active == True).count()

def validate_currency_code(db: Session, code: str) -> bool:
    """Validate if a currency code exists and is active"""
    currency = get_currency_by_code(db, code)
    return currency is not None and currency.is_active

def delete_currency(db: Session, currency_id: int) -> bool:
    """Delete a currency (soft delete by setting inactive)"""
    currency = get_currency(db, currency_id)
    if currency:
        currency.is_active = False
        db.add(currency)
        db.commit()
        return True
    return False