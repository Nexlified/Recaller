"""
Test script for the new Person Profile / Relationship Management API
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_person_profile_models():
    """Test that person profile models can be imported and instantiated."""
    from app.models.person_profile import PersonProfile, PersonContactInfo, PersonProfessionalInfo
    from app.schemas.person_profile import PersonProfileCreate, PersonContactInfoCreate
    
    # Test creating schema objects
    profile_create = PersonProfileCreate(
        first_name="John",
        last_name="Doe",
        display_name="Johnny"
    )
    
    contact_create = PersonContactInfoCreate(
        person_id=1,
        email="john.doe@example.com",
        phone="+1234567890",
        contact_type="personal",
        is_primary=True
    )
    
    print("✅ Person profile schemas created successfully")
    print(f"   Profile: {profile_create.first_name} {profile_create.last_name}")
    print(f"   Contact: {contact_create.email}")
    
    return True

def test_crud_functions():
    """Test that CRUD functions can be imported."""
    from app.crud.person_profile import (
        create_person_profile,
        get_person_profile,
        get_user_person_profiles,
        create_person_contact_info
    )
    
    print("✅ Person profile CRUD functions imported successfully")
    return True

def test_api_endpoints():
    """Test that API endpoints can be imported."""
    from app.api.v1.endpoints.relationship_management import router
    
    # Count the number of routes
    route_count = len(router.routes)
    print(f"✅ Relationship management API router loaded with {route_count} routes")
    
    # List some example routes
    for i, route in enumerate(router.routes[:5]):
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"   Route {i+1}: {methods} {route.path}")
    
    return True

def test_api_integration():
    """Test that the API is properly integrated."""
    from app.api.v1.api import api_router
    
    # Check if our relationship management routes are included
    relationship_routes = []
    for route in api_router.routes:
        if hasattr(route, 'path') and '/relationship-management' in route.path:
            relationship_routes.append(route.path)
    
    if relationship_routes:
        print(f"✅ Relationship management routes integrated: {len(relationship_routes)} routes found")
        for route in relationship_routes[:3]:
            print(f"   {route}")
    else:
        print("❌ No relationship management routes found in main API router")
        return False
    
    return True

def test_database_models():
    """Test database model relationships."""
    from app.models.person_profile import PersonProfile, PersonContactInfo
    from app.models.user import User
    from app.models.tenant import Tenant
    
    # Test that model classes exist and have expected attributes
    profile_attrs = ['first_name', 'last_name', 'tenant_id', 'created_by_user_id']
    for attr in profile_attrs:
        if not hasattr(PersonProfile, attr):
            print(f"❌ PersonProfile missing attribute: {attr}")
            return False
    
    contact_attrs = ['person_id', 'email', 'phone', 'is_primary']
    for attr in contact_attrs:
        if not hasattr(PersonContactInfo, attr):
            print(f"❌ PersonContactInfo missing attribute: {attr}")
            return False
    
    # Test that relationships are properly defined
    if not hasattr(User, 'person_profiles'):
        print("❌ User model missing person_profiles relationship")
        return False
    
    if not hasattr(Tenant, 'person_profiles'):
        print("❌ Tenant model missing person_profiles relationship")
        return False
    
    print("✅ Database models have correct attributes and relationships")
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Person Profile / Relationship Management System")
    print("=" * 60)
    
    tests = [
        ("Person Profile Models", test_person_profile_models),
        ("CRUD Functions", test_crud_functions),
        ("API Endpoints", test_api_endpoints),
        ("API Integration", test_api_integration),
        ("Database Models", test_database_models),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Relationship Management system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())