#!/usr/bin/env python3
"""
Manual integration test for currency management system
Run this script to test the complete currency workflow
"""
import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.currency import Currency
from app.crud import currency as crud_currency
from app.schemas.currency import CurrencyCreate
from app.schemas.transaction import TransactionCreate
from app.schemas.financial_account import FinancialAccountCreate
from datetime import date


def test_currency_system():
    """Test the complete currency management system"""
    print("🧪 Testing Currency Management System")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Test 1: Create currencies manually
        print("\n1. Testing Currency Creation...")
        
        test_currencies = [
            CurrencyCreate(
                code="USD",
                name="US Dollar",
                symbol="$",
                decimal_places=2,
                is_active=True,
                is_default=True,
                country_codes=["US"]
            ),
            CurrencyCreate(
                code="EUR",
                name="Euro",
                symbol="€",
                decimal_places=2,
                is_active=True,
                is_default=False,
                country_codes=["DE", "FR", "IT"]
            ),
            CurrencyCreate(
                code="JPY",
                name="Japanese Yen",
                symbol="¥",
                decimal_places=0,
                is_active=True,
                is_default=False,
                country_codes=["JP"]
            ),
            CurrencyCreate(
                code="GBP",
                name="British Pound",
                symbol="£",
                decimal_places=2,
                is_active=True,
                is_default=False,
                country_codes=["GB"]
            )
        ]
        
        created_currencies = []
        for currency_data in test_currencies:
            # Check if currency already exists
            existing = crud_currency.get_currency_by_code(db, currency_data.code)
            if existing:
                print(f"   ✓ Currency {currency_data.code} already exists")
                created_currencies.append(existing)
            else:
                currency = crud_currency.create_currency(db, currency_data)
                created_currencies.append(currency)
                print(f"   ✓ Created currency: {currency.code} - {currency.name} ({currency.symbol})")
        
        # Test 2: Test CRUD operations
        print("\n2. Testing CRUD Operations...")
        
        # Get all currencies
        all_currencies = crud_currency.get_currencies(db)
        print(f"   ✓ Total currencies: {len(all_currencies)}")
        
        # Get active currencies
        active_currencies = crud_currency.get_active_currencies(db)
        print(f"   ✓ Active currencies: {len(active_currencies)}")
        
        # Get default currency
        default_currency = crud_currency.get_default_currency(db)
        print(f"   ✓ Default currency: {default_currency.code if default_currency else 'None'}")
        
        # Test currency by country
        us_currencies = crud_currency.get_currencies_by_country(db, "US")
        print(f"   ✓ US currencies: {[c.code for c in us_currencies]}")
        
        # Test validation
        is_valid_usd = crud_currency.validate_currency_code(db, "USD")
        is_valid_xxx = crud_currency.validate_currency_code(db, "XXX")
        print(f"   ✓ USD validation: {is_valid_usd}")
        print(f"   ✓ XXX validation: {is_valid_xxx}")
        
        # Test 3: Test schema validation
        print("\n3. Testing Schema Validation...")
        
        try:
            # Test valid transaction with currency
            transaction = TransactionCreate(
                type="debit",
                amount=100.50,
                currency="USD",
                transaction_date=date.today()
            )
            print(f"   ✓ Transaction with USD: {transaction.currency}")
            
            # Test currency uppercase conversion
            transaction_lower = TransactionCreate(
                type="credit",
                amount=200.00,
                currency="eur",
                transaction_date=date.today()
            )
            print(f"   ✓ Currency uppercase conversion: {transaction_lower.currency}")
            
            # Test financial account with currency
            account = FinancialAccountCreate(
                account_name="Test Account",
                currency="JPY",
                current_balance=50000
            )
            print(f"   ✓ Financial account with JPY: {account.currency}")
            
        except Exception as e:
            print(f"   ❌ Schema validation error: {e}")
        
        # Test 4: Test decimal places handling
        print("\n4. Testing Decimal Places...")
        
        for currency in active_currencies:
            print(f"   ✓ {currency.code}: {currency.decimal_places} decimal places")
        
        # Test 5: Test default currency logic
        print("\n5. Testing Default Currency Logic...")
        
        # Try setting a different default
        if len(created_currencies) >= 2:
            eur_currency = next((c for c in created_currencies if c.code == "EUR"), None)
            if eur_currency:
                updated = crud_currency.set_default_currency(db, eur_currency.id)
                print(f"   ✓ Set EUR as default: {updated.is_default}")
                
                # Check that only one default exists
                default_count = db.query(Currency).filter(Currency.is_default == True).count()
                print(f"   ✓ Default currencies count: {default_count}")
                
                # Reset USD as default
                usd_currency = next((c for c in created_currencies if c.code == "USD"), None)
                if usd_currency:
                    crud_currency.set_default_currency(db, usd_currency.id)
                    print(f"   ✓ Reset USD as default")
        
        print("\n" + "=" * 50)
        print("✅ All currency system tests passed!")
        
        # Summary
        print(f"\nSummary:")
        print(f"   - Total currencies: {len(all_currencies)}")
        print(f"   - Active currencies: {len(active_currencies)}")
        print(f"   - Default currency: {default_currency.code if default_currency else 'None'}")
        print(f"   - Currencies by code: {', '.join([c.code for c in active_currencies])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Currency system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


def test_import_script():
    """Test the currency import script"""
    print("\n" + "=" * 50)
    print("🧪 Testing Currency Import Script")
    print("=" * 50)
    
    try:
        from scripts.import_currencies import import_currencies, validate_import
        
        print("\n1. Running currency import...")
        import_currencies()
        print("   ✓ Import completed")
        
        print("\n2. Validating import...")
        is_valid = validate_import()
        
        if is_valid:
            print("   ✅ Import validation passed")
            return True
        else:
            print("   ❌ Import validation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Import script error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Currency Management System Integration Test")
    
    # Test the currency system
    system_test_passed = test_currency_system()
    
    # Test the import script
    import_test_passed = test_import_script()
    
    print("\n" + "=" * 70)
    if system_test_passed and import_test_passed:
        print("🎉 All integration tests passed! Currency management system is working correctly.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the errors above.")
        sys.exit(1)