from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.personal_debt import DebtType, DebtStatus, PaymentStatus, ReminderFrequency


# Personal Debt Schemas
class PersonalDebtBase(BaseModel):
    creditor_contact_id: int = Field(..., description="Contact ID of who owes money")
    debtor_contact_id: int = Field(..., description="Contact ID of who borrowed money")
    debt_type: DebtType
    amount: Decimal = Field(..., gt=0, description="Debt amount must be positive")
    currency: str = Field(default="USD", max_length=3)
    description: Optional[str] = None
    reason: Optional[str] = None
    due_date: Optional[date] = None
    reminder_frequency: ReminderFrequency = ReminderFrequency.NEVER


class PersonalDebtCreate(PersonalDebtBase):
    pass


class PersonalDebtUpdate(BaseModel):
    creditor_contact_id: Optional[int] = None
    debtor_contact_id: Optional[int] = None
    debt_type: Optional[DebtType] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = None
    reason: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[DebtStatus] = None
    payment_status: Optional[PaymentStatus] = None
    reminder_frequency: Optional[ReminderFrequency] = None


class PersonalDebt(PersonalDebtBase):
    id: int
    user_id: int
    tenant_id: int
    created_date: date
    status: DebtStatus
    payment_status: PaymentStatus
    last_reminder_sent: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Debt Payment Schemas
class DebtPaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Payment amount must be positive")
    payment_date: date
    payment_method: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class DebtPaymentCreate(DebtPaymentBase):
    debt_id: int


class DebtPaymentUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class DebtPayment(DebtPaymentBase):
    id: int
    debt_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Extended schemas with related data
class PersonalDebtWithPayments(PersonalDebt):
    payments: List[DebtPayment] = []
    total_paid: Optional[Decimal] = None
    remaining_balance: Optional[Decimal] = None


class PersonalDebtSummary(BaseModel):
    total_debts: int
    total_amount_owed_to_me: Decimal
    total_amount_i_owe: Decimal
    active_debts: int
    overdue_debts: int
    currency: str = "USD"


# Contact reference schemas for debt details
class ContactRef(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class PersonalDebtWithContacts(PersonalDebt):
    creditor: ContactRef
    debtor: ContactRef
    payments: List[DebtPayment] = []
    total_paid: Optional[Decimal] = None
    remaining_balance: Optional[Decimal] = None