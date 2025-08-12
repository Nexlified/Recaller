from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(100))
    organization_type = Column(String(50), nullable=False, index=True)  # 'school', 'company', 'nonprofit', etc.
    industry = Column(String(100), index=True)  # 'technology', 'education', 'healthcare', etc.
    size_category = Column(String(20))  # 'startup', 'small', 'medium', 'large', 'enterprise'
    
    # Contact Information
    website = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    
    # Address
    address_street = Column(Text)
    address_city = Column(String(100))
    address_state = Column(String(100))
    address_postal_code = Column(String(20))
    address_country_code = Column(String(2))
    
    # Metadata
    founded_year = Column(Integer)
    description = Column(Text)
    logo_url = Column(String(500))
    employee_count = Column(Integer)
    annual_revenue = Column(BigInteger)  # For companies
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For data quality
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="organizations")
    current_employees = relationship("Contact", foreign_keys="Contact.current_organization_id", back_populates="current_organization")
    alumni = relationship("Contact", foreign_keys="Contact.alma_mater_id", back_populates="alma_mater")
    created_by = relationship("User")
    aliases = relationship("OrganizationAlias", back_populates="organization", cascade="all, delete-orphan")
    locations = relationship("OrganizationLocation", back_populates="organization", cascade="all, delete-orphan")


class OrganizationAlias(Base):
    __tablename__ = "organization_aliases"

    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False)
    alias_name = Column(String(255), nullable=False, index=True)
    alias_type = Column(String(50))  # 'former_name', 'abbreviation', 'common_name', 'legal_name'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="aliases")


class OrganizationLocation(Base):
    __tablename__ = "organization_locations"

    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False)
    
    location_name = Column(String(255))  # 'Headquarters', 'New York Office', 'Campus'
    location_type = Column(String(50))  # 'headquarters', 'branch', 'campus', 'remote'
    
    address_street = Column(Text)
    address_city = Column(String(100))
    address_state = Column(String(100))
    address_postal_code = Column(String(20))
    address_country_code = Column(String(2))
    
    phone = Column(String(50))
    email = Column(String(255))
    
    employee_count = Column(Integer)
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="locations")
