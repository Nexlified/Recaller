#!/usr/bin/env python3
"""
Test script to verify the enhanced relationship system with new fields.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_enhanced_schemas():
    """Test that the enhanced schemas work correctly."""
    print("🔍 Testing enhanced relationship schemas...")
    
    try:
        from app.schemas.contact_relationship import (
            ContactRelationshipCreate,
            ContactRelationshipUpdate,
            RelationshipStatus
        )
        
        # Test creating a relationship with new fields
        relationship_data = {
            'contact_a_id': 1,
            'contact_b_id': 2,
            'relationship_type': 'sibling',
            'relationship_strength': 8,
            'relationship_status': RelationshipStatus.ACTIVE,
            'is_mutual': True,
            'notes': 'Twin brothers',
            'context': 'Met at birth',
            'override_gender_resolution': False
        }
        
        # This should work without errors
        relationship = ContactRelationshipCreate(**relationship_data)
        
        # Test validation
        assert relationship.relationship_strength == 8
        assert relationship.relationship_status == RelationshipStatus.ACTIVE
        assert relationship.is_mutual == True
        assert relationship.context == 'Met at birth'
        
        # Test update schema
        update_data = {
            'relationship_strength': 9,
            'relationship_status': RelationshipStatus.DISTANT,
            'notes': 'Updated notes'
        }
        
        update = ContactRelationshipUpdate(**update_data)
        assert update.relationship_strength == 9
        assert update.relationship_status == RelationshipStatus.DISTANT
        
        print("✅ Enhanced schemas working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced schema test failed: {e}")
        return False

def test_enhanced_models():
    """Test that the enhanced models work correctly."""
    print("🔍 Testing enhanced relationship models...")
    
    try:
        from app.models.contact_relationship import ContactRelationship, RelationshipStatus
        
        # Test that enum values are accessible
        assert RelationshipStatus.ACTIVE.value == "active"
        assert RelationshipStatus.DISTANT.value == "distant"
        assert RelationshipStatus.ENDED.value == "ended"
        
        print("✅ Enhanced models working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced model test failed: {e}")
        return False

def test_field_validation():
    """Test field validation for new fields."""
    print("🔍 Testing field validation...")
    
    try:
        from app.schemas.contact_relationship import ContactRelationshipCreate
        from pydantic import ValidationError
        
        # Test invalid relationship strength (too high)
        try:
            ContactRelationshipCreate(
                contact_a_id=1,
                contact_b_id=2,
                relationship_type='friend',
                relationship_strength=15  # Should fail - max is 10
            )
            print("❌ Should have failed validation for strength > 10")
            return False
        except ValidationError:
            pass  # Expected
        
        # Test invalid relationship strength (too low)
        try:
            ContactRelationshipCreate(
                contact_a_id=1,
                contact_b_id=2,
                relationship_type='friend',
                relationship_strength=0  # Should fail - min is 1
            )
            print("❌ Should have failed validation for strength < 1")
            return False
        except ValidationError:
            pass  # Expected
        
        # Test valid strength
        valid = ContactRelationshipCreate(
            contact_a_id=1,
            contact_b_id=2,
            relationship_type='friend',
            relationship_strength=5  # Should work
        )
        assert valid.relationship_strength == 5
        
        print("✅ Field validation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Field validation test failed: {e}")
        return False

def main():
    """Run all enhancement tests."""
    print("🚀 Running Relationship Enhancement Tests")
    print("=" * 50)
    
    tests = [
        test_enhanced_schemas,
        test_enhanced_models,
        test_field_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhancement tests passed!")
        return 0
    else:
        print("💥 Some enhancement tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())