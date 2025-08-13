from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, contacts, events, analytics, organizations, social_groups, social_group_activities, configuration, tasks, task_scheduler

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(social_groups.router, prefix="/social-groups", tags=["Social Groups"])
api_router.include_router(social_group_activities.router, prefix="/social-groups", tags=["Social Group Activities"])
api_router.include_router(configuration.router, prefix="/config", tags=["Configuration"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(task_scheduler.router, prefix="/task-scheduler", tags=["Task Scheduler"])
