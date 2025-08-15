from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, contacts, contact_relationships, family_information, events, analytics, organizations, social_groups, 
    social_group_activities, configuration, tasks, task_scheduler, contact_work_experience,
    transactions_simple, background_tasks, journal, currencies, personal_debts, activity_config, config_manager
)

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(contact_relationships.router, prefix="/relationships", tags=["Contact Relationships"])
api_router.include_router(contact_work_experience.router, prefix="/work-experience", tags=["Work Experience"])
api_router.include_router(family_information.router, prefix="/family", tags=["Family Information"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(task_scheduler.router, prefix="/task-scheduler", tags=["Task Scheduler"])
api_router.include_router(transactions_simple.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(currencies.router, prefix="/currencies", tags=["Currencies"])
api_router.include_router(personal_debts.router, prefix="/personal-debts", tags=["Personal Debts"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organization Management"])
api_router.include_router(social_groups.router, prefix="/social-groups", tags=["Social Groups"])
api_router.include_router(social_group_activities.router, prefix="/social-groups", tags=["Social Group Activities"])
api_router.include_router(journal.router, prefix="/journal", tags=["Journal"])
api_router.include_router(configuration.router, prefix="/config", tags=["Configuration"])
api_router.include_router(config_manager.router, prefix="/config-manager", tags=["Configuration Manager"])
api_router.include_router(activity_config.router, prefix="/activity-config", tags=["Activity Configuration"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


api_router.include_router(background_tasks.router, prefix="/background-tasks", tags=["Background Tasks"])
