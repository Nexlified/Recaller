"""
Organization seed data for testing and development
This file contains sample organizations that can be loaded into the database
"""

SAMPLE_ORGANIZATIONS = [
    {
        "name": "Stanford University",
        "short_name": "Stanford",
        "organization_type": "school",
        "industry": "education",
        "size_category": "large",
        "website": "https://stanford.edu",
        "email": "info@stanford.edu",
        "phone": "+1-650-723-2300",
        "address_street": "450 Serra Mall",
        "address_city": "Stanford",
        "address_state": "CA",
        "address_postal_code": "94305",
        "address_country_code": "US",
        "founded_year": 1885,
        "description": "Private research university in California",
        "employee_count": 12000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "Stanford University", "alias_type": "legal_name"},
            {"alias_name": "SU", "alias_type": "abbreviation"},
            {"alias_name": "The Farm", "alias_type": "common_name"}
        ],
        "locations": [
            {
                "location_name": "Main Campus",
                "location_type": "campus",
                "address_street": "450 Serra Mall",
                "address_city": "Stanford",
                "address_state": "CA",
                "address_postal_code": "94305",
                "address_country_code": "US",
                "is_primary": True
            }
        ]
    },
    {
        "name": "Google LLC",
        "short_name": "Google",
        "organization_type": "company",
        "industry": "technology",
        "size_category": "enterprise",
        "website": "https://google.com",
        "email": "contact@google.com",
        "address_street": "1600 Amphitheatre Parkway",
        "address_city": "Mountain View",
        "address_state": "CA",
        "address_postal_code": "94043",
        "address_country_code": "US",
        "founded_year": 1998,
        "description": "Multinational technology company specializing in Internet-related services",
        "employee_count": 150000,
        "annual_revenue": 280000000000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "Alphabet Inc.", "alias_type": "legal_name"},
            {"alias_name": "GOOGL", "alias_type": "abbreviation"},
            {"alias_name": "Google Inc.", "alias_type": "former_name"}
        ],
        "locations": [
            {
                "location_name": "Googleplex",
                "location_type": "headquarters",
                "address_street": "1600 Amphitheatre Parkway",
                "address_city": "Mountain View",
                "address_state": "CA",
                "address_postal_code": "94043",
                "address_country_code": "US",
                "employee_count": 25000,
                "is_primary": True
            },
            {
                "location_name": "Google New York",
                "location_type": "branch",
                "address_street": "111 8th Avenue",
                "address_city": "New York",
                "address_state": "NY",
                "address_postal_code": "10011",
                "address_country_code": "US",
                "employee_count": 12000
            }
        ]
    },
    {
        "name": "Massachusetts Institute of Technology",
        "short_name": "MIT",
        "organization_type": "school",
        "industry": "education",
        "size_category": "large",
        "website": "https://mit.edu",
        "email": "info@mit.edu",
        "address_street": "77 Massachusetts Avenue",
        "address_city": "Cambridge",
        "address_state": "MA",
        "address_postal_code": "02139",
        "address_country_code": "US",
        "founded_year": 1861,
        "description": "Private research university focusing on science and technology",
        "employee_count": 11000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "MIT", "alias_type": "abbreviation"},
            {"alias_name": "The Institute", "alias_type": "common_name"}
        ]
    },
    {
        "name": "Microsoft Corporation",
        "short_name": "Microsoft",
        "organization_type": "company",
        "industry": "technology",
        "size_category": "enterprise",
        "website": "https://microsoft.com",
        "email": "info@microsoft.com",
        "address_street": "1 Microsoft Way",
        "address_city": "Redmond",
        "address_state": "WA",
        "address_postal_code": "98052",
        "address_country_code": "US",
        "founded_year": 1975,
        "description": "Multinational technology corporation developing software, hardware, and cloud services",
        "employee_count": 220000,
        "annual_revenue": 211000000000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "MSFT", "alias_type": "abbreviation"},
            {"alias_name": "Microsoft Corp", "alias_type": "legal_name"}
        ]
    },
    {
        "name": "Mayo Clinic",
        "organization_type": "healthcare",
        "industry": "healthcare",
        "size_category": "large",
        "website": "https://mayoclinic.org",
        "address_street": "200 First St SW",
        "address_city": "Rochester",
        "address_state": "MN",
        "address_postal_code": "55905",
        "address_country_code": "US",
        "founded_year": 1889,
        "description": "Non-profit American academic medical center focused on healthcare, education, and research",
        "employee_count": 70000,
        "is_verified": True
    },
    {
        "name": "American Red Cross",
        "organization_type": "nonprofit",
        "industry": "humanitarian",
        "website": "https://redcross.org",
        "address_street": "2025 E Street NW",
        "address_city": "Washington",
        "address_state": "DC",
        "address_postal_code": "20006",
        "address_country_code": "US",
        "founded_year": 1881,
        "description": "Humanitarian organization providing emergency assistance and disaster relief",
        "employee_count": 20000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "ARC", "alias_type": "abbreviation"},
            {"alias_name": "The Red Cross", "alias_type": "common_name"}
        ]
    },
    {
        "name": "Apple Inc.",
        "short_name": "Apple",
        "organization_type": "company",
        "industry": "technology",
        "size_category": "enterprise",
        "website": "https://apple.com",
        "address_street": "One Apple Park Way",
        "address_city": "Cupertino",
        "address_state": "CA",
        "address_postal_code": "95014",
        "address_country_code": "US",
        "founded_year": 1976,
        "description": "Multinational technology company designing consumer electronics and software",
        "employee_count": 164000,
        "annual_revenue": 394000000000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "AAPL", "alias_type": "abbreviation"},
            {"alias_name": "Apple Computer Inc.", "alias_type": "former_name"}
        ]
    },
    {
        "name": "Johns Hopkins University",
        "short_name": "JHU",
        "organization_type": "school",
        "industry": "education",
        "size_category": "large",
        "website": "https://jhu.edu",
        "address_street": "3400 N Charles St",
        "address_city": "Baltimore",
        "address_state": "MD",
        "address_postal_code": "21218",
        "address_country_code": "US",
        "founded_year": 1876,
        "description": "Private research university known for medicine and public health",
        "employee_count": 27000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "Johns Hopkins", "alias_type": "common_name"},
            {"alias_name": "JHU", "alias_type": "abbreviation"}
        ]
    },
    {
        "name": "Salesforce, Inc.",
        "short_name": "Salesforce",
        "organization_type": "company",
        "industry": "technology",
        "size_category": "large",
        "website": "https://salesforce.com",
        "address_street": "415 Mission Street",
        "address_city": "San Francisco",
        "address_state": "CA",
        "address_postal_code": "94105",
        "address_country_code": "US",
        "founded_year": 1999,
        "description": "Cloud-based software company providing CRM and enterprise applications",
        "employee_count": 73000,
        "annual_revenue": 31000000000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "CRM", "alias_type": "abbreviation"},
            {"alias_name": "Salesforce.com", "alias_type": "former_name"}
        ]
    },
    {
        "name": "World Health Organization",
        "short_name": "WHO",
        "organization_type": "government",
        "industry": "healthcare",
        "website": "https://who.int",
        "address_street": "Avenue Appia 20",
        "address_city": "Geneva",
        "address_postal_code": "1211",
        "address_country_code": "CH",
        "founded_year": 1948,
        "description": "United Nations agency responsible for international public health",
        "employee_count": 8000,
        "is_verified": True,
        "aliases": [
            {"alias_name": "WHO", "alias_type": "abbreviation"},
            {"alias_name": "OMS", "alias_type": "abbreviation"}  # French/Spanish
        ]
    }
]

def create_organizations_in_db(db_session, tenant_id: int, created_by_user_id: int):
    """
    Create sample organizations in the database
    This function would be used during development/testing with a real database
    """
    from app.models.organization import Organization, OrganizationAlias, OrganizationLocation
    from app.crud.organization import create_organization
    from app.schemas.organization import OrganizationCreate
    
    created_orgs = []
    
    for org_data in SAMPLE_ORGANIZATIONS:
        # Extract aliases and locations
        aliases_data = org_data.pop('aliases', [])
        locations_data = org_data.pop('locations', [])
        
        # Create organization
        org_schema = OrganizationCreate(**org_data)
        organization = create_organization(
            db=db_session,
            obj_in=org_schema,
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id
        )
        
        # Add aliases
        for alias_data in aliases_data:
            alias = OrganizationAlias(
                organization_id=organization.id,
                **alias_data
            )
            db_session.add(alias)
        
        # Add locations
        for location_data in locations_data:
            location = OrganizationLocation(
                organization_id=organization.id,
                **location_data
            )
            db_session.add(location)
        
        db_session.commit()
        created_orgs.append(organization)
    
    return created_orgs