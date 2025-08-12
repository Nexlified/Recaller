from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, analytics, social_groups, social_group_activities

api_router = APIRouter()
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(social_groups.router, prefix="/social-groups", tags=["social-groups"])
api_router.include_router(social_group_activities.router, prefix="/social-groups", tags=["social-group-activities"])
