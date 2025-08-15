"""
MCP Server Configuration Settings

This module defines the configuration settings for the MCP server,
including model backends, security settings, and integration points.
"""

from typing import List, Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum


class ModelBackendType(str, Enum):
    """Supported model backend types."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI_COMPATIBLE = "openai_compatible"
    LOCAL_TRANSFORMERS = "local_transformers"


class MCPServerSettings(BaseSettings):
    """MCP Server configuration settings."""
    
    # Server Configuration
    MCP_SERVER_HOST: str = Field(default="0.0.0.0", description="MCP server host")
    MCP_SERVER_PORT: int = Field(default=8001, description="MCP server port")
    MCP_PROTOCOL_VERSION: str = Field(default="1.0.0", description="MCP protocol version")
    
    # Security Configuration
    MCP_SECRET_KEY: str = Field(default="change-me-in-production-min-32-chars", description="Secret key for MCP server authentication")
    MCP_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="MCP access token expiration")
    MCP_ENABLE_TENANT_ISOLATION: bool = Field(default=True, description="Enable tenant isolation")
    
    # Backend Integration
    BACKEND_API_URL: str = Field(default="http://backend:8000", description="FastAPI backend URL")
    BACKEND_API_KEY: Optional[str] = Field(default=None, description="API key for backend communication")
    
    # Model Configuration
    DEFAULT_MODEL_BACKEND: ModelBackendType = Field(default=ModelBackendType.OLLAMA)
    MODEL_REGISTRY_PATH: str = Field(default="./models", description="Path to model registry")
    MAX_CONCURRENT_REQUESTS: int = Field(default=10, description="Maximum concurrent model requests")
    
    # Resource Limits
    MAX_CONTEXT_LENGTH: int = Field(default=4096, description="Maximum context length for models")
    MAX_RESPONSE_TOKENS: int = Field(default=1024, description="Maximum response tokens")
    REQUEST_TIMEOUT_SECONDS: int = Field(default=120, description="Request timeout in seconds")
    
    # Privacy and Security
    ENABLE_REQUEST_LOGGING: bool = Field(default=False, description="Enable request logging (privacy impact)")
    ANONYMIZE_LOGS: bool = Field(default=True, description="Anonymize sensitive data in logs")
    DATA_RETENTION_DAYS: int = Field(default=0, description="Data retention period (0 = no retention)")
    BLOCK_EXTERNAL_REQUESTS: bool = Field(default=True, description="Block external network requests for privacy")
    ALLOWED_EXTERNAL_HOSTS: List[str] = Field(default_factory=list, description="Whitelist of allowed external hosts")
    ENFORCE_LOCAL_ONLY: bool = Field(default=True, description="Enforce local-only processing")
    ANONYMIZE_ERROR_MESSAGES: bool = Field(default=True, description="Anonymize error messages to prevent data leakage")
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")
    MODEL_HEALTH_CHECK_ENABLED: bool = Field(default=True, description="Enable model health checks")
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = True


# Global settings instance
mcp_settings = MCPServerSettings()
