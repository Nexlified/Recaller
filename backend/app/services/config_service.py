from app.core.configuration_manager import config_manager
from typing import Dict, Any, Optional

class ActivityConfigService:
    """Activity-specific configuration service using centralized manager"""
    
    def __init__(self):
        self.manager = config_manager
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration from YAML file using centralized manager"""
        return self.manager.get_config(config_name)
    
    def get_activity_types(self) -> Dict[str, Any]:
        """Get activity types configuration"""
        return self.manager.get_config('activity_types')
    
    def get_activity_templates(self) -> Dict[str, Any]:
        """Get activity templates configuration"""
        return self.manager.get_config('activity_templates')
    
    def get_recommendations_config(self) -> Dict[str, Any]:
        """Get recommendation engine configuration"""
        return self.manager.get_config('activity_recommendations')
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.manager.get_config('activity_system')
    
    def get_activity_type_info(self, activity_type: str) -> Optional[Dict[str, Any]]:
        """Get specific activity type information"""
        config = self.get_activity_types()
        return config.get('activity_types', {}).get(activity_type)
    
    def get_quality_scale(self) -> Dict[str, Any]:
        """Get quality rating scale"""
        config = self.get_activity_types()
        return config.get('quality_scale', {})
    
    def validate_activity_type(self, activity_type: str) -> bool:
        """Validate if activity type exists"""
        config = self.get_activity_types()
        return activity_type in config.get('activity_types', {})

# Global instance
activity_config = ActivityConfigService()