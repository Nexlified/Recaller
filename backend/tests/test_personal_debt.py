import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.personal_debt import PersonalDebt, DebtPayment, DebtType, DebtStatus, PaymentStatus, ReminderFrequency
from app.crud import personal_debt as debt_crud
from app.schemas.personal_debt import PersonalDebtCreate, DebtPaymentCreate


def test_create_personal_debt(db_session: Session, test_user, test_tenant):
    """Test creating a personal debt."""
    # Create two test contacts first
    from app.models.contact import Contact
    
    creditor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="John",
        last_name="Creditor",
        email="john@example.com"
    )
    db_session.add(creditor_contact)
    
    debtor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="Jane",
        last_name="Debtor",
        email="jane@example.com"
    )
    db_session.add(debtor_contact)
    db_session.commit()
    db_session.refresh(creditor_contact)
    db_session.refresh(debtor_contact)
    
    # Create personal debt
    debt_data = PersonalDebtCreate(
        creditor_contact_id=creditor_contact.id,
        debtor_contact_id=debtor_contact.id,
        debt_type=DebtType.PERSONAL_LOAN,
        amount=Decimal("1000.00"),
        currency="USD",
        description="Personal loan for car repair",
        due_date=date(2024, 12, 31)
    )
    
    debt = debt_crud.create_personal_debt(
        db=db_session,
        obj_in=debt_data,
        user_id=test_user.id,
        tenant_id=test_tenant.id
    )
    
    assert debt.id is not None
    assert debt.user_id == test_user.id
    assert debt.tenant_id == test_tenant.id
    assert debt.creditor_contact_id == creditor_contact.id
    assert debt.debtor_contact_id == debtor_contact.id
    assert debt.debt_type == DebtType.PERSONAL_LOAN
    assert debt.amount == Decimal("1000.00")
    assert debt.currency == "USD"
    assert debt.description == "Personal loan for car repair"
    assert debt.status == DebtStatus.ACTIVE
    assert debt.payment_status == PaymentStatus.UNPAID
    assert debt.reminder_frequency == ReminderFrequency.NEVER


def test_create_debt_payment(db_session: Session, test_user, test_tenant):
    """Test creating a debt payment."""
    # Create contacts and debt first
    from app.models.contact import Contact
    
    creditor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="John",
        last_name="Creditor",
        email="john@example.com"
    )
    debtor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="Jane",
        last_name="Debtor",
        email="jane@example.com"
    )
    db_session.add_all([creditor_contact, debtor_contact])
    db_session.commit()
    
    debt_data = PersonalDebtCreate(
        creditor_contact_id=creditor_contact.id,
        debtor_contact_id=debtor_contact.id,
        debt_type=DebtType.PERSONAL_LOAN,
        amount=Decimal("1000.00"),
        currency="USD",
        description="Personal loan"
    )
    
    debt = debt_crud.create_personal_debt(
        db=db_session,
        obj_in=debt_data,
        user_id=test_user.id,
        tenant_id=test_tenant.id
    )
    
    # Create payment
    payment_data = DebtPaymentCreate(
        debt_id=debt.id,
        amount=Decimal("500.00"),
        payment_date=date.today(),
        payment_method="bank_transfer",
        notes="First payment"
    )
    
    payment = debt_crud.create_debt_payment(db=db_session, obj_in=payment_data)
    
    assert payment.id is not None
    assert payment.debt_id == debt.id
    assert payment.amount == Decimal("500.00")
    assert payment.payment_method == "bank_transfer"
    assert payment.notes == "First payment"
    
    # Check that debt payment status was updated
    db_session.refresh(debt)
    assert debt.payment_status == PaymentStatus.PARTIAL


def test_full_debt_payment(db_session: Session, test_user, test_tenant):
    """Test that debt status changes to PAID when fully paid."""
    # Create contacts and debt
    from app.models.contact import Contact
    
    creditor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="John",
        last_name="Creditor",
        email="john@example.com"
    )
    debtor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="Jane",
        last_name="Debtor",
        email="jane@example.com"
    )
    db_session.add_all([creditor_contact, debtor_contact])
    db_session.commit()
    
    debt_data = PersonalDebtCreate(
        creditor_contact_id=creditor_contact.id,
        debtor_contact_id=debtor_contact.id,
        debt_type=DebtType.BORROWED_MONEY,
        amount=Decimal("1000.00"),
        currency="USD",
        description="Borrowed money"
    )
    
    debt = debt_crud.create_personal_debt(
        db=db_session,
        obj_in=debt_data,
        user_id=test_user.id,
        tenant_id=test_tenant.id
    )
    
    # Make a full payment
    payment_data = DebtPaymentCreate(
        debt_id=debt.id,
        amount=Decimal("1000.00"),
        payment_date=date.today(),
        payment_method="cash",
        notes="Full payment"
    )
    
    payment = debt_crud.create_debt_payment(db=db_session, obj_in=payment_data)
    
    # Check that debt status changed to PAID
    db_session.refresh(debt)
    assert debt.payment_status == PaymentStatus.PAID
    assert debt.status == DebtStatus.PAID


def test_get_debt_summary(db_session: Session, test_user, test_tenant):
    """Test getting debt summary statistics."""
    # Create contacts
    from app.models.contact import Contact
    
    creditor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="John",
        last_name="Creditor",
        email="john@example.com"
    )
    debtor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="Jane",
        last_name="Debtor",
        email="jane@example.com"
    )
    db_session.add_all([creditor_contact, debtor_contact])
    db_session.commit()
    
    # Create debt where user is creditor (money owed TO user)
    debt_data1 = PersonalDebtCreate(
        creditor_contact_id=creditor_contact.id,  # User's contact
        debtor_contact_id=debtor_contact.id,
        debt_type=DebtType.PERSONAL_LOAN,
        amount=Decimal("1000.00"),
        currency="USD"
    )
    
    debt1 = debt_crud.create_personal_debt(
        db=db_session,
        obj_in=debt_data1,
        user_id=test_user.id,
        tenant_id=test_tenant.id
    )
    
    # Create debt where user is debtor (money user OWES)
    debt_data2 = PersonalDebtCreate(
        creditor_contact_id=debtor_contact.id,
        debtor_contact_id=creditor_contact.id,  # User's contact
        debt_type=DebtType.BORROWED_MONEY,
        amount=Decimal("500.00"),
        currency="USD"
    )
    
    debt2 = debt_crud.create_personal_debt(
        db=db_session,
        obj_in=debt_data2,
        user_id=test_user.id,
        tenant_id=test_tenant.id
    )
    
    # Get summary
    summary = debt_crud.get_debt_summary(db=db_session, user_id=test_user.id, tenant_id=test_tenant.id)
    
    assert summary["total_debts"] == 2
    assert summary["active_debts"] == 2
    # Note: The exact amounts will depend on which contact the user created
    # In a real scenario, we'd need to properly handle the relationship direction


def test_get_overdue_debts(db_session: Session, test_user, test_tenant):
    """Test getting overdue debts."""
    # Create contacts
    from app.models.contact import Contact
    
    creditor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="John",
        last_name="Creditor", 
        email="john@example.com"
    )
    debtor_contact = Contact(
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        first_name="Jane",
        last_name="Debtor",
        email="jane@example.com"
    )
    db_session.add_all([creditor_contact, debtor_contact])
    db_session.commit()
    
    # Create overdue debt
    debt_data = PersonalDebtCreate(
        creditor_contact_id=creditor_contact.id,
        debtor_contact_id=debtor_contact.id,
        debt_type=DebtType.PERSONAL_LOAN,
        amount=Decimal("1000.00"),
        currency="USD",
        due_date=date(2020, 1, 1)  # Past date
    )
    
    debt = debt_crud.create_personal_debt(
        db=db_session,
        obj_in=debt_data,
        user_id=test_user.id,
        tenant_id=test_tenant.id
    )
    
    # Get overdue debts
    overdue_debts = debt_crud.get_overdue_debts(
        db=db_session, 
        user_id=test_user.id, 
        tenant_id=test_tenant.id
    )
    
    assert len(overdue_debts) == 1
    assert overdue_debts[0].id == debt.id
    assert overdue_debts[0].due_date == date(2020, 1, 1)