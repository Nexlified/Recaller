import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

class ActivityConfigService:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent.parent.parent / "config"
    
    @lru_cache(maxsize=10)
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_file = self.config_path / f"{config_name}.yml"
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    
    def get_activity_types(self) -> Dict[str, Any]:
        """Get activity types configuration"""
        return self.load_config('activity_types')
    
    def get_activity_templates(self) -> Dict[str, Any]:
        """Get activity templates configuration"""
        return self.load_config('activity_templates')
    
    def get_recommendations_config(self) -> Dict[str, Any]:
        """Get recommendation engine configuration"""
        return self.load_config('activity_recommendations')
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.load_config('activity_system')
    
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