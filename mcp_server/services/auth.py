"""
Authentication and authorization service for MCP server.

This module provides authentication, tenant isolation, and access control
for the MCP server, integrating with the main Recaller backend.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
import httpx
from datetime import datetime

from ..config.settings import mcp_settings
from ..core.protocol import MCPProtocolError, MCPErrorCodes


logger = logging.getLogger(__name__)


class TenantInfo:
    """Tenant information model."""
    
    def __init__(self, id: str, slug: str, name: str, active: bool = True):
        self.id = id
        self.slug = slug
        self.name = name
        self.active = active


class AuthService:
    """
    Authentication and authorization service.
    
    Handles tenant verification, API access control, and integration
    with the main Recaller backend for authentication.
    """
    
    def __init__(self):
        self._backend_client = None
        self._tenant_cache: Dict[str, TenantInfo] = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_update: Dict[str, datetime] = {}
    
    async def get_backend_client(self) -> httpx.AsyncClient:
        """Get HTTP client for backend communication."""
        if not self._backend_client:
            headers = {"Content-Type": "application/json"}
            if mcp_settings.BACKEND_API_KEY:
                headers["Authorization"] = f"Bearer {mcp_settings.BACKEND_API_KEY}"
            
            self._backend_client = httpx.AsyncClient(
                base_url=mcp_settings.BACKEND_API_URL,
                headers=headers
            )
        return self._backend_client
    
    async def verify_tenant_access(self, tenant_id: str, user_token: Optional[str] = None) -> TenantInfo:
        """
        Verify tenant access and return tenant information.
        
        Args:
            tenant_id: Tenant ID or slug
            user_token: Optional user authentication token
            
        Returns:
            Tenant information
            
        Raises:
            MCPProtocolError: If tenant access is denied
        """
        try:
            # Check cache first
            if self._is_cached_valid(tenant_id):
                return self._tenant_cache[tenant_id]
            
            # Query backend for tenant information
            client = await self.get_backend_client()
            
            # Use the same tenant verification logic as the main backend
            headers = {"X-Tenant-ID": tenant_id}
            if user_token:
                headers["Authorization"] = f"Bearer {user_token}"
            
            try:
                response = await client.get("/api/v1/config/tenant-info", headers=headers)
            except Exception as e:
                logger.warning(f"Failed to connect to backend for tenant verification: {e}")
                # In development mode, create a default tenant when backend is unavailable
                if tenant_id == "default":
                    tenant_info = TenantInfo(
                        id="default",
                        slug="default",
                        name="Default Tenant",
                        active=True
                    )
                    self._tenant_cache[tenant_id] = tenant_info
                    self._last_cache_update[tenant_id] = datetime.utcnow()
                    return tenant_info
                else:
                    raise MCPProtocolError(
                        code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                        message="Backend unavailable for tenant verification"
                    )
            
            if response.status_code == 404:
                # Try default tenant
                if tenant_id != "default":
                    return await self.verify_tenant_access("default", user_token)
                else:
                    raise MCPProtocolError(
                        code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                        message="Default tenant not found"
                    )
            
            if response.status_code == 403:
                raise MCPProtocolError(
                    code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                    message="Tenant access denied"
                )
            
            response.raise_for_status()
            tenant_data = response.json()
            
            # Create tenant info
            tenant_info = TenantInfo(
                id=tenant_data.get("id", tenant_id),
                slug=tenant_data.get("slug", tenant_id),
                name=tenant_data.get("name", tenant_id),
                active=tenant_data.get("active", True)
            )
            
            # Cache the result
            self._tenant_cache[tenant_id] = tenant_info
            self._last_cache_update[tenant_id] = datetime.utcnow()
            
            return tenant_info
            
        except MCPProtocolError:
            raise
        except Exception as e:
            logger.error(f"Failed to verify tenant access for {tenant_id}: {e}")
            
            # Try to use default tenant as fallback
            if tenant_id != "default":
                try:
                    return await self.verify_tenant_access("default", user_token)
                except:
                    pass
            
            raise MCPProtocolError(
                code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                message="Failed to verify tenant access"
            )
    
    async def verify_api_access(self, request: Request, tenant_info: TenantInfo) -> bool:
        """
        Verify API access permissions for the request.
        
        Args:
            request: HTTP request
            tenant_info: Tenant information
            
        Returns:
            True if access is allowed
        """
        # Check if tenant is active
        if not tenant_info.active:
            raise MCPProtocolError(
                code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                message="Tenant is not active"
            )
        
        # Add additional access control logic here as needed
        # For example, checking API rate limits, feature flags, etc.
        
        return True
    
    def _is_cached_valid(self, tenant_id: str) -> bool:
        """Check if cached tenant info is still valid."""
        if tenant_id not in self._tenant_cache:
            return False
        
        last_update = self._last_cache_update.get(tenant_id)
        if not last_update:
            return False
        
        age = (datetime.utcnow() - last_update).total_seconds()
        return age < self._cache_ttl
    
    async def cleanup(self):
        """Cleanup resources."""
        if self._backend_client:
            await self._backend_client.aclose()


# Global auth service instance
auth_service = AuthService()


# FastAPI dependencies
async def get_current_tenant(request: Request) -> Optional[TenantInfo]:
    """
    FastAPI dependency to get current tenant from request.
    
    Extracts tenant information from X-Tenant-ID header and verifies access.
    """
    if not mcp_settings.MCP_ENABLE_TENANT_ISOLATION:
        # If tenant isolation is disabled, return None
        return None
    
    # Get tenant ID from header
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    
    # Get user token if available
    auth_header = request.headers.get("Authorization")
    user_token = None
    if auth_header and auth_header.startswith("Bearer "):
        user_token = auth_header[7:]
    
    try:
        tenant_info = await auth_service.verify_tenant_access(tenant_id, user_token)
        return tenant_info
    except MCPProtocolError as e:
        raise HTTPException(status_code=403, detail=e.message)


async def verify_api_access(
    request: Request,
    current_tenant: Optional[TenantInfo] = Depends(get_current_tenant)
) -> bool:
    """
    FastAPI dependency to verify API access.
    
    Performs additional access control checks beyond tenant verification.
    """
    if not current_tenant and mcp_settings.MCP_ENABLE_TENANT_ISOLATION:
        raise HTTPException(status_code=403, detail="Tenant access required")
    
    try:
        if current_tenant:
            await auth_service.verify_api_access(request, current_tenant)
        return True
    except MCPProtocolError as e:
        raise HTTPException(status_code=403, detail=e.message)