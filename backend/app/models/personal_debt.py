from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base


class DebtType(str, enum.Enum):
    PERSONAL_LOAN = "personal_loan"
    BORROWED_MONEY = "borrowed_money"
    SHARED_EXPENSE = "shared_expense"
    FAVOR_OWED = "favor_owed"


class DebtStatus(str, enum.Enum):
    ACTIVE = "active"
    PAID = "paid"
    FORGIVEN = "forgiven"
    DISPUTED = "disputed"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class ReminderFrequency(str, enum.Enum):
    NEVER = "never"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PersonalDebt(Base):
    __tablename__ = "personal_debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Contact references
    creditor_contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)  # who owes money
    debtor_contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)   # who borrowed money
    
    # Debt details
    debt_type = Column(Enum(DebtType), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    description = Column(Text)
    reason = Column(Text)
    
    # Dates
    created_date = Column(Date, nullable=False, server_default=func.current_date())
    due_date = Column(Date, index=True)
    
    # Status tracking
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.ACTIVE, index=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.UNPAID, index=True)
    
    # Reminders
    reminder_frequency = Column(Enum(ReminderFrequency), nullable=False, default=ReminderFrequency.NEVER)
    last_reminder_sent = Column(DateTime(timezone=True))
    
    # Standard audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")
    creditor = relationship("Contact", foreign_keys=[creditor_contact_id])
    debtor = relationship("Contact", foreign_keys=[debtor_contact_id])
    payments = relationship("DebtPayment", back_populates="debt", cascade="all, delete-orphan")


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(Integer, ForeignKey("personal_debts.id"), nullable=False, index=True)
    
    # Payment details
    amount = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50))  # cash, bank_transfer, check, credit_card, etc.
    notes = Column(Text)
    
    # Standard audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    debt = relationship("PersonalDebt", back_populates="payments")


# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.contact import Contact