"""
Tests for the relationship mapping service.
"""

import pytest
from app.services.relationship_mapping import RelationshipMappingService


class TestRelationshipMappingService:
    """Test the relationship mapping service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RelationshipMappingService()
    
    def test_sibling_gender_mapping_male_male(self):
        """Test sibling mapping for male-male relationship."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'male', 'male'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'brother'
        assert result.relationship_b_to_a == 'brother'
        assert result.is_gender_resolved is True
        assert result.original_relationship_type == 'sibling'
    
    def test_sibling_gender_mapping_male_female(self):
        """Test sibling mapping for male-female relationship."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'male', 'female'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'brother'
        assert result.relationship_b_to_a == 'sister'
        assert result.is_gender_resolved is True
        assert result.original_relationship_type == 'sibling'
    
    def test_sibling_gender_mapping_female_male(self):
        """Test sibling mapping for female-male relationship."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'female', 'male'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'sister'
        assert result.relationship_b_to_a == 'brother'
        assert result.is_gender_resolved is True
        assert result.original_relationship_type == 'sibling'
    
    def test_sibling_gender_mapping_female_female(self):
        """Test sibling mapping for female-female relationship."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'female', 'female'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'sister'
        assert result.relationship_b_to_a == 'sister'
        assert result.is_gender_resolved is True
        assert result.original_relationship_type == 'sibling'
    
    def test_sibling_fallback_missing_gender(self):
        """Test sibling mapping falls back when gender is missing."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', None, 'male'
        )
        
        assert result.success is True
        assert result.is_gender_resolved is False
        assert result.original_relationship_type == 'sibling'
        assert result.validation_warnings is not None
        assert len(result.validation_warnings) > 0
    
    def test_sibling_fallback_non_binary_gender(self):
        """Test sibling mapping falls back for non-binary genders."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'non_binary', 'female'
        )
        
        assert result.success is True
        assert result.is_gender_resolved is False
        assert result.original_relationship_type == 'sibling'
        assert result.validation_warnings is not None
    
    def test_sibling_fallback_prefer_not_to_say(self):
        """Test sibling mapping falls back for prefer_not_to_say."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'prefer_not_to_say', 'male'
        )
        
        assert result.success is True
        assert result.is_gender_resolved is False
        assert result.original_relationship_type == 'sibling'
    
    def test_non_gender_specific_relationship(self):
        """Test that non-gender-specific relationships pass through unchanged."""
        result = self.service.determine_gender_specific_relationship(
            'friend', 'male', 'female'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'friend'
        assert result.relationship_b_to_a == 'friend'  # Assuming friend is self-reversing
        assert result.is_gender_resolved is False
        assert result.original_relationship_type is None
    
    def test_uncle_aunt_mapping_male_uncle_male_child(self):
        """Test uncle/aunt mapping for male uncle with male child."""
        result = self.service.determine_gender_specific_relationship(
            'uncle_aunt', 'male', 'male'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'uncle'
        assert result.relationship_b_to_a == 'nephew'
        assert result.is_gender_resolved is True
        assert result.original_relationship_type == 'uncle_aunt'
    
    def test_uncle_aunt_mapping_female_aunt_female_child(self):
        """Test uncle/aunt mapping for female aunt with female child."""
        result = self.service.determine_gender_specific_relationship(
            'uncle_aunt', 'female', 'female'
        )
        
        assert result.success is True
        assert result.relationship_a_to_b == 'aunt'
        assert result.relationship_b_to_a == 'niece'
        assert result.is_gender_resolved is True
        assert result.original_relationship_type == 'uncle_aunt'
    
    def test_get_relationship_options_with_base_types(self):
        """Test getting relationship options including base types."""
        options = self.service.get_relationship_options(include_gender_specific_base=True)
        
        option_keys = [opt.key for opt in options]
        
        # Should include base types like 'sibling'
        assert 'sibling' in option_keys
        
        # Should not include specific variants when base is included
        assert 'brother' not in option_keys or 'sister' not in option_keys
    
    def test_get_relationship_options_without_base_types(self):
        """Test getting relationship options without base types."""
        options = self.service.get_relationship_options(include_gender_specific_base=False)
        
        option_keys = [opt.key for opt in options]
        
        # Should include specific types
        assert 'brother' in option_keys
        assert 'sister' in option_keys
        
        # Should not include base type
        assert 'sibling' not in option_keys
    
    def test_validate_gender_relationship_correct(self):
        """Test validation of correct gender-relationship combinations."""
        result = self.service.validate_gender_relationship(
            'brother', 'male', 'male'
        )
        
        assert result.success is True
        assert result.validation_warnings is None or len(result.validation_warnings) == 0
    
    def test_validate_gender_relationship_mismatch(self):
        """Test validation catches gender-relationship mismatches."""
        result = self.service.validate_gender_relationship(
            'sister', 'male', 'male'  # Both male but one labeled as sister
        )
        
        assert result.success is True
        assert result.validation_warnings is not None
        assert len(result.validation_warnings) > 0
    
    def test_validate_unknown_relationship_type(self):
        """Test validation of unknown relationship type."""
        result = self.service.validate_gender_relationship(
            'unknown_relationship', 'male', 'female'
        )
        
        assert result.success is False
        assert result.error_message is not None
        assert 'Unknown relationship type' in result.error_message
    
    def test_get_categories(self):
        """Test getting relationship categories."""
        categories = self.service.get_categories()
        
        assert len(categories) > 0
        assert any(cat.get('key') == 'family' for cat in categories)
        assert any(cat.get('key') == 'social' for cat in categories)


class TestRelationshipMappingEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RelationshipMappingService()
    
    def test_empty_gender_strings(self):
        """Test handling of empty gender strings."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', '', ''
        )
        
        assert result.success is True
        assert result.is_gender_resolved is False
    
    def test_invalid_gender_values(self):
        """Test handling of invalid gender values."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'invalid', 'also_invalid'
        )
        
        assert result.success is True
        assert result.is_gender_resolved is False
    
    def test_mixed_valid_invalid_genders(self):
        """Test handling of mixed valid and invalid genders."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'male', 'invalid'
        )
        
        assert result.success is True
        assert result.is_gender_resolved is False
    
    def test_case_sensitivity(self):
        """Test that gender values are case sensitive."""
        result = self.service.determine_gender_specific_relationship(
            'sibling', 'MALE', 'FEMALE'
        )
        
        # Should fall back because we expect lowercase
        assert result.success is True
        assert result.is_gender_resolved is False