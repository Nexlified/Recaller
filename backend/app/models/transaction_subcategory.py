from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class TransactionSubcategory(Base):
    __tablename__ = "transaction_subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("transaction_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    budget_limit = Column(Numeric(15, 2))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    category = relationship("TransactionCategory", back_populates="subcategories")
    transactions = relationship("Transaction", back_populates="subcategory")
    budgets = relationship("Budget", back_populates="subcategory")


