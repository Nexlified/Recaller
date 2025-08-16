#!/usr/bin/env python3
"""
Simple database initialization script for development.

This script creates the basic tables needed for CLI testing when PostgreSQL
is not available and SQLite fallback is used.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from app.models.tenant import Tenant
from app.models.user import User, DEFAULT_TENANT_ID


def init_db():
    """Initialize database with basic tables and default tenant."""
    try:
        # Create a simple SQLite engine for basic testing
        engine = create_engine("sqlite:///./recaller_test.db", connect_args={"check_same_thread": False})
        
        # Create basic tables manually to avoid JSONB issues
        metadata = MetaData()
        
        # Tenants table
        tenants_table = Table(
            'tenants', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, nullable=False),
            Column('slug', String, nullable=False, unique=True),
            Column('is_active', Boolean, nullable=False, default=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
        )
        
        # Users table
        users_table = Table(
            'users', metadata,
            Column('id', Integer, primary_key=True),
            Column('email', String, unique=True, nullable=False),
            Column('hashed_password', String, nullable=False),
            Column('full_name', String),
            Column('is_active', Boolean, default=True),
            Column('is_superuser', Boolean, default=False),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
            Column('tenant_id', Integer, ForeignKey('tenants.id'), nullable=False, default=DEFAULT_TENANT_ID)
        )
        
        # Create all tables
        metadata.create_all(engine)
        print("✅ Database tables created successfully")
        
        # Create default tenant if it doesn't exist
        Session = sessionmaker(bind=engine)
        db = Session()
        try:
            # Check if default tenant exists
            result = db.execute(text("SELECT COUNT(*) FROM tenants WHERE id = :tenant_id"), {"tenant_id": DEFAULT_TENANT_ID})
            tenant_count = result.scalar()
            
            if tenant_count == 0:
                # Insert default tenant
                from datetime import datetime
                db.execute(text("""
                    INSERT INTO tenants (id, name, slug, is_active, created_at) 
                    VALUES (:id, :name, :slug, :is_active, :created_at)
                """), {
                    "id": DEFAULT_TENANT_ID,
                    "name": "Default Tenant",
                    "slug": "default",
                    "is_active": True,
                    "created_at": datetime.utcnow()
                })
                db.commit()
                print(f"✅ Default tenant created with ID: {DEFAULT_TENANT_ID}")
            else:
                print(f"ℹ️  Default tenant already exists with ID: {DEFAULT_TENANT_ID}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    print("🚀 Initializing Recaller database...")
    init_db()
    print("✅ Database initialization complete!")