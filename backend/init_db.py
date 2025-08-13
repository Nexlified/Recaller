#!/usr/bin/env python3
"""
Initialize database with tables for testing
"""
from app.db.session import engine
from app.db.base_class import Base

# Import all models to ensure they're registered
from app.models.user import User
from app.models.tenant import Tenant
from app.models.contact import Contact
from app.models.task import Task, TaskCategory, TaskContact, TaskRecurrence, TaskCategoryAssignment

# Create all tables
Base.metadata.create_all(bind=engine)

# Create default tenant
from sqlalchemy.orm import Session
from app.models.tenant import Tenant

with Session(engine) as session:
    # Check if default tenant exists
    tenant = session.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant:
        tenant = Tenant(
            id=1,
            name="Default Tenant",
            slug="default",
            is_active=True
        )
        session.add(tenant)
        session.commit()
        print("Created default tenant")
    else:
        print("Default tenant already exists")

print("Database initialized successfully!")