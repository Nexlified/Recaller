from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, social_groups, social_group_activities, config

api_router = APIRouter()
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(social_groups.router, prefix="/social-groups", tags=["social-groups"])
api_router.include_router(social_group_activities.router, prefix="/social-groups", tags=["social-group-activities"])
api_router.include_router(config.router, prefix="/config", tags=["configuration"])
