from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import SessionLocal
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Combined DB session and tenant middleware
@app.middleware("http")
async def db_and_tenant_middleware(request: Request, call_next):
    # First set up DB session
    request.state.db = SessionLocal()
    
    # Then set up tenant
    tenant_slug = request.headers.get("X-Tenant-ID", "default")
    
    # Get tenant using the database session
    from app.crud.tenant import get_tenant_by_slug
    tenant = get_tenant_by_slug(request.state.db, tenant_slug)
    if not tenant:
        tenant = get_tenant_by_slug(request.state.db, "default")
    
    # Store tenant in request state
    request.state.tenant = tenant
    
    # Process request
    response = await call_next(request)
    
    # Clean up DB session
    request.state.db.close()
    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Recaller API!",
        "documentation": f"/docs",
        "openapi": f"{settings.API_V1_STR}/openapi.json"
    }