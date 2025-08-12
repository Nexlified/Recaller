from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ConfigurationCategory(Base):
    __tablename__ = "configuration_categories"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Multi-tenant support
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant")
    
    # Relationships
    types = relationship("ConfigurationType", back_populates="category", cascade="all, delete-orphan")


class ConfigurationType(Base):
    __tablename__ = "configuration_types"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("configuration_categories.id"), nullable=False, index=True)
    data_type = Column(String, default="string")  # string, number, boolean, json
    validation_rules = Column(JSON, nullable=True)  # JSON schema for validation
    default_value = Column(Text, nullable=True)
    is_hierarchical = Column(Boolean, default=False)
    is_translatable = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Multi-tenant support
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant")
    
    # Relationships
    category = relationship("ConfigurationCategory", back_populates="types")
    values = relationship("ConfigurationValue", back_populates="type", cascade="all, delete-orphan")


class ConfigurationValue(Base):
    __tablename__ = "configuration_values"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("configuration_types.id"), nullable=False, index=True)
    key = Column(String, nullable=False, index=True)
    value = Column(Text, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchical support
    parent_id = Column(Integer, ForeignKey("configuration_values.id"), nullable=True, index=True)
    level = Column(Integer, default=0)
    path = Column(String, nullable=True, index=True)  # Materialized path for efficient queries
    
    # Metadata
    value_metadata = Column(JSON, nullable=True)  # Additional metadata as JSON
    tags = Column(JSON, nullable=True)  # Array of tags as JSON
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Multi-tenant support
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant")
    
    # Relationships
    type = relationship("ConfigurationType", back_populates="values")
    parent = relationship("ConfigurationValue", remote_side=[id], backref="children")
    translations = relationship("ConfigurationTranslation", back_populates="value", cascade="all, delete-orphan")


class ConfigurationTranslation(Base):
    __tablename__ = "configuration_translations"

    id = Column(Integer, primary_key=True, index=True)
    value_id = Column(Integer, ForeignKey("configuration_values.id"), nullable=False, index=True)
    language_code = Column(String(5), nullable=False, index=True)  # e.g., 'en', 'es', 'fr'
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Multi-tenant support
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant")
    
    # Relationships
    value = relationship("ConfigurationValue", back_populates="translations")
    
    # Unique constraint for value_id + language_code per tenant
    __table_args__ = (
        {'schema': None}  # This will be added by SQLAlchemy automatically
    )