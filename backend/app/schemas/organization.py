from typing import Optional, List
from pydantic import BaseModel, validator, Field
from datetime import datetime


class OrganizationLocationBase(BaseModel):
    """Base model for organization locations."""
    location_name: Optional[str] = Field(
        None,
        description="Name of the location (e.g., 'Headquarters', 'Branch Office')",
        example="San Francisco Office",
        max_length=100
    )
    location_type: Optional[str] = Field(
        None,
        description="Type of location (headquarters, branch, warehouse, etc.)",
        example="headquarters"
    )
    address_street: Optional[str] = Field(
        None,
        description="Street address",
        example="123 Market Street, Suite 456",
        max_length=200
    )
    address_city: Optional[str] = Field(
        None,
        description="City name",
        example="San Francisco",
        max_length=100
    )
    address_state: Optional[str] = Field(
        None,
        description="State or province",
        example="California",
        max_length=100
    )
    address_postal_code: Optional[str] = Field(
        None,
        description="Postal or ZIP code",
        example="94105",
        max_length=20
    )
    address_country_code: Optional[str] = Field(
        None,
        description="Two-letter country code (ISO 3166-1 alpha-2)",
        example="US",
        max_length=2
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number for this location",
        example="+1-415-555-0123",
        max_length=50
    )
    email: Optional[str] = Field(
        None,
        description="Email address for this location",
        example="sf-office@company.com",
        max_length=254
    )
    employee_count: Optional[int] = Field(
        None,
        description="Number of employees at this location",
        example=150,
        ge=0
    )
    is_primary: Optional[bool] = Field(
        default=False,
        description="Whether this is the primary/main location",
        example=True
    )


class OrganizationLocationCreate(OrganizationLocationBase):
    """Model for creating a new organization location."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "location_name": "San Francisco Office",
                "location_type": "headquarters",
                "address_street": "123 Market Street, Suite 456",
                "address_city": "San Francisco",
                "address_state": "California",
                "address_postal_code": "94105",
                "address_country_code": "US",
                "phone": "+1-415-555-0123",
                "email": "sf-office@company.com",
                "employee_count": 150,
                "is_primary": True
            }
        }


class OrganizationLocationUpdate(OrganizationLocationBase):
    """Model for updating an organization location."""
    pass


class OrganizationLocation(OrganizationLocationBase):
    """Organization location with database fields."""
    id: int = Field(..., description="Unique location identifier", example=123)
    organization_id: int = Field(..., description="ID of the parent organization", example=456)
    created_at: datetime = Field(..., description="Location creation timestamp", example="2023-01-15T10:30:00Z")

    class Config:
        from_attributes = True


class OrganizationAliasBase(BaseModel):
    """Base model for organization aliases/alternate names."""
    alias_name: str = Field(
        ...,
        description="Alternative name for the organization",
        example="Tech Corp",
        max_length=200
    )
    alias_type: Optional[str] = Field(
        None,
        description="Type of alias (abbreviation, dba, former_name, etc.)",
        example="abbreviation"
    )


class OrganizationAliasCreate(OrganizationAliasBase):
    """Model for creating organization aliases."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "alias_name": "Tech Corp",
                "alias_type": "abbreviation"
            }
        }


class OrganizationAlias(OrganizationAliasBase):
    """Organization alias with database fields."""
    id: int = Field(..., description="Unique alias identifier", example=789)
    organization_id: int = Field(..., description="ID of the parent organization", example=456)
    created_at: datetime = Field(..., description="Alias creation timestamp", example="2023-01-15T10:30:00Z")

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    """Base organization model with core fields."""
    name: str = Field(
        ...,
        description="Official name of the organization",
        example="Technology Corporation Inc.",
        max_length=200
    )
    short_name: Optional[str] = Field(
        None,
        description="Commonly used short name or abbreviation",
        example="TechCorp",
        max_length=100
    )
    organization_type: str = Field(
        ...,
        description="Type of organization",
        example="company"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector",
        example="Technology",
        max_length=100
    )
    size_category: Optional[str] = Field(
        None,
        description="Organization size category",
        example="large"
    )
    website: Optional[str] = Field(
        None,
        description="Primary website URL",
        example="https://www.techcorp.com",
        max_length=500
    )
    email: Optional[str] = Field(
        None,
        description="General contact email",
        example="info@techcorp.com",
        max_length=254
    )
    phone: Optional[str] = Field(
        None,
        description="Primary phone number",
        example="+1-800-555-0123",
        max_length=50
    )
    linkedin_url: Optional[str] = Field(
        None,
        description="LinkedIn company page URL",
        example="https://www.linkedin.com/company/techcorp",
        max_length=500
    )
    address_street: Optional[str] = Field(
        None,
        description="Primary address street",
        example="456 Innovation Drive",
        max_length=200
    )
    address_city: Optional[str] = Field(
        None,
        description="Primary address city",
        example="Palo Alto",
        max_length=100
    )
    address_state: Optional[str] = Field(
        None,
        description="Primary address state/province",
        example="California",
        max_length=100
    )
    address_postal_code: Optional[str] = Field(
        None,
        description="Primary address postal code",
        example="94301",
        max_length=20
    )
    address_country_code: Optional[str] = Field(
        None,
        description="Primary address country code (ISO 3166-1 alpha-2)",
        example="US",
        max_length=2
    )
    founded_year: Optional[int] = Field(
        None,
        description="Year the organization was founded",
        example=2010,
        ge=1800,
        le=2030
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the organization",
        example="A leading technology company specializing in innovative software solutions.",
        max_length=2000
    )
    logo_url: Optional[str] = Field(
        None,
        description="URL to the organization's logo image",
        example="https://cdn.techcorp.com/logo.png",
        max_length=500
    )
    employee_count: Optional[int] = Field(
        None,
        description="Total number of employees",
        example=5000,
        ge=0
    )
    annual_revenue: Optional[int] = Field(
        None,
        description="Annual revenue in USD",
        example=50000000,
        ge=0
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="Whether the organization is currently active",
        example=True
    )
    is_verified: Optional[bool] = Field(
        default=False,
        description="Whether the organization information has been verified",
        example=False
    )

    @validator('organization_type')
    def validate_organization_type(cls, v):
        """Validate organization type against allowed values."""
        valid_types = ['school', 'company', 'nonprofit', 'government', 'healthcare', 'religious']
        if v not in valid_types:
            raise ValueError(f'organization_type must be one of: {", ".join(valid_types)}')
        return v

    @validator('size_category')
    def validate_size_category(cls, v):
        """Validate size category against allowed values."""
        if v is None:
            return v
        valid_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
        if v not in valid_sizes:
            raise ValueError(f'size_category must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('address_country_code')
    def validate_country_code(cls, v):
        """Validate country code format."""
        if v is not None and len(v) != 2:
            raise ValueError('address_country_code must be 2 characters')
        return v.upper() if v else v


class OrganizationCreate(OrganizationBase):
    """Model for creating new organizations."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Technology Corporation Inc.",
                "short_name": "TechCorp",
                "organization_type": "company",
                "industry": "Technology",
                "size_category": "large",
                "website": "https://www.techcorp.com",
                "email": "info@techcorp.com",
                "phone": "+1-800-555-0123",
                "linkedin_url": "https://www.linkedin.com/company/techcorp",
                "address_street": "456 Innovation Drive",
                "address_city": "Palo Alto",
                "address_state": "California",
                "address_postal_code": "94301",
                "address_country_code": "US",
                "founded_year": 2010,
                "description": "A leading technology company specializing in innovative software solutions.",
                "employee_count": 5000,
                "annual_revenue": 50000000,
                "is_active": True
            }
        }


class OrganizationUpdate(BaseModel):
    """Model for updating organizations with optional fields."""
    name: Optional[str] = Field(None, max_length=200)
    short_name: Optional[str] = Field(None, max_length=100)
    organization_type: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    size_category: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=254)
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    address_street: Optional[str] = Field(None, max_length=200)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=100)
    address_postal_code: Optional[str] = Field(None, max_length=20)
    address_country_code: Optional[str] = Field(None, max_length=2)
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = Field(None, max_length=500)
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @validator('organization_type')
    def validate_organization_type(cls, v):
        if v is None:
            return v
        valid_types = ['school', 'company', 'nonprofit', 'government', 'healthcare', 'religious']
        if v not in valid_types:
            raise ValueError(f'organization_type must be one of: {", ".join(valid_types)}')
        return v

    @validator('size_category')
    def validate_size_category(cls, v):
        if v is None:
            return v
        valid_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
        if v not in valid_sizes:
            raise ValueError(f'size_category must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('address_country_code')
    def validate_country_code(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('address_country_code must be 2 characters')
        return v.upper() if v else v


class OrganizationInDBBase(OrganizationBase):
    """Base organization model with database fields."""
    id: int = Field(..., description="Unique organization identifier", example=456)
    tenant_id: int = Field(..., description="Tenant ID for multi-tenancy", example=1)
    created_by_user_id: int = Field(..., description="ID of user who created this organization", example=123)
    created_at: datetime = Field(..., description="Creation timestamp", example="2023-01-15T10:30:00Z")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp", example="2023-01-20T14:45:00Z")

    class Config:
        from_attributes = True


class Organization(OrganizationInDBBase):
    """
    Complete organization model with relationships.
    
    Includes all organization details plus related aliases and locations.
    Used for detailed organization views.
    """
    aliases: List[OrganizationAlias] = Field(
        default=[],
        description="List of alternative names/aliases for this organization"
    )
    locations: List[OrganizationLocation] = Field(
        default=[],
        description="List of physical locations for this organization"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 456,
                "name": "Technology Corporation Inc.",
                "short_name": "TechCorp",
                "organization_type": "company",
                "industry": "Technology",
                "size_category": "large",
                "website": "https://www.techcorp.com",
                "email": "info@techcorp.com",
                "phone": "+1-800-555-0123",
                "address_city": "Palo Alto",
                "address_state": "California",
                "address_country_code": "US",
                "founded_year": 2010,
                "employee_count": 5000,
                "is_active": True,
                "is_verified": True,
                "tenant_id": 1,
                "created_by_user_id": 123,
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-20T14:45:00Z",
                "aliases": [
                    {
                        "id": 789,
                        "alias_name": "TechCorp",
                        "alias_type": "abbreviation",
                        "organization_id": 456,
                        "created_at": "2023-01-15T10:30:00Z"
                    }
                ],
                "locations": [
                    {
                        "id": 123,
                        "location_name": "Headquarters",
                        "location_type": "headquarters",
                        "address_street": "456 Innovation Drive",
                        "address_city": "Palo Alto",
                        "address_state": "California",
                        "address_postal_code": "94301",
                        "address_country_code": "US",
                        "phone": "+1-650-555-0123",
                        "email": "hq@techcorp.com",
                        "employee_count": 3000,
                        "is_primary": True,
                        "organization_id": 456,
                        "created_at": "2023-01-15T10:30:00Z"
                    }
                ]
            }
        }


class OrganizationSimple(OrganizationInDBBase):
    """
    Simplified organization response without relationships.
    
    Used for efficient listing and search results where
    full relationship data is not needed.
    """
    pass


class OrganizationSearchResult(BaseModel):
    """
    Organization search result model.
    
    Optimized for search and listing operations with key fields
    and contact statistics for efficient browsing.
    """
    id: int = Field(..., description="Unique organization identifier", example=456)
    name: str = Field(..., description="Organization name", example="Technology Corporation Inc.")
    short_name: Optional[str] = Field(None, description="Short/common name", example="TechCorp")
    organization_type: str = Field(..., description="Organization type", example="company")
    industry: Optional[str] = Field(None, description="Industry sector", example="Technology")
    size_category: Optional[str] = Field(None, description="Size category", example="large")
    website: Optional[str] = Field(None, description="Website URL", example="https://www.techcorp.com")
    logo_url: Optional[str] = Field(None, description="Logo image URL", example="https://cdn.techcorp.com/logo.png")
    employee_count: Optional[int] = Field(None, description="Number of employees", example=5000)
    address_city: Optional[str] = Field(None, description="Primary city", example="Palo Alto")
    address_state: Optional[str] = Field(None, description="Primary state", example="California")
    address_country_code: Optional[str] = Field(None, description="Country code", example="US")
    contact_count: int = Field(
        default=0,
        description="Number of contacts associated with this organization",
        example=25
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 456,
                "name": "Technology Corporation Inc.",
                "short_name": "TechCorp",
                "organization_type": "company",
                "industry": "Technology",
                "size_category": "large",
                "website": "https://www.techcorp.com",
                "logo_url": "https://cdn.techcorp.com/logo.png",
                "employee_count": 5000,
                "address_city": "Palo Alto",
                "address_state": "California",
                "address_country_code": "US",
                "contact_count": 25
            }
        }


class OrganizationListResponse(BaseModel):
    """
    Paginated organization list response.
    
    Contains a list of organizations and pagination metadata
    for efficient browsing of large organization datasets.
    """
    data: List[OrganizationSearchResult] = Field(
        ...,
        description="List of organizations for the current page"
    )
    pagination: dict = Field(
        ...,
        description="Pagination metadata including total count, current page, and page size"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": 456,
                        "name": "Technology Corporation Inc.",
                        "short_name": "TechCorp",
                        "organization_type": "company",
                        "industry": "Technology",
                        "size_category": "large",
                        "website": "https://www.techcorp.com",
                        "logo_url": "https://cdn.techcorp.com/logo.png",
                        "employee_count": 5000,
                        "address_city": "Palo Alto",
                        "address_state": "California",
                        "address_country_code": "US",
                        "contact_count": 25
                    }
                ],
                "pagination": {
                    "total": 150,
                    "page": 1,
                    "per_page": 10,
                    "total_pages": 15
                }
            }
        }