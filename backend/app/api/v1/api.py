from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, contacts, contact_intelligence, contact_followup, organizations

api_router = APIRouter()
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(contact_intelligence.router, prefix="/contacts", tags=["contact-intelligence"])
api_router.include_router(contact_followup.router, prefix="/contacts", tags=["contact-followup"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
