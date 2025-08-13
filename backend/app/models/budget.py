from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("transaction_categories.id"))
    subcategory_id = Column(Integer, ForeignKey("transaction_subcategories.id"))
    budget_amount = Column(Numeric(15, 2), nullable=False)
    period = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    alert_percentage = Column(Integer, default=80)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")
    category = relationship("TransactionCategory", back_populates="budgets")
    subcategory = relationship("TransactionSubcategory", back_populates="budgets")


