"""
Relationship mapping service for gender-specific relationship resolution.

This service handles automatic mapping of base relationship types (like 'sibling')
to specific types (like 'brother', 'sister') based on contact genders.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from app.schemas.contact_relationship import RelationshipMappingResult, RelationshipTypeOption


class RelationshipMappingService:
    """
    Service for handling gender-specific relationship mapping and validation.
    """
    
    def __init__(self):
        self.relationship_config = self._load_yaml_config()
        self.gender_mappings = self.relationship_config.get('gender_specific_relationships', {})
        self.relationship_types = self.relationship_config.get('relationship_types', [])
        self.categories = self.relationship_config.get('categories', [])
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load relationship mappings from YAML configuration file."""
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "relationship_mappings.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Fallback configuration if file is missing
            return self._get_fallback_config()
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing relationship mappings YAML: {e}")
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Fallback configuration if YAML file is not available."""
        return {
            'gender_specific_relationships': {
                'sibling': {
                    'mappings': {
                        'male_male': ['brother', 'brother'],
                        'male_female': ['brother', 'sister'],
                        'female_male': ['sister', 'brother'],
                        'female_female': ['sister', 'sister'],
                    },
                    'fallback': ['sibling', 'sibling']
                }
            },
            'relationship_types': [
                {'key': 'sibling', 'display_name': 'Sibling', 'category': 'family', 'is_gender_specific': True},
                {'key': 'brother', 'display_name': 'Brother', 'category': 'family', 'is_gender_specific': False},
                {'key': 'sister', 'display_name': 'Sister', 'category': 'family', 'is_gender_specific': False},
                {'key': 'friend', 'display_name': 'Friend', 'category': 'social', 'is_gender_specific': False},
            ],
            'categories': [
                {'key': 'family', 'display_name': 'Family'},
                {'key': 'social', 'display_name': 'Social'},
            ]
        }
    
    def determine_gender_specific_relationship(
        self, 
        base_relationship: str, 
        contact_a_gender: Optional[str], 
        contact_b_gender: Optional[str]
    ) -> RelationshipMappingResult:
        """
        Determine the specific relationship types based on genders.
        
        Args:
            base_relationship: Base relationship type (e.g., 'sibling', 'uncle_aunt')
            contact_a_gender: Gender of first contact
            contact_b_gender: Gender of second contact
            
        Returns:
            RelationshipMappingResult with resolved relationship types
        """
        # Check if this is a gender-specific relationship
        if base_relationship not in self.gender_mappings:
            # Not a gender-specific relationship, return as-is
            category = self._get_relationship_category(base_relationship)
            return RelationshipMappingResult(
                success=True,
                relationship_a_to_b=base_relationship,
                relationship_b_to_a=self._get_reverse_relationship(base_relationship),
                relationship_category=category,
                is_gender_resolved=False
            )
        
        mapping_config = self.gender_mappings[base_relationship]
        
        # If either gender is missing or non-binary/prefer_not_to_say, use fallback
        if not self._can_resolve_gender(contact_a_gender, contact_b_gender):
            fallback = mapping_config.get('fallback', [base_relationship, base_relationship])
            category = self._get_relationship_category(base_relationship)
            
            return RelationshipMappingResult(
                success=True,
                relationship_a_to_b=fallback[0],
                relationship_b_to_a=fallback[1],
                relationship_category=category,
                is_gender_resolved=False,
                original_relationship_type=base_relationship,
                validation_warnings=["Gender information insufficient for automatic resolution, using fallback"]
            )
        
        # Generate mapping key
        mapping_key = f"{contact_a_gender}_{contact_b_gender}"
        mappings = mapping_config.get('mappings', {})
        
        if mapping_key in mappings:
            resolved_types = mappings[mapping_key]
            category = self._get_relationship_category(base_relationship)
            
            return RelationshipMappingResult(
                success=True,
                relationship_a_to_b=resolved_types[0],
                relationship_b_to_a=resolved_types[1],
                relationship_category=category,
                is_gender_resolved=True,
                original_relationship_type=base_relationship
            )
        else:
            # Fallback if mapping not found
            fallback = mapping_config.get('fallback', [base_relationship, base_relationship])
            category = self._get_relationship_category(base_relationship)
            
            return RelationshipMappingResult(
                success=True,
                relationship_a_to_b=fallback[0],
                relationship_b_to_a=fallback[1],
                relationship_category=category,
                is_gender_resolved=False,
                original_relationship_type=base_relationship,
                validation_warnings=[f"No specific mapping found for {mapping_key}, using fallback"]
            )
    
    def _can_resolve_gender(self, gender_a: Optional[str], gender_b: Optional[str]) -> bool:
        """Check if genders can be used for automatic resolution."""
        valid_genders = {'male', 'female'}
        return (
            gender_a in valid_genders and 
            gender_b in valid_genders
        )
    
    def _get_relationship_category(self, relationship_type: str) -> str:
        """Get the category for a relationship type."""
        for rel_type in self.relationship_types:
            if rel_type.get('key') == relationship_type:
                return rel_type.get('category', 'unknown')
        return 'unknown'
    
    def _get_reverse_relationship(self, relationship_type: str) -> str:
        """Get the reverse relationship type."""
        for rel_type in self.relationship_types:
            if rel_type.get('key') == relationship_type:
                return rel_type.get('reverse', relationship_type)
        return relationship_type
    
    def get_relationship_options(self, include_gender_specific_base: bool = True) -> List[RelationshipTypeOption]:
        """
        Get available relationship options for UI selection.
        
        Args:
            include_gender_specific_base: Whether to include base types like 'sibling' 
                                        instead of specific types like 'brother', 'sister'
        
        Returns:
            List of relationship type options
        """
        options = []
        
        for rel_type in self.relationship_types:
            # Skip gender-specific variants if we're including base types
            if include_gender_specific_base and rel_type.get('gender_specific_of'):
                continue
            
            # Skip base types if we're not including them and they have specific variants
            if not include_gender_specific_base and rel_type.get('is_gender_specific'):
                continue
            
            options.append(RelationshipTypeOption(
                key=rel_type.get('key'),
                display_name=rel_type.get('display_name'),
                category=rel_type.get('category', 'unknown'),
                is_gender_specific=rel_type.get('is_gender_specific', False),
                description=rel_type.get('description')
            ))
        
        return sorted(options, key=lambda x: (x.category, x.display_name))
    
    def validate_gender_relationship(
        self, 
        relationship_type: str, 
        contact_a_gender: Optional[str], 
        contact_b_gender: Optional[str]
    ) -> RelationshipMappingResult:
        """
        Validate if the relationship type is appropriate for the genders.
        
        This can be used to warn users about potential mismatches.
        """
        # Find relationship type info
        rel_info = None
        for rel_type in self.relationship_types:
            if rel_type.get('key') == relationship_type:
                rel_info = rel_type
                break
        
        if not rel_info:
            return RelationshipMappingResult(
                success=False,
                relationship_a_to_b=relationship_type,
                relationship_b_to_a=relationship_type,
                relationship_category='unknown',
                is_gender_resolved=False,
                error_message=f"Unknown relationship type: {relationship_type}"
            )
        
        warnings = []
        
        # Check for gender-specific relationship issues
        if relationship_type in ['brother', 'sister'] and self._can_resolve_gender(contact_a_gender, contact_b_gender):
            expected_result = self.determine_gender_specific_relationship('sibling', contact_a_gender, contact_b_gender)
            if expected_result.success and expected_result.relationship_a_to_b != relationship_type:
                warnings.append(f"Gender suggests '{expected_result.relationship_a_to_b}' but '{relationship_type}' was selected")
        
        return RelationshipMappingResult(
            success=True,
            relationship_a_to_b=relationship_type,
            relationship_b_to_a=self._get_reverse_relationship(relationship_type),
            relationship_category=rel_info.get('category', 'unknown'),
            is_gender_resolved=False,
            validation_warnings=warnings if warnings else None
        )
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get available relationship categories."""
        return self.categories


# Global service instance
relationship_mapping_service = RelationshipMappingService()