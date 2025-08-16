import os
import re
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, validator, Field
from pydantic_settings import BaseSettings
import yaml

class EnvironmentConfigLoader:
    """Load and process environment configuration from YAML files"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config_root = Path(__file__).parent.parent.parent.parent / "config"
        self.env_config_path = self.config_root / "environment" / f"{environment}.yml"
        self._config_cache = {}
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML with environment variable substitution"""
        if self.environment in self._config_cache:
            return self._config_cache[self.environment]
        
        if not self.env_config_path.exists():
            raise FileNotFoundError(f"Environment config not found: {self.env_config_path}")
        
        with open(self.env_config_path, 'r') as file:
            raw_config = yaml.safe_load(file)
        
        # Process environment variable substitutions
        processed_config = self._process_env_vars(raw_config)
        self._config_cache[self.environment] = processed_config
        
        return processed_config
    
    def _process_env_vars(self, config: Any) -> Any:
        """Recursively process environment variable substitutions"""
        if isinstance(config, dict):
            return {key: self._process_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str):
            return self._substitute_env_var(config)
        else:
            return config
    
    def _substitute_env_var(self, value: str) -> Any:
        """Substitute environment variables in string values"""
        # Pattern: ${VAR_NAME:default_value} or ${VAR_NAME}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_match(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            env_value = os.getenv(var_name, default_value)
            return env_value
        
        # If the entire string is a single environment variable, preserve type conversion
        if re.match(r'^\$\{[^}]+\}$', value):
            result = re.sub(pattern, replace_match, value)
            # Try to convert to appropriate type
            if result.lower() in ('true', 'false'):
                return result.lower() == 'true'
            try:
                if '.' in result:
                    return float(result)
                return int(result)
            except ValueError:
                return result
        else:
            # Multiple substitutions or mixed content, return as string
            return re.sub(pattern, replace_match, value)
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._config_cache.clear()

class EnhancedSettings(BaseSettings):
    """Enhanced settings class with YAML configuration support"""
    
    # Environment detection
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "recaller"
    POSTGRES_PORT: int = 5432
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DATABASE_URI: Optional[str] = None
    
    # Security Configuration
    SECRET_KEY: str = "_FZtjmrehpEpICV9lVqTP6v2E4UNO9XBSn21rX6e7sI"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # Application Configuration
    PROJECT_NAME: str = "Recaller"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    CORS_ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_ALLOWED_HEADERS: str = "Content-Type,Authorization,X-Tenant-ID"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_FROM_EMAIL: str = "noreply@recaller.com"
    
    # Feature Flags
    ENABLE_HOT_RELOAD: bool = True
    DEBUG_TOOLBAR: bool = False
    METRICS_ENABLED: bool = True
    RATE_LIMITING: bool = True
    
    # Storage Configuration
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf,txt"
    
    # Gift System Configuration
    GIFT_SYSTEM_ENABLED: bool = True
    GIFT_DEFAULT_CURRENCY: str = "USD"
    GIFT_MAX_BUDGET: int = 10000
    GIFT_SUGGESTION_ENGINE: str = "basic"
    GIFT_REMINDER_DAYS: str = "7,3,1"
    GIFT_AUTO_CREATE_TASKS: bool = True
    GIFT_PRIVACY_MODE: str = "personal"
    GIFT_IMAGE_STORAGE: bool = True
    GIFT_EXTERNAL_LINKS: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_yaml_config()
    
    def _load_yaml_config(self):
        """Load and apply YAML configuration"""
        try:
            config_loader = EnvironmentConfigLoader(self.ENVIRONMENT)
            yaml_config = config_loader.load_config()
            
            # Apply YAML configuration
            self._apply_yaml_config(yaml_config)
            
        except FileNotFoundError:
            # Fall back to environment variables only
            pass
    
    def _apply_yaml_config(self, yaml_config: Dict[str, Any]):
        """Apply YAML configuration to settings"""
        # Map YAML structure to settings attributes
        mappings = {
            ('database', 'host'): 'POSTGRES_SERVER',
            ('database', 'port'): 'POSTGRES_PORT',
            ('database', 'user'): 'POSTGRES_USER',
            ('database', 'password'): 'POSTGRES_PASSWORD',
            ('database', 'name'): 'POSTGRES_DB',
            ('database', 'pool_size'): 'DB_POOL_SIZE',
            ('database', 'max_overflow'): 'DB_MAX_OVERFLOW',
            ('database', 'pool_timeout'): 'DB_POOL_TIMEOUT',
            
            ('security', 'secret_key'): 'SECRET_KEY',
            ('security', 'access_token_expire_minutes'): 'ACCESS_TOKEN_EXPIRE_MINUTES',
            ('security', 'jwt_algorithm'): 'JWT_ALGORITHM',
            
            ('redis', 'url'): 'REDIS_URL',
            ('redis', 'cache_ttl'): 'REDIS_CACHE_TTL',
            ('redis', 'max_connections'): 'REDIS_MAX_CONNECTIONS',
            
            ('celery', 'broker_url'): 'CELERY_BROKER_URL',
            ('celery', 'result_backend'): 'CELERY_RESULT_BACKEND',
            ('celery', 'task_always_eager'): 'CELERY_TASK_ALWAYS_EAGER',
            
            ('application', 'project_name'): 'PROJECT_NAME',
            ('application', 'version'): 'VERSION',
            ('application', 'api_v1_str'): 'API_V1_STR',
            ('application', 'debug_mode'): 'DEBUG',
            ('application', 'log_level'): 'LOG_LEVEL',
            
            ('cors', 'allowed_origins'): 'CORS_ALLOWED_ORIGINS',
            ('cors', 'allowed_methods'): 'CORS_ALLOWED_METHODS',
            ('cors', 'allowed_headers'): 'CORS_ALLOWED_HEADERS',
            ('cors', 'allow_credentials'): 'CORS_ALLOW_CREDENTIALS',
            
            ('email', 'smtp_host'): 'SMTP_HOST',
            ('email', 'smtp_port'): 'SMTP_PORT',
            ('email', 'smtp_username'): 'SMTP_USERNAME',
            ('email', 'smtp_password'): 'SMTP_PASSWORD',
            ('email', 'smtp_tls'): 'SMTP_TLS',
            ('email', 'from_email'): 'SMTP_FROM_EMAIL',
            
            ('features', 'hot_reload'): 'ENABLE_HOT_RELOAD',
            ('features', 'debug_toolbar'): 'DEBUG_TOOLBAR',
            ('features', 'metrics_enabled'): 'METRICS_ENABLED',
            ('features', 'rate_limiting'): 'RATE_LIMITING',
            
            ('storage', 'upload_dir'): 'UPLOAD_DIR',
            ('storage', 'max_file_size'): 'MAX_FILE_SIZE',
            ('storage', 'allowed_extensions'): 'ALLOWED_EXTENSIONS',
            
            # Gift System mappings
            ('gift_system', 'enabled'): 'GIFT_SYSTEM_ENABLED',
            ('gift_system', 'default_budget_currency'): 'GIFT_DEFAULT_CURRENCY',
            ('gift_system', 'max_budget_amount'): 'GIFT_MAX_BUDGET',
            ('gift_system', 'suggestion_engine'): 'GIFT_SUGGESTION_ENGINE',
            ('gift_system', 'reminder_advance_days'): 'GIFT_REMINDER_DAYS',
            ('gift_system', 'auto_create_tasks'): 'GIFT_AUTO_CREATE_TASKS',
            ('gift_system', 'privacy_mode'): 'GIFT_PRIVACY_MODE',
            ('gift_system', 'image_storage_enabled'): 'GIFT_IMAGE_STORAGE',
            ('gift_system', 'external_links_enabled'): 'GIFT_EXTERNAL_LINKS',
        }
        
        for (section, key), attr_name in mappings.items():
            if section in yaml_config and key in yaml_config[section]:
                value = yaml_config[section][key]
                if hasattr(self, attr_name):
                    setattr(self, attr_name, value)
    
    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        from sqlalchemy.engine.url import URL
        return str(URL.create(
            drivername="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT", 5432),
            database=values.get("POSTGRES_DB")
        ))
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY with same logic as original"""
        if not isinstance(v, str):
            raise ValueError("SECRET_KEY must be a string")
        
        # Check for known weak defaults
        weak_defaults = {
            "your-secret-key", "your-secret-key-change-in-production",
            "secret", "secret-key", "development-secret", "dev-secret",
            "test-secret", "default-secret", "change-me", "changeme"
        }
        
        if v.lower() in weak_defaults:
            raise ValueError(
                f"SECRET_KEY cannot be a default/weak value: '{v}'. "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters long for security. "
                f"Current length: {len(v)}. "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        return v
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS allowed origins from comma-separated string"""
        if self.CORS_ALLOWED_ORIGINS:
            return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]
        return ["http://localhost:3000"]
    
    def get_cors_methods(self) -> List[str]:
        """Parse CORS allowed methods from comma-separated string"""
        if self.CORS_ALLOWED_METHODS:
            return [method.strip() for method in self.CORS_ALLOWED_METHODS.split(",") if method.strip()]
        return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    def get_cors_headers(self) -> List[str]:
        """Parse CORS allowed headers from comma-separated string"""
        if self.CORS_ALLOWED_HEADERS:
            return [header.strip() for header in self.CORS_ALLOWED_HEADERS.split(",") if header.strip()]
        return ["Content-Type", "Authorization", "X-Tenant-ID"]
    
    def get_gift_reminder_days(self) -> List[int]:
        """Parse gift reminder advance days from comma-separated string"""
        if self.GIFT_REMINDER_DAYS:
            try:
                return [int(day.strip()) for day in self.GIFT_REMINDER_DAYS.split(",") if day.strip().isdigit()]
            except ValueError:
                return [7, 3, 1]  # Default fallback
        return [7, 3, 1]
    
    def is_gift_system_enabled(self) -> bool:
        """Check if gift system is enabled"""
        return self.GIFT_SYSTEM_ENABLED
    
    def get_gift_allowed_extensions(self) -> List[str]:
        """Get allowed extensions for gift images based on general file settings"""
        if self.GIFT_IMAGE_STORAGE:
            extensions = self.ALLOWED_EXTENSIONS.split(",")
            # Filter to image types only for gifts
            image_extensions = [ext.strip() for ext in extensions if ext.strip().lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']]
            return image_extensions if image_extensions else ['jpg', 'jpeg', 'png']
        return []
    
    def reload_config(self):
        """Reload configuration from YAML (for hot reload)"""
        if self.ENABLE_HOT_RELOAD:
            config_loader = EnvironmentConfigLoader(self.ENVIRONMENT)
            config_loader.clear_cache()
            yaml_config = config_loader.load_config()
            self._apply_yaml_config(yaml_config)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Global instance with hot reload support
_settings_instance = None

def get_settings(reload: bool = False) -> EnhancedSettings:
    """Get settings instance with optional reload"""
    global _settings_instance
    
    if _settings_instance is None or reload:
        _settings_instance = EnhancedSettings()
    elif reload and _settings_instance.ENABLE_HOT_RELOAD:
        _settings_instance.reload_config()
    
    return _settings_instance

# Backward compatibility
settings = get_settings()