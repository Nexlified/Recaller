from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, organizations

api_router = APIRouter()
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
