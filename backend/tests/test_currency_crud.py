"""
Tests for currency CRUD operations
"""
import pytest
from sqlalchemy.orm import Session

from app.crud import currency as crud_currency
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate


def test_create_currency(db: Session):
    """Test creating a new currency"""
    currency_data = CurrencyCreate(
        code="EUR",
        name="Euro",
        symbol="€",
        decimal_places=2,
        is_active=True,
        is_default=False,
        country_codes=["DE", "FR", "IT"]
    )
    
    currency = crud_currency.create_currency(db, currency_data)
    assert currency.code == "EUR"
    assert currency.name == "Euro"
    assert currency.symbol == "€"
    assert currency.decimal_places == 2
    assert currency.is_active is True
    assert currency.is_default is False
    assert currency.country_codes == ["DE", "FR", "IT"]


def test_get_currency_by_code(db: Session):
    """Test retrieving a currency by code"""
    # Create a currency first
    currency_data = CurrencyCreate(
        code="USD",
        name="US Dollar",
        symbol="$",
        decimal_places=2,
        is_active=True,
        is_default=True,
        country_codes=["US"]
    )
    created = crud_currency.create_currency(db, currency_data)
    
    # Retrieve by code
    retrieved = crud_currency.get_currency_by_code(db, "USD")
    assert retrieved is not None
    assert retrieved.code == "USD"
    assert retrieved.id == created.id


def test_get_active_currencies(db: Session):
    """Test retrieving only active currencies"""
    # Create active currency
    active_currency = CurrencyCreate(
        code="GBP",
        name="British Pound",
        symbol="£",
        decimal_places=2,
        is_active=True,
        is_default=False,
        country_codes=["GB"]
    )
    crud_currency.create_currency(db, active_currency)
    
    # Create inactive currency
    inactive_currency = CurrencyCreate(
        code="OLD",
        name="Old Currency",
        symbol="O",
        decimal_places=2,
        is_active=False,
        is_default=False,
        country_codes=["XX"]
    )
    crud_currency.create_currency(db, inactive_currency)
    
    # Get active currencies
    active_currencies = crud_currency.get_active_currencies(db)
    codes = [c.code for c in active_currencies]
    assert "GBP" in codes
    assert "OLD" not in codes


def test_set_default_currency(db: Session):
    """Test setting a currency as default"""
    # Create two currencies
    usd = crud_currency.create_currency(db, CurrencyCreate(
        code="USD", name="US Dollar", symbol="$", decimal_places=2,
        is_active=True, is_default=True
    ))
    
    eur = crud_currency.create_currency(db, CurrencyCreate(
        code="EUR", name="Euro", symbol="€", decimal_places=2,
        is_active=True, is_default=False
    ))
    
    # Set EUR as default
    result = crud_currency.set_default_currency(db, eur.id)
    
    assert result.is_default is True
    
    # Check that USD is no longer default
    updated_usd = crud_currency.get_currency(db, usd.id)
    assert updated_usd.is_default is False


def test_validate_currency_code(db: Session):
    """Test currency code validation"""
    # Create an active currency
    crud_currency.create_currency(db, CurrencyCreate(
        code="JPY", name="Japanese Yen", symbol="¥", decimal_places=0,
        is_active=True, is_default=False
    ))
    
    # Create an inactive currency
    crud_currency.create_currency(db, CurrencyCreate(
        code="OLD", name="Old Currency", symbol="O", decimal_places=2,
        is_active=False, is_default=False
    ))
    
    # Test validation
    assert crud_currency.validate_currency_code(db, "JPY") is True
    assert crud_currency.validate_currency_code(db, "OLD") is False
    assert crud_currency.validate_currency_code(db, "XXX") is False


def test_get_currencies_by_country(db: Session):
    """Test retrieving currencies by country code"""
    # Create currencies with different countries
    usd = crud_currency.create_currency(db, CurrencyCreate(
        code="USD", name="US Dollar", symbol="$", decimal_places=2,
        is_active=True, is_default=False, country_codes=["US"]
    ))
    
    eur = crud_currency.create_currency(db, CurrencyCreate(
        code="EUR", name="Euro", symbol="€", decimal_places=2,
        is_active=True, is_default=False, country_codes=["DE", "FR", "IT"]
    ))
    
    # Test getting currencies by country
    us_currencies = crud_currency.get_currencies_by_country(db, "US")
    assert len(us_currencies) == 1
    assert us_currencies[0].code == "USD"
    
    de_currencies = crud_currency.get_currencies_by_country(db, "DE")
    assert len(de_currencies) == 1
    assert de_currencies[0].code == "EUR"
    
    xx_currencies = crud_currency.get_currencies_by_country(db, "XX")
    assert len(xx_currencies) == 0