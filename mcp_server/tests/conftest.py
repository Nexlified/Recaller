"""
Test configuration and fixtures for MCP server tests.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.auth import TenantInfo
from models.registry import model_registry
from services.inference import inference_service
from services.privacy import privacy_enforcer
from config.settings import mcp_settings


@pytest.fixture
def event_loop() -> Generator:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_tenant_1() -> TenantInfo:
    """Create a mock tenant for testing."""
    return TenantInfo(
        id="tenant-1",
        slug="tenant-1",
        name="Test Tenant 1",
        active=True
    )


@pytest.fixture
def mock_tenant_2() -> TenantInfo:
    """Create a second mock tenant for testing."""
    return TenantInfo(
        id="tenant-2", 
        slug="tenant-2",
        name="Test Tenant 2",
        active=True
    )


@pytest.fixture
def mock_inactive_tenant() -> TenantInfo:
    """Create an inactive tenant for testing."""
    return TenantInfo(
        id="inactive-tenant",
        slug="inactive-tenant",
        name="Inactive Tenant",
        active=False
    )


@pytest.fixture
async def clean_model_registry():
    """Clean model registry before and after tests."""
    # Clear any existing models
    original_models = model_registry._models.copy()
    original_backends = model_registry._backends.copy()
    
    model_registry._models.clear()
    model_registry._backends.clear()
    
    yield model_registry
    
    # Restore original state
    model_registry._models = original_models
    model_registry._backends = original_backends


@pytest.fixture
def mock_model_backend():
    """Create a mock model backend for testing."""
    backend = MagicMock()
    backend.model_id = "test-model"
    backend.status = "available"
    backend.initialize = AsyncMock()
    backend.health_check = AsyncMock(return_value=True)
    backend.shutdown = AsyncMock()
    backend.get_capabilities = MagicMock(return_value=["completion", "chat"])
    return backend


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset MCP settings to defaults for each test."""
    # Store original values
    original_tenant_isolation = mcp_settings.MCP_ENABLE_TENANT_ISOLATION
    original_block_external = mcp_settings.BLOCK_EXTERNAL_REQUESTS
    original_enforce_local = mcp_settings.ENFORCE_LOCAL_ONLY
    original_anonymize_logs = mcp_settings.ANONYMIZE_LOGS
    original_anonymize_errors = mcp_settings.ANONYMIZE_ERROR_MESSAGES
    
    # Set test defaults
    mcp_settings.MCP_ENABLE_TENANT_ISOLATION = True
    mcp_settings.BLOCK_EXTERNAL_REQUESTS = True
    mcp_settings.ENFORCE_LOCAL_ONLY = True
    mcp_settings.ANONYMIZE_LOGS = True
    mcp_settings.ANONYMIZE_ERROR_MESSAGES = True
    
    yield
    
    # Restore original values
    mcp_settings.MCP_ENABLE_TENANT_ISOLATION = original_tenant_isolation
    mcp_settings.BLOCK_EXTERNAL_REQUESTS = original_block_external
    mcp_settings.ENFORCE_LOCAL_ONLY = original_enforce_local
    mcp_settings.ANONYMIZE_LOGS = original_anonymize_logs
    mcp_settings.ANONYMIZE_ERROR_MESSAGES = original_anonymize_errors