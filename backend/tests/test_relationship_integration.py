"""
Integration tests for the contact relationship system.
These tests demonstrate the complete workflow from contact creation to relationship management.
"""

import pytest
from typing import Dict, Any


class TestContactRelationshipIntegration:
    """Integration tests for contact relationships with gender resolution."""
    
    @pytest.fixture
    def sample_contacts(self):
        """Sample contact data for testing."""
        return {
            'john': {
                'first_name': 'John',
                'last_name': 'Smith',
                'gender': 'male',
                'email': 'john@example.com'
            },
            'jane': {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'gender': 'female',
                'email': 'jane@example.com'
            },
            'alex': {
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'gender': 'non_binary',
                'email': 'alex@example.com'
            },
            'bob': {
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'gender': None,  # No gender specified
                'email': 'bob@example.com'
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_sibling_relationship_male_female(self, test_client, sample_contacts):
        """Test creating a sibling relationship between male and female contacts."""
        # This test would require a full test environment with database
        # For now, it serves as documentation of the expected workflow
        
        # Step 1: Create contacts
        john_data = sample_contacts['john']
        jane_data = sample_contacts['jane']
        
        # POST /api/v1/contacts/
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        jane_response = await test_client.post("/api/v1/contacts/", json=jane_data)
        
        john_id = john_response.json()['id']
        jane_id = jane_response.json()['id']
        
        # Step 2: Create sibling relationship
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': jane_id,
            'relationship_type': 'sibling',
            'notes': 'Twins'
        }
        
        # POST /api/v1/relationships/
        relationship_response = await test_client.post("/api/v1/relationships/", json=relationship_data)
        
        # Step 3: Verify gender resolution
        result = relationship_response.json()
        assert result['relationship_a_to_b'] == 'brother'
        assert result['relationship_b_to_a'] == 'sister'
        assert result['is_gender_resolved'] is True
        assert result['original_relationship_type'] == 'sibling'
        
        # Step 4: Verify bidirectional relationships exist
        john_relationships = await test_client.get(f"/api/v1/relationships/contact/{john_id}")
        jane_relationships = await test_client.get(f"/api/v1/relationships/contact/{jane_id}")
        
        assert len(john_relationships.json()) == 1
        assert len(jane_relationships.json()) == 1
        
        # John's relationship should show Jane as sister
        john_rel = john_relationships.json()[0]
        assert john_rel['relationship_type'] == 'brother'
        assert john_rel['contact_b_id'] == jane_id
        
        # Jane's relationship should show John as brother
        jane_rel = jane_relationships.json()[0]
        assert jane_rel['relationship_type'] == 'sister'
        assert jane_rel['contact_b_id'] == john_id
    
    @pytest.mark.asyncio
    async def test_create_relationship_with_non_binary_fallback(self, test_client, sample_contacts):
        """Test relationship creation falls back when one contact is non-binary."""
        
        john_data = sample_contacts['john']
        alex_data = sample_contacts['alex']  # non_binary
        
        # Create contacts
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        alex_response = await test_client.post("/api/v1/contacts/", json=alex_data)
        
        john_id = john_response.json()['id']
        alex_id = alex_response.json()['id']
        
        # Create sibling relationship
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': alex_id,
            'relationship_type': 'sibling'
        }
        
        relationship_response = await test_client.post("/api/v1/relationships/", json=relationship_data)
        result = relationship_response.json()
        
        # Should fall back to base types
        assert result['relationship_a_to_b'] == 'sibling'
        assert result['relationship_b_to_a'] == 'sibling'
        assert result['is_gender_resolved'] is False
        assert result['original_relationship_type'] == 'sibling'
    
    @pytest.mark.asyncio
    async def test_create_uncle_aunt_relationship(self, test_client, sample_contacts):
        """Test creating uncle-nephew relationship with automatic gender resolution."""
        
        john_data = sample_contacts['john']  # Uncle (male)
        jane_data = {**sample_contacts['jane'], 'first_name': 'Jimmy', 'gender': 'male'}  # Nephew (male)
        
        # Create contacts
        uncle_response = await test_client.post("/api/v1/contacts/", json=john_data)
        nephew_response = await test_client.post("/api/v1/contacts/", json=jane_data)
        
        uncle_id = uncle_response.json()['id']
        nephew_id = nephew_response.json()['id']
        
        # Create uncle/aunt relationship
        relationship_data = {
            'contact_a_id': uncle_id,
            'contact_b_id': nephew_id,
            'relationship_type': 'uncle_aunt'
        }
        
        relationship_response = await test_client.post("/api/v1/relationships/", json=relationship_data)
        result = relationship_response.json()
        
        # Should resolve to uncle-nephew
        assert result['relationship_a_to_b'] == 'uncle'
        assert result['relationship_b_to_a'] == 'nephew'
        assert result['is_gender_resolved'] is True
        assert result['original_relationship_type'] == 'uncle_aunt'
    
    @pytest.mark.asyncio
    async def test_override_gender_resolution(self, test_client, sample_contacts):
        """Test manual override of automatic gender resolution."""
        
        john_data = sample_contacts['john']
        jane_data = sample_contacts['jane']
        
        # Create contacts
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        jane_response = await test_client.post("/api/v1/contacts/", json=jane_data)
        
        john_id = john_response.json()['id']
        jane_id = jane_response.json()['id']
        
        # Create relationship with manual override
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': jane_id,
            'relationship_type': 'friend',  # Non-gender-specific type
            'override_gender_resolution': True
        }
        
        relationship_response = await test_client.post("/api/v1/relationships/", json=relationship_data)
        result = relationship_response.json()
        
        # Should use the specified relationship type
        assert result['relationship_a_to_b'] == 'friend'
        assert result['relationship_b_to_a'] == 'friend'
        assert result['is_gender_resolved'] is False
    
    @pytest.mark.asyncio
    async def test_update_relationship_type(self, test_client, sample_contacts):
        """Test updating an existing relationship type."""
        
        john_data = sample_contacts['john']
        jane_data = sample_contacts['jane']
        
        # Create contacts and initial relationship
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        jane_response = await test_client.post("/api/v1/contacts/", json=jane_data)
        
        john_id = john_response.json()['id']
        jane_id = jane_response.json()['id']
        
        # Create initial friend relationship
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': jane_id,
            'relationship_type': 'friend'
        }
        
        await test_client.post("/api/v1/relationships/", json=relationship_data)
        
        # Update to sibling relationship
        update_response = await test_client.put(
            f"/api/v1/relationships/{john_id}/{jane_id}",
            params={
                'new_relationship_type': 'sibling',
                'notes': 'Updated relationship'
            }
        )
        
        result = update_response.json()
        
        # Should resolve to gender-specific types
        assert result['relationship_a_to_b'] == 'brother'
        assert result['relationship_b_to_a'] == 'sister'
        assert result['is_gender_resolved'] is True
    
    @pytest.mark.asyncio
    async def test_relationship_summary(self, test_client, sample_contacts):
        """Test getting a relationship summary for a contact."""
        
        # Create multiple contacts and relationships
        contacts = []
        for contact_data in sample_contacts.values():
            response = await test_client.post("/api/v1/contacts/", json=contact_data)
            contacts.append(response.json())
        
        main_contact = contacts[0]
        
        # Create various relationships
        relationships = [
            {'contact_b_id': contacts[1]['id'], 'relationship_type': 'sibling'},
            {'contact_b_id': contacts[2]['id'], 'relationship_type': 'friend'},
            {'contact_b_id': contacts[3]['id'], 'relationship_type': 'colleague'},
        ]
        
        for rel_data in relationships:
            relationship_data = {
                'contact_a_id': main_contact['id'],
                **rel_data
            }
            await test_client.post("/api/v1/relationships/", json=relationship_data)
        
        # Get relationship summary
        summary_response = await test_client.get(
            f"/api/v1/relationships/contact/{main_contact['id']}/summary"
        )
        
        summary = summary_response.json()
        
        # Should have relationships grouped by category
        assert 'family' in summary
        assert 'social' in summary
        assert 'professional' in summary
        
        # Family should include the sibling relationship
        family_rels = summary['family']
        assert len(family_rels) == 1
        assert family_rels[0]['relationship_type'] in ['brother', 'sister', 'sibling']
    
    @pytest.mark.asyncio
    async def test_delete_relationship(self, test_client, sample_contacts):
        """Test deleting a bidirectional relationship."""
        
        john_data = sample_contacts['john']
        jane_data = sample_contacts['jane']
        
        # Create contacts and relationship
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        jane_response = await test_client.post("/api/v1/contacts/", json=jane_data)
        
        john_id = john_response.json()['id']
        jane_id = jane_response.json()['id']
        
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': jane_id,
            'relationship_type': 'friend'
        }
        
        await test_client.post("/api/v1/relationships/", json=relationship_data)
        
        # Verify relationship exists
        john_rels_before = await test_client.get(f"/api/v1/relationships/contact/{john_id}")
        assert len(john_rels_before.json()) == 1
        
        # Delete relationship
        delete_response = await test_client.delete(f"/api/v1/relationships/{john_id}/{jane_id}")
        assert delete_response.status_code == 200
        
        # Verify relationship is deleted (both sides)
        john_rels_after = await test_client.get(f"/api/v1/relationships/contact/{john_id}")
        jane_rels_after = await test_client.get(f"/api/v1/relationships/contact/{jane_id}")
        
        assert len(john_rels_after.json()) == 0
        assert len(jane_rels_after.json()) == 0


class TestRelationshipAPIValidation:
    """Test API validation and error handling."""
    
    @pytest.mark.asyncio
    async def test_create_relationship_invalid_contacts(self, test_client):
        """Test creating relationship with non-existent contacts."""
        
        relationship_data = {
            'contact_a_id': 99999,  # Non-existent
            'contact_b_id': 99998,  # Non-existent
            'relationship_type': 'friend'
        }
        
        response = await test_client.post("/api/v1/relationships/", json=relationship_data)
        assert response.status_code == 400
        assert "not found" in response.json()['detail'].lower()
    
    @pytest.mark.asyncio
    async def test_create_self_relationship(self, test_client, sample_contacts):
        """Test that creating a relationship with self is prevented."""
        
        john_data = sample_contacts['john']
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        john_id = john_response.json()['id']
        
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': john_id,  # Same contact
            'relationship_type': 'friend'
        }
        
        response = await test_client.post("/api/v1/relationships/", json=relationship_data)
        assert response.status_code == 400
        assert "self" in response.json()['detail'].lower()
    
    @pytest.mark.asyncio
    async def test_create_duplicate_relationship(self, test_client, sample_contacts):
        """Test that duplicate relationships are prevented."""
        
        john_data = sample_contacts['john']
        jane_data = sample_contacts['jane']
        
        # Create contacts
        john_response = await test_client.post("/api/v1/contacts/", json=john_data)
        jane_response = await test_client.post("/api/v1/contacts/", json=jane_data)
        
        john_id = john_response.json()['id']
        jane_id = jane_response.json()['id']
        
        # Create first relationship
        relationship_data = {
            'contact_a_id': john_id,
            'contact_b_id': jane_id,
            'relationship_type': 'friend'
        }
        
        response1 = await test_client.post("/api/v1/relationships/", json=relationship_data)
        assert response1.status_code == 200
        
        # Try to create duplicate relationship
        response2 = await test_client.post("/api/v1/relationships/", json=relationship_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()['detail'].lower()


# Note: These tests require a full test environment with database setup.
# They serve as documentation and integration test templates.
# To run them, you would need:
# 1. Test database setup
# 2. FastAPI test client configuration  
# 3. Proper fixtures for authentication and tenant context
# 4. Database cleanup between tests