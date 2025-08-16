from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class GiftStatus(enum.Enum):
    IDEA = "idea"
    PLANNED = "planned"
    PURCHASED = "purchased"
    WRAPPED = "wrapped"
    GIVEN = "given"
    RETURNED = "returned"


class GiftPriority(enum.IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class Gift(Base):
    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=True, index=True)  # Electronics, Clothing, etc.
    
    # Recipient Information
    recipient_contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    recipient_name = Column(String(255), nullable=True)  # In case recipient is not a contact
    
    # Occasion and Timing
    occasion = Column(String(100), nullable=True, index=True)  # Birthday, Christmas, Anniversary, etc.
    occasion_date = Column(Date, nullable=True, index=True)
    
    # Financial Information
    budget_amount = Column(Numeric(10, 2), nullable=True)
    actual_amount = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    
    # Status and Priority
    status = Column(String(20), nullable=False, default=GiftStatus.IDEA.value, index=True)
    priority = Column(Integer, nullable=False, default=GiftPriority.MEDIUM.value, index=True)
    
    # Purchase Information
    store_name = Column(String(255), nullable=True)
    purchase_url = Column(Text, nullable=True)
    purchase_date = Column(Date, nullable=True)
    
    # Gift Details (JSON format for flexibility)
    # Example: {"size": "M", "color": "blue", "brand": "Nike", "model": "Air Max"}
    gift_details = Column(JSON, nullable=False, default=dict)
    
    # Tracking Information
    tracking_number = Column(String(255), nullable=True)
    delivery_date = Column(Date, nullable=True)
    
    # Notes and References
    notes = Column(Text)
    image_url = Column(Text, nullable=True)
    
    # Reminders and Notifications (JSON format)
    # Example: {"purchase_reminder": "2024-12-15", "wrap_reminder": "2024-12-20"}
    reminder_dates = Column(JSON, nullable=False, default=dict)
    
    # Integration References
    task_id = Column(Integer, nullable=True)  # Reference to shopping task
    transaction_id = Column(Integer, nullable=True)  # Reference to financial transaction
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_surprise = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="gifts")
    user = relationship(lambda: User, back_populates="gifts")
    recipient_contact = relationship(lambda: Contact, back_populates="gifts_received")


class GiftIdea(Base):
    __tablename__ = "gift_ideas"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=True, index=True)
    
    # Target Information
    target_contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    target_demographic = Column(String(100), nullable=True)  # "teenage girl", "elderly man", etc.
    
    # Occasion Context
    suitable_occasions = Column(JSON, nullable=False, default=list)  # ["birthday", "graduation"]
    
    # Financial Information
    price_range_min = Column(Numeric(10, 2), nullable=True)
    price_range_max = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    
    # Idea Details (JSON format for flexibility)
    # Example: {"style": "modern", "interests": ["technology", "gaming"], "preferences": {"color": "blue"}}
    idea_details = Column(JSON, nullable=False, default=dict)
    
    # Sources and References
    source_url = Column(Text, nullable=True)
    source_description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    
    # Rating and Feedback
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    notes = Column(Text)
    
    # Tracking
    times_gifted = Column(Integer, nullable=False, default=0)  # How many times this idea was used
    last_gifted_date = Column(Date, nullable=True)
    
    # Tags for searchability (JSON format)
    tags = Column(JSON, nullable=False, default=list)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_favorite = Column(Boolean, nullable=False, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - using lambda to defer resolution
    tenant = relationship(lambda: Tenant, back_populates="gift_ideas")
    user = relationship(lambda: User, back_populates="gift_ideas")
    target_contact = relationship(lambda: Contact, back_populates="gift_ideas_for_them")


# Import after class definitions to avoid circular imports
from app.models.tenant import Tenant
from app.models.user import User
from app.models.contact import Contact