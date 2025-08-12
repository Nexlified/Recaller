from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class ConfigCategory(Base):
    """Configuration Categories (Top-level grouping)"""
    __tablename__ = "config_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config_types = relationship("ConfigType", back_populates="category", cascade="all, delete-orphan")


class ConfigType(Base):
    """Configuration Types (Second-level grouping)"""
    __tablename__ = "config_types"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("config_categories.id", ondelete="CASCADE"), nullable=False)
    type_key = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    data_type = Column(String(20), default="enum")  # 'enum', 'hierarchical', 'key_value'
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Configuration Metadata
    source_file = Column(String(255))
    last_sync_at = Column(DateTime(timezone=True))
    sync_version = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("ConfigCategory", back_populates="config_types")
    config_values = relationship("ConfigValue", back_populates="config_type", cascade="all, delete-orphan")
    sync_history = relationship("ConfigSyncHistory", back_populates="config_type", cascade="all, delete-orphan")


class ConfigValue(Base):
    """Configuration Values (Actual data)"""
    __tablename__ = "config_values"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)  # NULL for global configs
    config_type_id = Column(Integer, ForeignKey("config_types.id", ondelete="CASCADE"), nullable=False)
    
    # Value Information
    value_key = Column(String(100), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Hierarchical Support
    parent_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=True, index=True)
    hierarchy_path = Column(String(500), index=True)  # For nested categories like industries
    level = Column(Integer, default=1)
    
    # Additional Metadata
    extra_metadata = Column(JSONB)  # Extra properties like icons, colors, etc.
    tags = Column(ARRAY(Text))  # For flexible categorization
    
    # Lifecycle
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System values can't be deleted
    
    # Sync Information
    source_file = Column(String(255))
    sync_version = Column(String(50))
    last_sync_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config_type = relationship("ConfigType", back_populates="config_values")
    parent_value = relationship("ConfigValue", remote_side=[id], backref="child_values")
    translations = relationship("ConfigValueTranslation", back_populates="config_value", cascade="all, delete-orphan")


class ConfigValueTranslation(Base):
    """Configuration Value Translations (i18n support)"""
    __tablename__ = "config_value_translations"

    id = Column(Integer, primary_key=True, index=True)
    config_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False, index=True)  # 'en', 'es', 'fr', etc.
    
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config_value = relationship("ConfigValue", back_populates="translations")


class ConfigSyncHistory(Base):
    """Configuration Sync History"""
    __tablename__ = "config_sync_history"

    id = Column(Integer, primary_key=True, index=True)
    sync_session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    config_type_id = Column(Integer, ForeignKey("config_types.id", ondelete="CASCADE"), nullable=True)
    
    # Sync Information
    source_file = Column(String(255), nullable=False)
    sync_action = Column(String(20), nullable=False)  # 'create', 'update', 'delete', 'validate'
    sync_status = Column(String(20), nullable=False)  # 'success', 'failed', 'warning'
    
    # Change Details
    changes_summary = Column(JSONB)  # Summary of what changed
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)
    
    # Error Handling
    errors = Column(JSONB)  # Any errors encountered
    warnings = Column(JSONB)  # Non-blocking warnings
    
    # Version Information
    source_version = Column(String(50))
    target_version = Column(String(50))
    
    # Metadata
    triggered_by = Column(String(50))  # 'command', 'api', 'schedule'
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    duration_ms = Column(Integer)
    
    # Relationships
    config_type = relationship("ConfigType", back_populates="sync_history")