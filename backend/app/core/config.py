from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recaller"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "recaller"
    POSTGRES_PORT: int = 5432
    DATABASE_URI: Optional[str] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        url = PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", 5432)),
            path=f"{values.get('POSTGRES_DB') or ''}"
        )
        return str(url)

    # JWT Configuration
    SECRET_KEY: str = "_FZtjmrehpEpICV9lVqTP6v2E4UNO9XBSn21rX6e7sI"  # Strong default, override in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY for production security requirements."""
        if not isinstance(v, str):
            raise ValueError("SECRET_KEY must be a string")
        
        # Check for known weak defaults first (regardless of length)
        weak_defaults = {
            "your-secret-key",
            "your-secret-key-change-in-production",
            "secret",
            "secret-key",
            "development-secret",
            "dev-secret",
            "test-secret",
            "default-secret",
            "change-me",
            "changeme",
        }
        
        if v.lower() in weak_defaults:
            raise ValueError(
                f"SECRET_KEY cannot be a default/weak value: '{v}'. "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        # Check for simple patterns that indicate weak secrets (regardless of length)
        normalized = v.lower().replace("-", "").replace("_", "").replace(" ", "")
        weak_patterns = [
            "yoursecretkey", "secretkey", "mysecret", "password", "admin"
        ]
        
        # Check if any weak pattern matches the beginning or makes up significant portion
        for pattern in weak_patterns:
            if (normalized.startswith(pattern) or 
                normalized == pattern or
                (len(pattern) >= 6 and pattern in normalized and len(pattern) / len(normalized) > 0.3)):
                raise ValueError(
                    f"SECRET_KEY appears to be a weak/predictable value. "
                    f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
        
        # Check minimum length
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters long for security. "
                f"Current length: {len(v)}. "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        # Check for predictable patterns (all same character, all numbers, etc.)
        if len(set(v)) <= 4:  # Too few unique characters
            raise ValueError(
                f"SECRET_KEY appears to be too predictable (too few unique characters). "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        if v.isdigit():  # All numbers
            raise ValueError(
                f"SECRET_KEY cannot be all numbers. "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        if v.isalpha():  # All letters
            raise ValueError(
                f"SECRET_KEY cannot be all letters. "
                f"Generate a strong secret with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        return v
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    CORS_ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_ALLOWED_HEADERS: str = "Content-Type,Authorization,X-Tenant-ID"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Email Configuration (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_FROM_EMAIL: str = "noreply@recaller.com"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS allowed origins from comma-separated string."""
        if self.CORS_ALLOWED_ORIGINS:
            return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]
        return ["http://localhost:3000"]
    
    def get_cors_methods(self) -> List[str]:
        """Parse CORS allowed methods from comma-separated string."""
        if self.CORS_ALLOWED_METHODS:
            return [method.strip() for method in self.CORS_ALLOWED_METHODS.split(",") if method.strip()]
        return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    def get_cors_headers(self) -> List[str]:
        """Parse CORS allowed headers from comma-separated string."""
        if self.CORS_ALLOWED_HEADERS:
            return [header.strip() for header in self.CORS_ALLOWED_HEADERS.split(",") if header.strip()]
        return ["Content-Type", "Authorization", "X-Tenant-ID"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
