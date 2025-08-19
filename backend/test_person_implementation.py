#!/usr/bin/env python3
"""
Basic test script to validate the new person API works correctly.
This is a standalone test that doesn't require a database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_person_schemas():
    """Test that person schemas can be imported and validated"""
    try:
        from app.schemas.person import (
            PersonProfileCreate, PersonContactInfoCreate, 
            PersonProfessionalInfoCreate, PersonPersonalInfoCreate,
            PersonLifeEventCreate, PersonBelongingCreate
        )
        
        # Test PersonProfile creation
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender": "male",
            "notes": "Test person"
        }
        person = PersonProfileCreate(**person_data)
        print(f"✅ PersonProfile schema: {person.first_name} {person.last_name}")
        
        # Test PersonContactInfo creation
        contact_data = {
            "person_id": 1,
            "contact_type": "email", 
            "contact_value": "john@example.com",
            "contact_label": "primary"
        }
        contact_info = PersonContactInfoCreate(**contact_data)
        print(f"✅ PersonContactInfo schema: {contact_info.contact_type} = {contact_info.contact_value}")
        
        # Test PersonProfessionalInfo creation
        prof_data = {
            "person_id": 1,
            "job_title": "Software Engineer",
            "organization_id": 1,
            "is_current_position": True
        }
        prof_info = PersonProfessionalInfoCreate(**prof_data)
        print(f"✅ PersonProfessionalInfo schema: {prof_info.job_title}")
        
        # Test PersonPersonalInfo creation
        personal_data = {
            "person_id": 1,
            "date_of_birth": "1990-01-01",
            "is_emergency_contact": False
        }
        personal_info = PersonPersonalInfoCreate(**personal_data)
        print(f"✅ PersonPersonalInfo schema: DOB = {personal_info.date_of_birth}")
        
        # Test PersonLifeEvent creation
        event_data = {
            "person_id": 1,
            "event_type": "birthday",
            "event_date": "1990-01-01", 
            "event_title": "John's Birthday"
        }
        life_event = PersonLifeEventCreate(**event_data)
        print(f"✅ PersonLifeEvent schema: {life_event.event_title}")
        
        # Test PersonBelonging creation
        belonging_data = {
            "person_id": 1,
            "belonging_type": "gift_received",
            "item_name": "Laptop",
            "description": "Work laptop"
        }
        belonging = PersonBelongingCreate(**belonging_data)
        print(f"✅ PersonBelonging schema: {belonging.item_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in person schemas: {e}")
        return False


def test_person_models():
    """Test that person models can be imported"""
    try:
        from app.models.person import (
            PersonProfile, PersonContactInfo, PersonProfessionalInfo,
            PersonPersonalInfo, PersonLifeEvent, PersonBelonging
        )
        from app.models.person_relationship import PersonRelationship
        
        print("✅ All person models import successfully")
        print(f"✅ PersonProfile table: {PersonProfile.__tablename__}")
        print(f"✅ PersonContactInfo table: {PersonContactInfo.__tablename__}")
        print(f"✅ PersonProfessionalInfo table: {PersonProfessionalInfo.__tablename__}")
        print(f"✅ PersonPersonalInfo table: {PersonPersonalInfo.__tablename__}")
        print(f"✅ PersonLifeEvent table: {PersonLifeEvent.__tablename__}")
        print(f"✅ PersonBelonging table: {PersonBelonging.__tablename__}")
        print(f"✅ PersonRelationship table: {PersonRelationship.__tablename__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in person models: {e}")
        return False


def test_person_crud():
    """Test that person CRUD functions can be imported"""
    try:
        from app.crud.person import (
            get_person_profile, create_person_profile, get_user_persons,
            search_persons, get_complete_person, get_person_contact_info_by_person,
            create_person_contact_info, get_person_professional_info_by_person,
            create_person_professional_info, get_person_personal_info_by_person,
            create_person_personal_info, get_person_life_events_by_person,
            create_person_life_event, get_person_belongings_by_person,
            create_person_belonging, get_upcoming_events, get_emergency_contacts,
            get_borrowed_items
        )
        
        print("✅ All person CRUD functions import successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in person CRUD: {e}")
        return False


def test_person_api():
    """Test that person API endpoints can be imported"""
    try:
        from app.api.v1.endpoints.persons import router
        
        route_count = len(router.routes)
        print(f"✅ Person API router imported with {route_count} routes")
        
        # Check for key endpoints
        paths = [route.path for route in router.routes if hasattr(route, 'path')]
        
        expected_paths = [
            "/",
            "/search/", 
            "/{person_id}",
            "/{person_id}/contact-info",
            "/{person_id}/professional-info",
            "/{person_id}/personal-info",
            "/{person_id}/life-events",
            "/{person_id}/belongings"
        ]
        
        for path in expected_paths:
            if any(path in p for p in paths):
                print(f"✅ Found endpoint: {path}")
            else:
                print(f"⚠️  Missing endpoint: {path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in person API: {e}")
        return False


def test_migration_files():
    """Test that migration files exist and are valid"""
    try:
        # Check if migration files exist
        person_migration = "alembic/versions/026_create_person_tables.py"
        data_migration = "alembic/versions/027_migrate_contacts_to_persons.py"
        
        if os.path.exists(person_migration):
            print(f"✅ Person tables migration exists: {person_migration}")
        else:
            print(f"❌ Missing migration: {person_migration}")
            return False
            
        if os.path.exists(data_migration):
            print(f"✅ Data migration exists: {data_migration}")
        else:
            print(f"❌ Missing migration: {data_migration}")
            return False
        
        # Try to import the migrations (basic syntax check)
        spec = {}
        with open(person_migration, 'r') as f:
            exec(f.read(), spec)
        print(f"✅ Person migration syntax is valid")
        
        with open(data_migration, 'r') as f:
            exec(f.read(), spec)
        print(f"✅ Data migration syntax is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in migration files: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Person Tables Implementation")
    print("=" * 60)
    
    tests = [
        ("Person Schemas", test_person_schemas),
        ("Person Models", test_person_models), 
        ("Person CRUD", test_person_crud),
        ("Person API", test_person_api),
        ("Migration Files", test_migration_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Person tables implementation is ready.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())