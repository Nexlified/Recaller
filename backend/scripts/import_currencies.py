#!/usr/bin/env python3
"""
Import currencies from YAML configuration into database
"""
import yaml
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.currency import Currency

def load_currencies_config():
    """Load currencies from YAML configuration"""
    config_path = Path(__file__).parent.parent.parent / "config" / "currencies.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Currency configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def import_currencies():
    """Import currencies from config into database"""
    db = SessionLocal()
    try:
        config = load_currencies_config()
        currencies_data = config['currencies']
        
        imported_count = 0
        updated_count = 0
        
        for currency_info in currencies_data:
            # Extract currency data from simplified YAML structure
            code = currency_info['code']
            name = currency_info['name']
            symbol = currency_info['symbol']
            decimal_places = currency_info['decimal_places']
            country_codes = currency_info.get('countries', [])
            is_active = currency_info['is_active']
            is_default = currency_info.get('is_default', False)
            
            # Check if currency already exists
            existing = db.query(Currency).filter(Currency.code == code).first()
            
            if not existing:
                # Create new currency
                currency = Currency(
                    code=code,
                    name=name,
                    symbol=symbol,
                    decimal_places=decimal_places,
                    is_active=is_active,
                    is_default=is_default,
                    country_codes=country_codes
                )
                db.add(currency)
                imported_count += 1
                print(f"Added currency: {code} - {name}")
            else:
                # Update existing currency
                existing.name = name
                existing.symbol = symbol
                existing.decimal_places = decimal_places
                existing.is_active = is_active
                existing.country_codes = country_codes
                # Only set as default if explicitly marked as default
                if is_default:
                    # Clear other defaults first
                    db.query(Currency).filter(Currency.is_default == True).update({Currency.is_default: False})
                    existing.is_default = True
                    
                db.add(existing)
                updated_count += 1
                print(f"Updated currency: {code} - {name}")
        
        db.commit()
        print(f"\nImport completed successfully:")
        print(f"  - {imported_count} currencies imported")
        print(f"  - {updated_count} currencies updated")
        print(f"  - Total currencies in database: {db.query(Currency).count()}")
        
        # Ensure we have a default currency
        default = db.query(Currency).filter(Currency.is_default == True).first()
        if not default:
            usd = db.query(Currency).filter(Currency.code == 'USD').first()
            if usd:
                usd.is_default = True
                db.add(usd)
                db.commit()
                print(f"Set USD as default currency")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing currencies: {e}")
        raise
    finally:
        db.close()

def validate_import():
    """Validate the imported currencies"""
    db = SessionLocal()
    try:
        total = db.query(Currency).count()
        active = db.query(Currency).filter(Currency.is_active == True).count()
        default = db.query(Currency).filter(Currency.is_default == True).first()
        
        print(f"\nValidation Results:")
        print(f"  - Total currencies: {total}")
        print(f"  - Active currencies: {active}")
        print(f"  - Default currency: {default.code if default else 'None'}")
        
        if total == 0:
            print("  ❌ No currencies found in database")
            return False
        
        if not default:
            print("  ❌ No default currency set")
            return False
            
        print("  ✅ Currency import validation passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting currency import...")
    try:
        import_currencies()
        validate_import()
        print("\nCurrency import completed successfully!")
    except Exception as e:
        print(f"\nCurrency import failed: {e}")
        sys.exit(1)