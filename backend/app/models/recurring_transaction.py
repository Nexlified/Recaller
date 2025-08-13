from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    template_name = Column(String(200), nullable=False)
    type = Column(String(10), nullable=False)  # credit, debit
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("transaction_categories.id"))
    subcategory_id = Column(Integer, ForeignKey("transaction_subcategories.id"))
    account_id = Column(Integer, ForeignKey("financial_accounts.id"))
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    interval_count = Column(Integer, default=1)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_due_date = Column(Date)
    reminder_days = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSON().with_variant(JSONB, "postgresql"))  # EMI details, loan info, etc.
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")
    category = relationship("TransactionCategory")
    subcategory = relationship("TransactionSubcategory")
    account = relationship("FinancialAccount", back_populates="recurring_transactions")
    transactions = relationship("Transaction", back_populates="recurring_template")


