from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ConfigType(Base):
    """Configuration type/category (e.g., 'expense_categories', 'contact_types')"""
    __tablename__ = "config_types"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String, nullable=False)  # e.g., 'expense_categories'
    display_name = Column(String, nullable=False)  # e.g., 'Expense Categories'
    description = Column(Text)
    
    # Configuration management
    schema_version = Column(String, default="1.0")
    is_active = Column(Boolean, default=True)
    
    # Sync metadata
    last_sync_at = Column(DateTime(timezone=True))
    last_sync_checksum = Column(String)  # File checksum from last sync
    config_file_path = Column(String)  # Relative path to YAML file
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", backref="config_types")
    values = relationship("ConfigValue", back_populates="config_type", cascade="all, delete-orphan")


class ConfigValue(Base):
    """Individual configuration values within a type"""
    __tablename__ = "config_values"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    config_type_id = Column(Integer, ForeignKey("config_types.id"), nullable=False, index=True)
    
    # Value identification
    key = Column(String, nullable=False)  # Unique key within config type
    display_name = Column(String, nullable=False)
    description = Column(Text)
    
    # Hierarchical support
    parent_value_id = Column(Integer, ForeignKey("config_values.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    
    # Value properties
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System values can't be deleted via sync
    config_metadata = Column(JSON)  # Additional properties from YAML
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    config_type = relationship("ConfigType", back_populates="values")
    parent = relationship("ConfigValue", remote_side=[id], backref="children")


class ConfigSyncSession(Base):
    """Tracks sync operations for auditing and rollback"""
    __tablename__ = "config_sync_sessions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Session info
    session_id = Column(String, nullable=False, unique=True)  # UUID for this sync
    status = Column(String, nullable=False)  # 'running', 'completed', 'failed', 'rolled_back'
    sync_type = Column(String, nullable=False)  # 'full', 'incremental', 'file'
    
    # Results
    files_processed = Column(Integer, default=0)
    changes_made = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_details = Column(JSON)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    tenant = relationship("Tenant")
    changes = relationship("ConfigChange", back_populates="sync_session")


class ConfigChange(Base):
    """Individual changes made during sync operations"""
    __tablename__ = "config_changes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sync_session_id = Column(Integer, ForeignKey("config_sync_sessions.id"), nullable=False, index=True)
    
    # Change details
    change_type = Column(String, nullable=False)  # 'create', 'update', 'delete'
    table_name = Column(String, nullable=False)  # 'config_types' or 'config_values'
    record_id = Column(Integer)  # ID of affected record
    
    # Change data
    field_name = Column(String)  # For updates, which field changed
    old_value = Column(JSON)  # Previous value
    new_value = Column(JSON)  # New value
    
    # Context
    config_file_path = Column(String)  # Which file caused this change
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant")
    sync_session = relationship("ConfigSyncSession", back_populates="changes")