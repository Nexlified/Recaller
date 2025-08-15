"""
Tests for currency schema validation
"""
import pytest
from pydantic import ValidationError

from app.schemas.currency import CurrencyCreate, CurrencyUpdate
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.schemas.financial_account import FinancialAccountCreate, FinancialAccountUpdate
from app.schemas.recurring_transaction import RecurringTransactionCreate, RecurringTransactionUpdate
from datetime import date


class TestCurrencySchemas:
    """Test currency schema validation"""
    
    def test_currency_create_valid(self):
        """Test valid currency creation"""
        currency = CurrencyCreate(
            code="USD",
            name="US Dollar", 
            symbol="$",
            decimal_places=2,
            is_active=True,
            is_default=False,
            country_codes=["US"]
        )
        assert currency.code == "USD"
        assert currency.decimal_places == 2
    
    def test_currency_code_validation(self):
        """Test currency code validation"""
        # Valid 3-letter code
        currency = CurrencyCreate(
            code="EUR",
            name="Euro",
            symbol="€"
        )
        assert currency.code == "EUR"
        
        # Invalid length codes should fail
        with pytest.raises(ValidationError):
            CurrencyCreate(
                code="EU",  # Too short
                name="Euro",
                symbol="€"
            )
        
        with pytest.raises(ValidationError):
            CurrencyCreate(
                code="EURO",  # Too long
                name="Euro", 
                symbol="€"
            )
    
    def test_decimal_places_validation(self):
        """Test decimal places validation"""
        # Valid decimal places
        currency = CurrencyCreate(
            code="JPY",
            name="Japanese Yen",
            symbol="¥",
            decimal_places=0
        )
        assert currency.decimal_places == 0
        
        # Invalid decimal places (negative)
        with pytest.raises(ValidationError):
            CurrencyCreate(
                code="USD",
                name="US Dollar",
                symbol="$",
                decimal_places=-1
            )
        
        # Invalid decimal places (too many)
        with pytest.raises(ValidationError):
            CurrencyCreate(
                code="USD",
                name="US Dollar", 
                symbol="$",
                decimal_places=5
            )


class TestTransactionCurrencyValidation:
    """Test currency validation in transaction schemas"""
    
    def test_transaction_create_currency_validation(self):
        """Test currency validation in transaction creation"""
        # Valid currency code
        transaction = TransactionCreate(
            type="debit",
            amount=100.50,
            currency="USD",
            transaction_date=date.today()
        )
        assert transaction.currency == "USD"
        
        # Currency should be converted to uppercase
        transaction = TransactionCreate(
            type="debit",
            amount=100.50,
            currency="usd",
            transaction_date=date.today()
        )
        assert transaction.currency == "USD"
        
        # Invalid currency length
        with pytest.raises(ValidationError):
            TransactionCreate(
                type="debit",
                amount=100.50,
                currency="US",  # Too short
                transaction_date=date.today()
            )
        
        # Invalid currency characters
        with pytest.raises(ValidationError):
            TransactionCreate(
                type="debit",
                amount=100.50,
                currency="US1",  # Contains number
                transaction_date=date.today()
            )
    
    def test_transaction_update_currency_validation(self):
        """Test currency validation in transaction updates"""
        # Valid update
        update = TransactionUpdate(currency="EUR")
        assert update.currency == "EUR"
        
        # Uppercase conversion
        update = TransactionUpdate(currency="gbp")
        assert update.currency == "GBP"
        
        # Invalid length
        with pytest.raises(ValidationError):
            TransactionUpdate(currency="E")


class TestFinancialAccountCurrencyValidation:
    """Test currency validation in financial account schemas"""
    
    def test_financial_account_create_currency_validation(self):
        """Test currency validation in account creation"""
        # Valid account with currency
        account = FinancialAccountCreate(
            account_name="Test Account",
            currency="EUR"
        )
        assert account.currency == "EUR"
        
        # Uppercase conversion
        account = FinancialAccountCreate(
            account_name="Test Account", 
            currency="cad"
        )
        assert account.currency == "CAD"
        
        # Invalid currency
        with pytest.raises(ValidationError):
            FinancialAccountCreate(
                account_name="Test Account",
                currency="XX"  # Too short
            )
    
    def test_financial_account_update_currency_validation(self):
        """Test currency validation in account updates"""
        # Valid update
        update = FinancialAccountUpdate(currency="JPY")
        assert update.currency == "JPY"
        
        # Invalid currency
        with pytest.raises(ValidationError):
            FinancialAccountUpdate(currency="INVALID")


class TestRecurringTransactionCurrencyValidation:
    """Test currency validation in recurring transaction schemas"""
    
    def test_recurring_transaction_create_currency_validation(self):
        """Test currency validation in recurring transaction creation"""
        # Valid recurring transaction
        recurring = RecurringTransactionCreate(
            template_name="Monthly Salary",
            type="credit",
            amount=5000.00,
            currency="USD",
            frequency="monthly",
            start_date=date.today()
        )
        assert recurring.currency == "USD"
        
        # Uppercase conversion
        recurring = RecurringTransactionCreate(
            template_name="Monthly Salary",
            type="credit", 
            amount=5000.00,
            currency="eur",
            frequency="monthly",
            start_date=date.today()
        )
        assert recurring.currency == "EUR"
        
        # Invalid currency
        with pytest.raises(ValidationError):
            RecurringTransactionCreate(
                template_name="Monthly Salary",
                type="credit",
                amount=5000.00,
                currency="E",  # Too short
                frequency="monthly", 
                start_date=date.today()
            )
    
    def test_recurring_transaction_update_currency_validation(self):
        """Test currency validation in recurring transaction updates"""
        # Valid update
        update = RecurringTransactionUpdate(currency="CHF")
        assert update.currency == "CHF"
        
        # Invalid currency
        with pytest.raises(ValidationError):
            RecurringTransactionUpdate(currency="1USD")