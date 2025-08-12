from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class ConfigCategory(Base):
    __tablename__ = "config_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to config types
    config_types = relationship("ConfigType", back_populates="category")


class ConfigType(Base):
    __tablename__ = "config_types"

    id = Column(Integer, primary_key=True, index=True)
    type_key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    data_type = Column(String, nullable=False)  # 'enum', 'hierarchical', 'key_value'
    max_level = Column(Integer, default=1)
    allows_custom_values = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("config_categories.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("ConfigCategory", back_populates="config_types")
    values = relationship("ConfigValue", back_populates="config_type")


class ConfigValue(Base):
    __tablename__ = "config_values"

    id = Column(Integer, primary_key=True, index=True)
    config_type_id = Column(Integer, ForeignKey("config_types.id"), nullable=False)
    value_key = Column(String, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    level = Column(Integer, default=1)
    parent_value_id = Column(Integer, ForeignKey("config_values.id"))
    extra_data = Column(JSON)  # Store additional metadata like icons, colors, etc.
    tags = Column(JSON)  # Store tags as JSON array
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System values cannot be deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    config_type = relationship("ConfigType", back_populates="values")
    parent = relationship("ConfigValue", remote_side=[id], backref="children")

    # Unique constraint on config_type_id and value_key
    __table_args__ = (
        {"sqlite_autoincrement": True}
    )