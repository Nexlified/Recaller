from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud import currency as crud_currency
from app.schemas.currency import Currency, CurrencyCreate, CurrencyUpdate, CurrencyList
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=CurrencyList)
def get_currencies(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all currencies or active currencies only"""
    if active_only:
        currencies = crud_currency.get_active_currencies(db, skip=skip, limit=limit)
        total = crud_currency.count_active_currencies(db)
    else:
        currencies = crud_currency.get_currencies(db, skip=skip, limit=limit)
        total = db.query(crud_currency.Currency).count()
    
    active_count = crud_currency.count_active_currencies(db)
    default_currency = crud_currency.get_default_currency(db)
    
    return CurrencyList(
        currencies=currencies,
        total=total,
        active_count=active_count,
        default_currency=default_currency
    )

@router.get("/active", response_model=List[Currency])
def get_active_currencies(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get only active currencies - optimized endpoint for dropdowns"""
    return crud_currency.get_active_currencies(db, skip=skip, limit=limit)

@router.get("/default", response_model=Optional[Currency])
def get_default_currency(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the default currency"""
    return crud_currency.get_default_currency(db)

@router.get("/by-country/{country_code}", response_model=List[Currency])
def get_currencies_by_country(
    country_code: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get currencies used in a specific country"""
    if len(country_code) != 2:
        raise HTTPException(status_code=400, detail="Country code must be 2 characters")
    
    return crud_currency.get_currencies_by_country(db, country_code)

@router.get("/{currency_code}", response_model=Currency)
def get_currency_by_code(
    currency_code: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific currency by its ISO code"""
    if len(currency_code) != 3:
        raise HTTPException(status_code=400, detail="Currency code must be 3 characters")
    
    currency = crud_currency.get_currency_by_code(db, currency_code)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    return currency

@router.post("/validate", response_model=dict)
def validate_currency(
    currency_code: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate if a currency code is valid and active"""
    is_valid = crud_currency.validate_currency_code(db, currency_code)
    return {"currency_code": currency_code.upper(), "is_valid": is_valid}

@router.post("/", response_model=Currency)
def create_currency(
    currency: CurrencyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new currency (admin functionality)"""
    # Check if currency already exists
    existing = crud_currency.get_currency_by_code(db, currency.code)
    if existing:
        raise HTTPException(status_code=400, detail="Currency already exists")
    
    return crud_currency.create_currency(db, currency)

@router.put("/{currency_id}", response_model=Currency)
def update_currency(
    currency_id: int,
    currency_update: CurrencyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing currency (admin functionality)"""
    currency = crud_currency.update_currency(db, currency_id, currency_update)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    return currency

@router.post("/{currency_id}/set-default", response_model=Currency)
def set_default_currency(
    currency_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a currency as the default currency (admin functionality)"""
    currency = crud_currency.set_default_currency(db, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    return currency