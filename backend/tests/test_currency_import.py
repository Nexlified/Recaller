"""
Tests for currency import functionality
"""
import pytest
import yaml
from unittest.mock import patch, mock_open
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.crud import currency as crud_currency


def test_import_currencies_from_yaml(db: Session):
    """Test importing currencies from YAML configuration"""
    
    # Mock YAML data matching the existing format
    mock_yaml_content = """
---
version: "1.0.0"
category: "core"
type: "currencies"
name: "Currencies"
description: "ISO 4217 currency codes and symbols"

metadata:
  author: "Recaller Team"
  last_updated: "2024-01-01"
  deprecated: false

values:
  - key: "usd"
    display_name: "US Dollar"
    description: "United States Dollar"
    sort_order: 0
    is_system: true
    is_active: true
    metadata:
      iso_code: "USD"
      symbol: "$"
      numeric_code: "840"
      decimal_places: 2
      countries: ["US"]
    tags: ["currency", "major", "north_america"]

  - key: "eur"
    display_name: "Euro"
    description: "European Union Euro"
    sort_order: 1
    is_system: true
    is_active: true
    metadata:
      iso_code: "EUR"
      symbol: "€"
      numeric_code: "978"
      decimal_places: 2
      countries: ["DE", "FR"]
    tags: ["currency", "major", "europe"]

  - key: "jpy"
    display_name: "Japanese Yen"
    description: "Japanese Yen"
    sort_order: 3
    is_system: true
    is_active: true
    metadata:
      iso_code: "JPY"
      symbol: "¥"
      numeric_code: "392"
      decimal_places: 0
      countries: ["JP"]
    tags: ["currency", "major", "asia"]
"""
    
    # Import the import function and mock file reading
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "scripts"))
    
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        with patch("pathlib.Path.exists", return_value=True):
            # Import the function 
            from import_currencies import load_currencies_config, import_currencies
            
            # Mock the database session
            with patch("import_currencies.SessionLocal", return_value=db):
                # Test loading config
                config = load_currencies_config()
                assert config["category"] == "core"
                assert len(config["values"]) == 3
                
                # Test import process
                import_currencies()
    
    # Verify currencies were imported
    currencies = crud_currency.get_currencies(db)
    assert len(currencies) == 3
    
    # Check specific currencies
    usd = crud_currency.get_currency_by_code(db, "USD")
    assert usd is not None
    assert usd.name == "US Dollar"
    assert usd.symbol == "$"
    assert usd.decimal_places == 2
    assert usd.is_default is True  # USD should be set as default
    
    eur = crud_currency.get_currency_by_code(db, "EUR")
    assert eur is not None
    assert eur.name == "Euro"
    assert eur.symbol == "€"
    assert eur.decimal_places == 2
    assert eur.is_default is False
    
    jpy = crud_currency.get_currency_by_code(db, "JPY")
    assert jpy is not None
    assert jpy.name == "Japanese Yen"
    assert jpy.symbol == "¥"
    assert jpy.decimal_places == 0  # Important: JPY has 0 decimal places
    assert jpy.is_default is False


def test_import_currencies_update_existing(db: Session):
    """Test that import updates existing currencies"""
    
    # Create an existing currency with old data
    existing = crud_currency.create_currency(db, {
        "code": "USD",
        "name": "Old US Dollar",
        "symbol": "$$",
        "decimal_places": 3,
        "is_active": False,
        "is_default": False,
        "country_codes": []
    })
    
    # Mock YAML with updated data
    mock_yaml_content = """
values:
  - key: "usd"
    display_name: "US Dollar"
    is_active: true
    metadata:
      iso_code: "USD"
      symbol: "$"
      decimal_places: 2
      countries: ["US"]
"""
    
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "scripts"))
    
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        with patch("pathlib.Path.exists", return_value=True):
            from import_currencies import import_currencies
            
            with patch("import_currencies.SessionLocal", return_value=db):
                import_currencies()
    
    # Check that existing currency was updated
    updated = crud_currency.get_currency_by_code(db, "USD")
    assert updated.id == existing.id  # Same currency
    assert updated.name == "US Dollar"  # Updated name
    assert updated.symbol == "$"  # Updated symbol
    assert updated.decimal_places == 2  # Updated decimal places
    assert updated.is_active is True  # Updated active status
    assert updated.country_codes == ["US"]  # Updated countries


def test_import_currencies_validation():
    """Test import script validation functions"""
    
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "scripts"))
    
    from sqlalchemy.orm import Session
    
    # Mock a database with currencies
    with patch("import_currencies.SessionLocal") as mock_session:
        mock_db = mock_session.return_value
        
        # Mock currency queries
        mock_db.query.return_value.count.return_value = 5
        mock_db.query.return_value.filter.return_value.count.return_value = 4
        mock_db.query.return_value.filter.return_value.first.return_value = type('obj', (object,), {'code': 'USD'})()
        
        from import_currencies import validate_import
        
        # Test validation passes with proper data
        result = validate_import()
        assert result is True


def test_currency_import_error_handling(db: Session):
    """Test error handling in currency import"""
    
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "scripts"))
    
    # Test file not found
    with patch("pathlib.Path.exists", return_value=False):
        from import_currencies import load_currencies_config
        
        with pytest.raises(FileNotFoundError):
            load_currencies_config()
    
    # Test invalid YAML
    with patch("builtins.open", mock_open(read_data="invalid: yaml: content: [")):
        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(yaml.YAMLError):
                load_currencies_config()


def test_default_currency_logic(db: Session):
    """Test that USD is correctly set as default currency"""
    
    mock_yaml_content = """
values:
  - key: "eur"
    display_name: "Euro"
    is_active: true
    metadata:
      iso_code: "EUR"
      symbol: "€"
      decimal_places: 2
      countries: ["DE"]
  
  - key: "usd" 
    display_name: "US Dollar"
    is_active: true
    metadata:
      iso_code: "USD"
      symbol: "$"
      decimal_places: 2
      countries: ["US"]
"""
    
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "scripts"))
    
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        with patch("pathlib.Path.exists", return_value=True):
            from import_currencies import import_currencies
            
            with patch("import_currencies.SessionLocal", return_value=db):
                import_currencies()
    
    # Verify USD is set as default
    usd = crud_currency.get_currency_by_code(db, "USD")
    assert usd.is_default is True
    
    # Verify EUR is not default
    eur = crud_currency.get_currency_by_code(db, "EUR")
    assert eur.is_default is False
    
    # Verify only one default currency exists
    default_currencies = db.query(Currency).filter(Currency.is_default == True).all()
    assert len(default_currencies) == 1
    assert default_currencies[0].code == "USD"