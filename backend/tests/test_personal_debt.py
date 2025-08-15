import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models.personal_debt import PersonalDebt, DebtPayment, DebtType, DebtStatus, PaymentStatus, ReminderFrequency
from app.schemas.personal_debt import PersonalDebtCreate, DebtPaymentCreate


def test_personal_debt_model():
    """Test PersonalDebt model basic functionality."""
    debt = PersonalDebt(
        user_id=1,
        tenant_id=1,
        creditor_contact_id=1,
        debtor_contact_id=2,
        debt_type=DebtType.PERSONAL_LOAN,
        amount=Decimal("1000.00"),
        currency="USD",
        description="Test personal loan",
        status=DebtStatus.ACTIVE,
        payment_status=PaymentStatus.UNPAID,
        reminder_frequency=ReminderFrequency.NEVER
    )
    
    assert debt.debt_type == DebtType.PERSONAL_LOAN
    assert debt.amount == Decimal("1000.00")
    assert debt.currency == "USD"
    assert debt.status == DebtStatus.ACTIVE
    assert debt.payment_status == PaymentStatus.UNPAID


def test_debt_payment_model():
    """Test DebtPayment model basic functionality."""
    payment = DebtPayment(
        debt_id=1,
        amount=Decimal("500.00"),
        payment_date=date.today(),
        payment_method="bank_transfer",
        notes="First payment"
    )
    
    assert payment.debt_id == 1
    assert payment.amount == Decimal("500.00")
    assert payment.payment_method == "bank_transfer"
    assert payment.notes == "First payment"


def test_personal_debt_create_schema():
    """Test PersonalDebtCreate schema validation."""
    debt_data = PersonalDebtCreate(
        creditor_contact_id=1,
        debtor_contact_id=2,
        debt_type=DebtType.BORROWED_MONEY,
        amount=Decimal("750.00"),
        currency="EUR",
        description="Borrowed money for trip",
        due_date=date(2024, 12, 31)
    )
    
    assert debt_data.debt_type == DebtType.BORROWED_MONEY
    assert debt_data.amount == Decimal("750.00")
    assert debt_data.currency == "EUR"
    assert debt_data.due_date == date(2024, 12, 31)


def test_debt_payment_create_schema():
    """Test DebtPaymentCreate schema validation."""
    payment_data = DebtPaymentCreate(
        debt_id=1,
        amount=Decimal("250.00"),
        payment_date=date.today(),
        payment_method="cash",
        notes="Partial payment"
    )
    
    assert payment_data.debt_id == 1
    assert payment_data.amount == Decimal("250.00")
    assert payment_data.payment_method == "cash"
    assert payment_data.notes == "Partial payment"


def test_debt_type_enum():
    """Test DebtType enum values."""
    assert DebtType.PERSONAL_LOAN == "personal_loan"
    assert DebtType.BORROWED_MONEY == "borrowed_money"
    assert DebtType.SHARED_EXPENSE == "shared_expense"
    assert DebtType.FAVOR_OWED == "favor_owed"


def test_debt_status_enum():
    """Test DebtStatus enum values."""
    assert DebtStatus.ACTIVE == "active"
    assert DebtStatus.PAID == "paid"
    assert DebtStatus.FORGIVEN == "forgiven"
    assert DebtStatus.DISPUTED == "disputed"


def test_payment_status_enum():
    """Test PaymentStatus enum values."""
    assert PaymentStatus.UNPAID == "unpaid"
    assert PaymentStatus.PARTIAL == "partial"
    assert PaymentStatus.PAID == "paid"


def test_reminder_frequency_enum():
    """Test ReminderFrequency enum values."""
    assert ReminderFrequency.NEVER == "never"
    assert ReminderFrequency.WEEKLY == "weekly"
    assert ReminderFrequency.MONTHLY == "monthly"