from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class TransactionCategory(Base):
    __tablename__ = "transaction_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null for system categories
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20))  # income, expense, transfer
    color = Column(String(7))
    icon = Column(String(50))
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")
    subcategories = relationship("TransactionSubcategory", back_populates="category")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


# Import after class definition to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.budget import Budget