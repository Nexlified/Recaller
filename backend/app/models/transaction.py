from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    type = Column(String(10), nullable=False)  # credit, debit
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    description = Column(Text)
    transaction_date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey("transaction_categories.id"))
    subcategory_id = Column(Integer, ForeignKey("transaction_subcategories.id"))
    account_id = Column(Integer, ForeignKey("financial_accounts.id"))
    reference_number = Column(String(100))
    is_recurring = Column(Boolean, default=False)
    recurring_template_id = Column(Integer, ForeignKey("recurring_transactions.id"))
    attachments = Column(JSON().with_variant(JSONB, "postgresql"))
    extra_data = Column(JSON().with_variant(JSONB, "postgresql"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")
    category = relationship("TransactionCategory", back_populates="transactions")
    subcategory = relationship("TransactionSubcategory", back_populates="transactions")
    account = relationship("FinancialAccount", back_populates="transactions")
    recurring_template = relationship("RecurringTransaction", back_populates="transactions")


