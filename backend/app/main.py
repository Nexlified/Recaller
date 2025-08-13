from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1.endpoints import auth
from app.core.config import settings
from app.db.session import SessionLocal
# Import minimal models for auth functionality
from app.db import base_minimal

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

# Add DB session middleware
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    # Set default tenant for all requests (preparing for future multi-tenant support)
    request.state.tenant_id = 1
    response = await call_next(request)
    request.state.db.close()
    return response

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Recaller API!",
        "documentation": f"/docs",
        "openapi": f"{settings.API_V1_STR}/openapi.json"
    }