#!/usr/bin/env python3
"""
Simple test script for relationship mapping functionality.
This script tests the core logic without requiring the full dependency stack.
"""

import yaml
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_yaml_configuration():
    """Test that the YAML configuration loads correctly."""
    print("🔍 Testing YAML configuration...")
    
    config_path = Path(__file__).parent / "config" / "relationship_mappings.yaml"
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # Validate structure
        required_keys = ['version', 'gender_specific_relationships', 'relationship_types', 'categories']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Test specific mappings
        sibling_config = config.get('gender_specific_relationships', {}).get('sibling', {})
        mappings = sibling_config.get('mappings', {})
        
        expected_mappings = {
            'male_male': ['brother', 'brother'],
            'male_female': ['brother', 'sister'],
            'female_male': ['sister', 'brother'],
            'female_female': ['sister', 'sister']
        }
        
        for key, expected in expected_mappings.items():
            if key not in mappings:
                print(f"❌ Missing sibling mapping: {key}")
                return False
            if mappings[key] != expected:
                print(f"❌ Incorrect sibling mapping for {key}: expected {expected}, got {mappings[key]}")
                return False
        
        print(f"✅ YAML configuration is valid")
        print(f"   - Version: {config.get('version')}")
        print(f"   - Relationship types: {len(config.get('relationship_types', []))}")
        print(f"   - Categories: {len(config.get('categories', []))}")
        print(f"   - Gender-specific types: {len(config.get('gender_specific_relationships', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading YAML: {e}")
        return False


def test_gender_mapping_logic():
    """Test the core gender mapping logic."""
    print("\n🔍 Testing gender mapping logic...")
    
    # Simple implementation of the core logic for testing
    gender_mappings = {
        'sibling': {
            'male_male': ['brother', 'brother'],
            'male_female': ['brother', 'sister'],
            'female_male': ['sister', 'brother'],
            'female_female': ['sister', 'sister']
        },
        'uncle_aunt': {
            'male_male': ['uncle', 'nephew'],
            'male_female': ['uncle', 'niece'],
            'female_male': ['aunt', 'nephew'],
            'female_female': ['aunt', 'niece']
        }
    }
    
    def resolve_relationship(base_type, gender_a, gender_b):
        if base_type not in gender_mappings:
            return base_type, base_type, False
        
        if not gender_a or not gender_b or gender_a not in ['male', 'female'] or gender_b not in ['male', 'female']:
            return 'sibling', 'sibling', False  # fallback
        
        mapping_key = f"{gender_a}_{gender_b}"
        mappings = gender_mappings[base_type]
        
        if mapping_key in mappings:
            result = mappings[mapping_key]
            return result[0], result[1], True
        
        return 'sibling', 'sibling', False  # fallback
    
    # Test cases
    test_cases = [
        # (base_type, gender_a, gender_b, expected_a_to_b, expected_b_to_a, expected_resolved)
        ('sibling', 'male', 'male', 'brother', 'brother', True),
        ('sibling', 'male', 'female', 'brother', 'sister', True),
        ('sibling', 'female', 'male', 'sister', 'brother', True),
        ('sibling', 'female', 'female', 'sister', 'sister', True),
        ('sibling', None, 'female', 'sibling', 'sibling', False),  # fallback
        ('sibling', 'non_binary', 'female', 'sibling', 'sibling', False),  # fallback
        ('uncle_aunt', 'male', 'male', 'uncle', 'nephew', True),
        ('uncle_aunt', 'female', 'female', 'aunt', 'niece', True),
        ('friend', 'male', 'female', 'friend', 'friend', False),  # non-gender-specific
    ]
    
    all_passed = True
    
    for base_type, gender_a, gender_b, expected_a_to_b, expected_b_to_a, expected_resolved in test_cases:
        result_a_to_b, result_b_to_a, is_resolved = resolve_relationship(base_type, gender_a, gender_b)
        
        if (result_a_to_b != expected_a_to_b or 
            result_b_to_a != expected_b_to_a or 
            is_resolved != expected_resolved):
            print(f"❌ Test failed: {base_type} + {gender_a}:{gender_b}")
            print(f"   Expected: {expected_a_to_b} <-> {expected_b_to_a} (resolved: {expected_resolved})")
            print(f"   Got:      {result_a_to_b} <-> {result_b_to_a} (resolved: {is_resolved})")
            all_passed = False
        else:
            print(f"✅ {base_type} + {gender_a}:{gender_b} -> {result_a_to_b} <-> {result_b_to_a}")
    
    return all_passed


def test_file_structure():
    """Test that all required files are in place."""
    print("\n🔍 Testing file structure...")
    
    base_path = Path(__file__).parent
    required_files = [
        "config/relationship_mappings.yaml",
        "backend/app/models/contact.py",
        "backend/app/models/contact_relationship.py",
        "backend/app/schemas/contact_relationship.py",
        "backend/app/services/relationship_mapping.py",
        "backend/app/crud/contact_relationship.py",
        "backend/app/api/v1/endpoints/contact_relationships.py",
        "backend/alembic/versions/014_add_gender_and_relationships.py",
        "backend/tests/test_relationship_mapping.py"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("🚀 Running Relationship Mapping Tests")
    print("=" * 50)
    
    tests = [
        ("YAML Configuration", test_yaml_configuration),
        ("Gender Mapping Logic", test_gender_mapping_logic),
        ("File Structure", test_file_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())