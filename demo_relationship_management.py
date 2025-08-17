"""
Demo script showing the Relationship Management system capabilities.
This demonstrates the key features requested in the issue.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def demonstrate_minimal_profile_creation():
    """Show how to create a profile with just a name."""
    from app.schemas.person_profile import PersonProfileCreate
    
    print("🎯 Demonstrating Minimal Profile Creation")
    print("-" * 50)
    
    # Create profile with just first name
    minimal_profile = PersonProfileCreate(
        first_name="Alice"
    )
    print(f"✅ Created minimal profile: {minimal_profile.first_name}")
    
    # Create profile with first and last name
    basic_profile = PersonProfileCreate(
        first_name="Bob",
        last_name="Smith"
    )
    print(f"✅ Created basic profile: {basic_profile.first_name} {basic_profile.last_name}")
    
    # Create profile with display name
    display_profile = PersonProfileCreate(
        first_name="Robert",
        last_name="Johnson",
        display_name="Bobby",
        notes="Met at conference"
    )
    print(f"✅ Created profile with display name: {display_profile.display_name} ({display_profile.first_name})")
    print()

def demonstrate_normalized_information():
    """Show the normalized database structure."""
    from app.schemas.person_profile import (
        PersonContactInfoCreate,
        PersonProfessionalInfoCreate,
        PersonPersonalInfoCreate,
        PersonLifeEventCreate,
        PersonBelongingCreate
    )
    
    print("🗄️ Demonstrating Normalized Information Structure")
    print("-" * 50)
    
    person_id = 1  # Would be actual person ID in real usage
    
    # Contact Information
    contact_info = PersonContactInfoCreate(
        person_id=person_id,
        email="alice@example.com",
        phone="+1-555-0123",
        address_line1="123 Main St",
        city="Anytown",
        state="CA",
        contact_type="personal",
        is_primary=True
    )
    print(f"📧 Contact Info: {contact_info.email}, {contact_info.phone}")
    
    # Professional Information
    professional_info = PersonProfessionalInfoCreate(
        person_id=person_id,
        job_title="Software Engineer",
        organization_name="Tech Corp",
        department="Engineering",
        is_current=True,
        employment_type="full-time"
    )
    print(f"💼 Professional: {professional_info.job_title} at {professional_info.organization_name}")
    
    # Personal Information
    personal_info = PersonPersonalInfoCreate(
        person_id=person_id,
        date_of_birth="1990-05-15",
        favorite_color="blue",
        dietary_restrictions="vegetarian",
        interests_hobbies="photography, hiking"
    )
    print(f"👤 Personal: Born {personal_info.date_of_birth}, likes {personal_info.favorite_color}")
    
    # Life Event
    life_event = PersonLifeEventCreate(
        person_id=person_id,
        event_type="graduation",
        title="Computer Science Degree",
        event_date="2012-06-15",
        location="University of California",
        significance=8
    )
    print(f"🎓 Life Event: {life_event.title} on {life_event.event_date}")
    
    # Belonging
    belonging = PersonBelongingCreate(
        person_id=person_id,
        name="MacBook Pro",
        category="electronics",
        brand="Apple",
        model="M2 13-inch",
        relationship_context="Uses for work and personal projects"
    )
    print(f"💻 Belonging: {belonging.brand} {belonging.model} - {belonging.name}")
    print()

def demonstrate_privacy_controls():
    """Show privacy control features."""
    from app.schemas.person_profile import PersonProfileCreate, PersonProfileVisibility
    
    print("🔒 Demonstrating Privacy Controls")
    print("-" * 50)
    
    # Private profile (default)
    private_profile = PersonProfileCreate(
        first_name="Private",
        last_name="Person",
        visibility=PersonProfileVisibility.PRIVATE
    )
    print(f"🔐 Private profile: {private_profile.first_name} {private_profile.last_name}")
    print("   → Only visible to creator")
    
    # Tenant-shared profile
    shared_profile = PersonProfileCreate(
        first_name="Shared",
        last_name="Person",
        visibility=PersonProfileVisibility.TENANT_SHARED
    )
    print(f"👥 Tenant-shared profile: {shared_profile.first_name} {shared_profile.last_name}")
    print("   → Visible to all users in the same tenant")
    print()

def demonstrate_relationship_types():
    """Show different relationship types."""
    from app.schemas.person_profile import PersonRelationshipCreate
    
    print("🤝 Demonstrating Relationship Types")
    print("-" * 50)
    
    # Family relationship
    family_rel = PersonRelationshipCreate(
        person_a_id=1,
        person_b_id=2,
        relationship_type="sister",
        relationship_category="family",
        relationship_strength=9,
        how_we_met="She's my sister!",
        is_mutual=True
    )
    print(f"👨‍👩‍👧‍👦 Family: {family_rel.relationship_type} (strength: {family_rel.relationship_strength}/10)")
    
    # Professional relationship
    work_rel = PersonRelationshipCreate(
        person_a_id=1,
        person_b_id=3,
        relationship_type="colleague",
        relationship_category="professional",
        relationship_strength=7,
        context="Same engineering team"
    )
    print(f"💼 Professional: {work_rel.relationship_type} - {work_rel.context}")
    
    # Social relationship
    social_rel = PersonRelationshipCreate(
        person_a_id=1,
        person_b_id=4,
        relationship_type="friend",
        relationship_category="social",
        relationship_strength=8,
        how_we_met="Met at photography club",
        start_date="2020-03-15"
    )
    print(f"👫 Social: {social_rel.relationship_type} - {social_rel.how_we_met}")
    print()

def demonstrate_api_structure():
    """Show the API endpoint structure."""
    print("🌐 API Endpoint Structure")
    print("-" * 50)
    
    endpoints = [
        ("GET", "/relationship-management/profiles/", "List person profiles"),
        ("POST", "/relationship-management/profiles/", "Create new profile"),
        ("GET", "/relationship-management/profiles/{id}", "Get specific profile"),
        ("PUT", "/relationship-management/profiles/{id}", "Update profile"),
        ("DELETE", "/relationship-management/profiles/{id}", "Delete profile"),
        ("GET", "/relationship-management/profiles/{id}/contact-info/", "Get contact information"),
        ("POST", "/relationship-management/profiles/{id}/contact-info/", "Add contact information"),
        ("GET", "/relationship-management/profiles/{id}/professional-info/", "Get professional info"),
        ("GET", "/relationship-management/profiles/{id}/personal-info/", "Get personal info"),
        ("GET", "/relationship-management/profiles/{id}/life-events/", "Get life events"),
        ("GET", "/relationship-management/profiles/{id}/belongings/", "Get belongings"),
        ("GET", "/relationship-management/profiles/{id}/relationships/", "Get relationships"),
        ("POST", "/relationship-management/relationships/", "Create relationship"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"  {method:6} {endpoint:50} # {description}")
    print()

def demonstrate_comparison_with_old_system():
    """Compare with the old Contact system."""
    print("📊 Comparison: Old vs New System")
    print("-" * 50)
    
    print("OLD CONTACT SYSTEM:")
    print("  ❌ Monolithic Contact table with all fields")
    print("  ❌ Limited information types")
    print("  ❌ No belongings or life events")
    print("  ❌ Basic relationship mapping")
    print("  ❌ All-or-nothing privacy")
    print()
    
    print("NEW RELATIONSHIP MANAGEMENT SYSTEM:")
    print("  ✅ Normalized tables (6 separate tables)")
    print("  ✅ Rich information types (contact, professional, personal, events, belongings)")
    print("  ✅ Comprehensive life event tracking")
    print("  ✅ Advanced relationship management")
    print("  ✅ Granular privacy controls per information type")
    print("  ✅ Minimal profile creation (just name required)")
    print("  ✅ Extensible structure for future enhancements")
    print()

def main():
    """Run the demonstration."""
    print("🎭 Person Profile / Relationship Management System Demo")
    print("=" * 65)
    print("This demonstrates the key features from issue #228:")
    print("- Minimal profile creation with just a name")
    print("- Normalized database structure") 
    print("- Privacy controls")
    print("- Rich relationship management")
    print("- Life events, belongings, and comprehensive person info")
    print("=" * 65)
    print()
    
    demonstrate_minimal_profile_creation()
    demonstrate_normalized_information()
    demonstrate_privacy_controls()
    demonstrate_relationship_types()
    demonstrate_api_structure()
    demonstrate_comparison_with_old_system()
    
    print("🎉 Demo Complete!")
    print("The new Relationship Management system provides:")
    print("  • Better database normalization")
    print("  • Enhanced privacy controls")
    print("  • Richer person information tracking")
    print("  • Improved relationship management")
    print("  • Extensible architecture for future features")

if __name__ == "__main__":
    main()