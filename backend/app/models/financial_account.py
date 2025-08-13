from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class FinancialAccount(Base):
    __tablename__ = "financial_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50))  # checking, savings, credit_card, investment
    account_number = Column(String(50))
    bank_name = Column(String(100))
    current_balance = Column(Numeric(15, 2), default=0)
    currency = Column(String(3), default='USD')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="financial_accounts")
    tenant = relationship("Tenant")
    transactions = relationship("Transaction", back_populates="account")
    recurring_transactions = relationship("RecurringTransaction", back_populates="account")


