from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.api.v1.api import api_router
from app.services.task_scheduler import task_scheduler_service
from app.api.middleware.rate_limit import rate_limit_middleware
from app.api.middleware.request_validation import request_validation_middleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request validation middleware (before rate limiting)
app.middleware("http")(request_validation_middleware)

# Add rate limiting middleware 
app.middleware("http")(rate_limit_middleware)

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


@app.on_event("startup")
async def startup_event():
    """Start services when the application starts."""
    try:
        # Initialize Redis connection
        redis_client.connect()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Warning: Could not connect to Redis: {e}")
    
    try:
        # Start the task scheduler
        task_scheduler_service.start()
    except Exception as e:
        print(f"Warning: Could not start task scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop services when the application shuts down."""
    try:
        # Disconnect Redis
        redis_client.disconnect()
        print("Redis disconnected")
    except Exception as e:
        print(f"Warning: Could not disconnect Redis: {e}")
        
    try:
        # Stop the task scheduler
        task_scheduler_service.stop()
    except Exception as e:
        print(f"Warning: Could not stop task scheduler: {e}")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Recaller API!",
        "documentation": f"/docs",
        "openapi": f"{settings.API_V1_STR}/openapi.json"
    }


@app.get("/health")
def health_check():
    """Health check endpoint that includes Redis connectivity."""
    health_status = {
        "status": "ok",
        "services": {
            "api": "healthy"
        }
    }
    
    # Check Redis connection
    try:
        if redis_client.is_connected():
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status