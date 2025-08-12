"""Configuration Management Models

This module contains all SQLAlchemy models for the configuration management system,
including categories, types, values, translations, dependencies, sync history, and usage statistics.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class ConfigCategory(Base):
    """Configuration Categories - Top-level grouping like 'core', 'professional', 'social', 'contact'"""
    __tablename__ = "config_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadata
    icon = Column(String(50))
    color = Column(String(7))  # Hex color code
    config_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config_types = relationship("ConfigType", back_populates="category", cascade="all, delete-orphan")


class ConfigType(Base):
    """Configuration Types - Second-level grouping like 'genders', 'industries', 'activities'"""
    __tablename__ = "config_types"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("config_categories.id", ondelete="CASCADE"), nullable=False)
    type_key = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Data Structure
    data_type = Column(String(20), default="enum")  # 'enum', 'hierarchical', 'key_value'
    max_level = Column(Integer, default=1)  # Maximum hierarchy depth
    allows_custom_values = Column(Boolean, default=False)
    
    # Display Configuration
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    is_system = Column(Boolean, default=False)
    
    # Configuration Metadata
    source_file = Column(String(255))  # Path to YAML file
    last_sync_at = Column(DateTime(timezone=True))
    sync_version = Column(String(50))
    
    # UI Configuration
    icon = Column(String(50))
    color = Column(String(7))
    config_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("ConfigCategory", back_populates="config_types")
    config_values = relationship("ConfigValue", back_populates="config_type", cascade="all, delete-orphan")
    sync_history = relationship("ConfigSyncHistory", back_populates="config_type")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('category_id', 'type_key', name='uq_config_types_category_key'),
        Index('idx_config_types_data_type', 'data_type'),
    )


class ConfigValue(Base):
    """Configuration Values - Actual data like 'male', 'technology', 'coffee_meeting'"""
    __tablename__ = "config_values"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)  # NULL for global configs
    config_type_id = Column(Integer, ForeignKey("config_types.id", ondelete="CASCADE"), nullable=False)
    
    # Value Information
    value_key = Column(String(100), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Hierarchical Support
    parent_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=True)
    hierarchy_path = Column(String(500), index=True)  # For nested categories like 'technology.software.saas'
    level = Column(Integer, default=1, index=True)
    has_children = Column(Boolean, default=False)
    children_count = Column(Integer, default=0)
    
    # Additional Metadata
    value_metadata = Column(JSON)  # Extra properties like icons, colors, aliases, etc.
    tags = Column(ARRAY(String), index=True)  # For flexible categorization
    custom_properties = Column(JSON)  # Tenant-specific custom properties
    
    # Lifecycle
    sort_order = Column(Integer, default=0, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_system = Column(Boolean, default=False)  # System values can't be deleted
    is_custom = Column(Boolean, default=False, index=True)  # User-created values
    
    # Sync Information
    source_file = Column(String(255))
    sync_version = Column(String(50))
    last_sync_at = Column(DateTime(timezone=True))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    config_type = relationship("ConfigType", back_populates="config_values")
    tenant = relationship("Tenant")
    parent = relationship("ConfigValue", remote_side=[id], backref="children")
    translations = relationship("ConfigValueTranslation", back_populates="config_value", cascade="all, delete-orphan")
    usage_stats = relationship("ConfigUsageStats", back_populates="config_value", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    # Dependency relationships
    source_dependencies = relationship("ConfigValueDependency", 
                                     foreign_keys="ConfigValueDependency.source_value_id",
                                     back_populates="source_value")
    target_dependencies = relationship("ConfigValueDependency", 
                                     foreign_keys="ConfigValueDependency.target_value_id",
                                     back_populates="target_value")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('config_type_id', 'value_key', 'tenant_id', name='uq_config_values_type_key_tenant'),
        Index('idx_config_values_value_metadata', 'value_metadata', postgresql_using='gin'),
        Index('idx_config_values_custom_props', 'custom_properties', postgresql_using='gin'),
        Index('idx_config_values_hierarchy_path', 'hierarchy_path'),
    )


class ConfigValueTranslation(Base):
    """Configuration Value Translations - i18n support for multiple languages"""
    __tablename__ = "config_value_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    config_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False, index=True)  # 'en', 'es', 'fr', etc.
    
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Translation metadata
    translated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    translation_quality = Column(String(20), default="manual", index=True)  # 'manual', 'auto', 'reviewed'
    last_reviewed_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config_value = relationship("ConfigValue", back_populates="translations")
    translator = relationship("User", foreign_keys=[translated_by])
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('config_value_id', 'language_code', name='uq_config_translations_value_lang'),
    )


class ConfigValueDependency(Base):
    """Configuration Value Dependencies - Relationships between config values"""
    __tablename__ = "config_value_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    source_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=False)
    target_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), nullable=False, index=True)  # 'requires', 'excludes', 'implies', 'related'
    
    description = Column(Text)
    dependency_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source_value = relationship("ConfigValue", foreign_keys=[source_value_id], back_populates="source_dependencies")
    target_value = relationship("ConfigValue", foreign_keys=[target_value_id], back_populates="target_dependencies")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('source_value_id', 'target_value_id', 'dependency_type', 
                        name='uq_config_dependencies_source_target_type'),
    )


class ConfigSyncHistory(Base):
    """Configuration Sync History - Track YAML sync operations"""
    __tablename__ = "config_sync_history"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_session_id = Column(UUID(as_uuid=True), server_default=func.gen_random_uuid(), index=True)
    config_type_id = Column(Integer, ForeignKey("config_types.id", ondelete="CASCADE"), nullable=True)
    
    # Sync Information
    source_file = Column(String(255), nullable=False, index=True)
    sync_action = Column(String(20), nullable=False, index=True)  # 'create', 'update', 'delete', 'validate'
    sync_status = Column(String(20), nullable=False, index=True)  # 'success', 'failed', 'warning'
    
    # Change Details
    changes_summary = Column(JSON)  # Summary of what changed
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    
    # Error Handling
    errors = Column(JSON)  # Any errors encountered
    warnings = Column(JSON)  # Non-blocking warnings
    
    # Version Information
    source_version = Column(String(50))
    target_version = Column(String(50))
    checksum = Column(String(64))  # File checksum for change detection
    
    # Performance Metrics
    duration_ms = Column(Integer)
    memory_usage_mb = Column(Integer)
    
    # Metadata
    triggered_by = Column(String(50))  # 'command', 'api', 'schedule', 'user'
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    execution_context = Column(JSON)  # Environment, server info, etc.
    
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    config_type = relationship("ConfigType", back_populates="sync_history")
    triggered_by_user = relationship("User")
    change_log = relationship("ConfigChangeLog", back_populates="sync_history", cascade="all, delete-orphan")


class ConfigChangeLog(Base):
    """Configuration Change Log - Detailed change tracking"""
    __tablename__ = "config_change_log"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_history_id = Column(Integer, ForeignKey("config_sync_history.id", ondelete="CASCADE"), nullable=False)
    config_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="SET NULL"), nullable=True)
    
    # Change Details
    action = Column(String(20), nullable=False, index=True)  # 'create', 'update', 'delete', 'restore'
    field_name = Column(String(100))  # Specific field that changed
    old_value = Column(Text)
    new_value = Column(Text)
    
    # Context
    value_key = Column(String(100))
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    change_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    sync_history = relationship("ConfigSyncHistory", back_populates="change_log")
    config_value = relationship("ConfigValue")
    tenant = relationship("Tenant")


class ConfigUsageStats(Base):
    """Configuration Usage Statistics - Usage metrics and analytics"""
    __tablename__ = "config_usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    config_value_id = Column(Integer, ForeignKey("config_values.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    
    # Usage Metrics
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), index=True)
    first_used_at = Column(DateTime(timezone=True))
    
    # Context Usage
    context_type = Column(String(50), index=True)  # 'contact', 'organization', 'event', etc.
    context_count = Column(Integer, default=0)
    
    # Period tracking
    daily_usage = Column(Integer, default=0)
    weekly_usage = Column(Integer, default=0)
    monthly_usage = Column(Integer, default=0)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config_value = relationship("ConfigValue", back_populates="usage_stats")
    tenant = relationship("Tenant")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('config_value_id', 'tenant_id', 'context_type', 
                        name='uq_usage_stats_value_tenant_context'),
    )