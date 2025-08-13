#!/usr/bin/env python3

"""
Create a focused test for contact visibility that follows the existing test patterns
"""

import pytest
import sys
import os

# Add the backend directory to the path
sys.path.append('/home/runner/work/Recaller/Recaller/backend')

from app.schemas.contact import ContactVisibility, ContactCreate, ContactUpdate

class TestContactVisibilitySchemas:
    """Test the contact visibility schemas"""
    
    def test_contact_visibility_enum(self):
        """Test ContactVisibility enum values"""
        assert ContactVisibility.PRIVATE == "private"
        assert ContactVisibility.PUBLIC == "public"
    
    def test_contact_create_with_visibility(self):
        """Test creating a contact with explicit visibility"""
        contact_data = {
            "first_name": "John", 
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "visibility": ContactVisibility.PUBLIC
        }
        
        contact = ContactCreate(**contact_data)
        assert contact.visibility == ContactVisibility.PUBLIC
        assert contact.first_name == "John"
    
    def test_contact_create_default_visibility(self):
        """Test that contacts default to private visibility"""
        contact_data = {
            "first_name": "Jane",
            "last_name": "Smith", 
            "email": "jane.smith@example.com"
        }
        
        contact = ContactCreate(**contact_data)
        assert contact.visibility == ContactVisibility.PRIVATE
    
    def test_contact_update_visibility(self):
        """Test updating contact visibility"""
        contact_update = ContactUpdate(visibility=ContactVisibility.PUBLIC)
        assert contact_update.visibility == ContactVisibility.PUBLIC
        
        # Test updating visibility to private
        contact_update_private = ContactUpdate(visibility=ContactVisibility.PRIVATE)
        assert contact_update_private.visibility == ContactVisibility.PRIVATE

class TestContactModelImport:
    """Test that the Contact model imports correctly with new fields"""
    
    def test_contact_model_import(self):
        """Test importing the Contact model"""
        from app.models.contact import Contact, ContactVisibility as ModelVisibility
        
        # Check that enum is available
        assert ModelVisibility.PRIVATE.value == "private"
        assert ModelVisibility.PUBLIC.value == "public"
    
    def test_contact_crud_functions_import(self):
        """Test importing new CRUD functions"""
        from app.crud.contact import (
            get_user_contacts,
            get_public_contacts, 
            get_contact_with_user_access,
            can_user_edit_contact
        )
        
        # All functions should be callable
        assert callable(get_user_contacts)
        assert callable(get_public_contacts)
        assert callable(get_contact_with_user_access)
        assert callable(can_user_edit_contact)

if __name__ == "__main__":
    # Run the tests using pytest
    exit_code = pytest.main([__file__, "-v"])
    sys.exit(exit_code)