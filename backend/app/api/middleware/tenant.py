from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app.crud.tenant import get_tenant_by_slug

class TenantMiddleware:
    async def __call__(self, request: Request, call_next):
        tenant_slug = request.headers.get("X-Tenant-ID", "default")
        
        # Get DB session
        db: Session = request.state.db
        
        # Get tenant
        tenant = get_tenant_by_slug(db, tenant_slug)
        if not tenant:
            tenant = get_tenant_by_slug(db, "default")
        
        # Store tenant in request state
        request.state.tenant = tenant
        
        response = await call_next(request)
        return response
