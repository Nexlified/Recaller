from app.core.configuration_manager import config_manager
from typing import Dict, Any, Optional, List, Tuple
from app.schemas.contact_relationship import RelationshipMappingResult, RelationshipTypeOption

class RelationshipMappingService:
    """Service for managing contact relationship mappings"""
    
    def __init__(self):
        self.manager = config_manager
        self._relationship_config = None
    
    @property
    def relationship_config(self) -> Dict[str, Any]:
        """Lazy load relationship configuration"""
        if self._relationship_config is None:
            self._relationship_config = self.manager.get_config('relationship_mappings')
        return self._relationship_config
    
    def get_gender_specific_mapping(self, relationship: str, from_gender: str, to_gender: str) -> Tuple[str, str]:
        """Get gender-specific relationship mapping"""
        gender_mappings = self.relationship_config.get('gender_specific_relationships', {})
        
        if relationship not in gender_mappings:
            return relationship, relationship
        
        mapping_key = f"{from_gender}_{to_gender}"
        mappings = gender_mappings[relationship].get('mappings', {})
        
        if mapping_key in mappings:
            return tuple(mappings[mapping_key])
        
        # Return fallback
        fallback = gender_mappings[relationship].get('fallback', [relationship, relationship])
        return tuple(fallback)
    
    def get_bidirectional_relationship(self, relationship_type: str) -> str:
        """Get the reverse relationship type"""
        relationships = self.relationship_config.get('relationship_types', [])
        
        for rel in relationships:
            if rel.get('key') == relationship_type:
                return rel.get('reverse', relationship_type)
        
        return relationship_type
    
    def get_relationship_categories(self) -> List[Dict[str, Any]]:
        """Get all relationship categories"""
        return self.relationship_config.get('categories', [])
    
    def validate_relationship_type(self, relationship_type: str) -> bool:
        """Validate if relationship type exists"""
        relationships = self.relationship_config.get('relationship_types', [])
        return any(rel.get('key') == relationship_type for rel in relationships)
    
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
        gender_mappings = self.relationship_config.get('gender_specific_relationships', {})
        if base_relationship not in gender_mappings:
            # Not a gender-specific relationship, return as-is
            category = self._get_relationship_category(base_relationship)
            return RelationshipMappingResult(
                success=True,
                relationship_a_to_b=base_relationship,
                relationship_b_to_a=self._get_reverse_relationship(base_relationship),
                relationship_category=category,
                is_gender_resolved=False
            )
        
        mapping_config = gender_mappings[base_relationship]
        
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
        relationships = self.relationship_config.get('relationship_types', [])
        for rel_type in relationships:
            if rel_type.get('key') == relationship_type:
                return rel_type.get('category', 'unknown')
        return 'unknown'
    
    def _get_reverse_relationship(self, relationship_type: str) -> str:
        """Get the reverse relationship type."""
        relationships = self.relationship_config.get('relationship_types', [])
        for rel_type in relationships:
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
        relationships = self.relationship_config.get('relationship_types', [])
        
        for rel_type in relationships:
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
        relationships = self.relationship_config.get('relationship_types', [])
        rel_info = None
        for rel_type in relationships:
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
        return self.relationship_config.get('categories', [])


# Global service instance
relationship_mapping_service = RelationshipMappingService()