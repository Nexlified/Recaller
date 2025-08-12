from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class ConfigurationCategory(Base):
    """Configuration categories (e.g., core, professional)"""
    __tablename__ = "configuration_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    types = relationship("ConfigurationType", back_populates="category")


class ConfigurationType(Base):
    """Configuration types within categories (e.g., genders, countries)"""
    __tablename__ = "configuration_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("configuration_categories.id"), nullable=False)
    tenant_scope = Column(String, default="global")  # global, tenant, or user
    version = Column(String, default="1.0.0")
    checksum = Column(String)  # For tracking file changes
    file_path = Column(String)  # Path to YAML file
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True))

    # Relationships
    category = relationship("ConfigurationCategory", back_populates="types")
    values = relationship("ConfigurationValue", back_populates="config_type")


class ConfigurationValue(Base):
    """Individual configuration values within types"""
    __tablename__ = "configuration_values"

    id = Column(Integer, primary_key=True, index=True)
    config_type_id = Column(Integer, ForeignKey("configuration_types.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # NULL for global values
    
    # Value fields
    key = Column(String, nullable=False)  # Unique identifier within type
    name = Column(String, nullable=False)
    display_name = Column(String)
    description = Column(Text)
    code = Column(String)  # Additional code field (e.g., ISO codes)
    iso_code = Column(String)  # ISO codes for countries, etc.
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    config_type = relationship("ConfigurationType", back_populates="values")
    tenant = relationship("Tenant")


class ConfigurationSyncLog(Base):
    """Log of configuration sync operations"""
    __tablename__ = "configuration_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    config_type_id = Column(Integer, ForeignKey("configuration_types.id"), nullable=True)
    operation = Column(String, nullable=False)  # sync, validate, backup, restore
    status = Column(String, nullable=False)  # success, error, warning
    message = Column(Text)
    file_path = Column(String)
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    config_type = relationship("ConfigurationType")