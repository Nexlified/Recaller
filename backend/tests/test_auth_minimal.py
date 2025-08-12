"""
Minimal Authentication Integration Tests

This simplified version tests authentication endpoints by creating a minimal
FastAPI app instance with only the necessary components for authentication.
"""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from jose import jwt
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.endpoints.auth import router as auth_router
from app.core.config import settings
from app.core.security import get_password_hash, verify_password

# Create minimal FastAPI app for testing
app = FastAPI()
app.include_router(auth_router, prefix="/api/v1")

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/test_auth_minimal.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    """Get test database session"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override database dependency
from app.api import deps
app.dependency_overrides[deps.get_db] = get_test_db

def setup_test_database():
    """Create test database tables and insert default data"""
    with engine.connect() as conn:
        # Create tenants table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create users table  
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                is_superuser BOOLEAN DEFAULT FALSE,
                tenant_id INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """))
        
        # Insert default tenant
        conn.execute(text("""
            INSERT OR IGNORE INTO tenants (id, name, slug) 
            VALUES (1, 'Test Tenant', 'test')
        """))
        
        # Insert test user
        test_password_hash = get_password_hash("testpassword123")
        conn.execute(text("""
            INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, is_active, tenant_id)
            VALUES (1, 'testuser@example.com', :password_hash, 'Test User', 1, 1)
        """), {"password_hash": test_password_hash})
        
        # Insert inactive user
        inactive_password_hash = get_password_hash("inactivepassword")
        conn.execute(text("""
            INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, is_active, tenant_id)
            VALUES (2, 'inactive@example.com', :password_hash, 'Inactive User', 0, 1)
        """), {"password_hash": inactive_password_hash})
        
        conn.commit()

def cleanup_test_database():
    """Clean up test database"""
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users WHERE id > 2"))
        conn.commit()

# Setup database
setup_test_database()

client = TestClient(app)

def test_login_valid_credentials():
    """Test successful login with valid credentials"""
    response = client.post(
        "/api/v1/login",
        data={
            "username": "testuser@example.com",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    
    # Verify token is valid JWT
    token = data["access_token"]
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify token payload
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert "sub" in payload
    assert "exp" in payload
    assert payload["sub"] == "1"  # User ID

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/login",
        data={
            "username": "testuser@example.com",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Incorrect email or password"

def test_login_inactive_user():
    """Test login with inactive user account"""
    response = client.post(
        "/api/v1/login",
        data={
            "username": "inactive@example.com",
            "password": "inactivepassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Inactive user"

def test_login_missing_fields():
    """Test login with missing required fields"""
    # Missing username
    response = client.post(
        "/api/v1/login",
        data={"password": "testpassword123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 422
    
    # Missing password
    response = client.post(
        "/api/v1/login",
        data={"username": "testuser@example.com"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 422

def test_register_valid_user():
    """Test successful user registration"""
    user_data = {
        "email": "newuser@example.com",
        "password": "newuserpassword123",
        "full_name": "New User"
    }
    
    response = client.post(
        "/api/v1/register",
        json=user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "id" in data
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] is True
    assert "created_at" in data
    assert "hashed_password" not in data  # Password should not be in response
    
    # Verify user can login
    login_response = client.post(
        "/api/v1/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert login_response.status_code == 200
    
    # Cleanup
    cleanup_test_database()

def test_register_duplicate_email():
    """Test registration with already existing email"""
    user_data = {
        "email": "testuser@example.com",  # Already exists
        "password": "somepassword123",
        "full_name": "Duplicate User"
    }
    
    response = client.post(
        "/api/v1/register",
        json=user_data
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "The user with this email already exists in the system"

def test_register_invalid_email():
    """Test registration with invalid email format"""
    user_data = {
        "email": "notanemail",
        "password": "validpassword123",
        "full_name": "Test User"
    }
    
    response = client.post(
        "/api/v1/register",
        json=user_data
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_register_weak_password():
    """Test registration with weak password"""
    user_data = {
        "email": "weak@example.com",
        "password": "123",  # Too short
        "full_name": "Weak Password User"
    }
    
    response = client.post(
        "/api/v1/register",
        json=user_data
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_token_security():
    """Test token security properties"""
    response = client.post(
        "/api/v1/login",
        data={
            "username": "testuser@example.com",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Decode token and verify structure
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    
    # Check required fields
    assert "sub" in payload
    assert "exp" in payload
    
    # Verify expiration is in the future
    exp_datetime = datetime.utcfromtimestamp(payload["exp"])
    assert exp_datetime > datetime.utcnow()
    
    # Verify user ID is correct
    assert payload["sub"] == "1"

def test_password_hashing():
    """Test that passwords are properly hashed"""
    user_data = {
        "email": "hashtest@example.com", 
        "password": "plaintextpassword123",
        "full_name": "Hash Test User"
    }
    
    response = client.post(
        "/api/v1/register",
        json=user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    user_id = data["id"]
    
    # Check password is hashed in database
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT hashed_password FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        stored_hash = result[0]
        
        # Verify password is not stored as plaintext
        assert stored_hash != user_data["password"]
        
        # Verify hash can be verified with original password
        assert verify_password(user_data["password"], stored_hash)
    
    # Cleanup
    cleanup_test_database()

if __name__ == "__main__":
    # Run tests
    print("Running minimal authentication tests...")
    
    tests = [
        test_login_valid_credentials,
        test_login_invalid_credentials,
        test_login_inactive_user,
        test_login_missing_fields,
        test_register_valid_user,
        test_register_duplicate_email,
        test_register_invalid_email,
        test_register_weak_password,
        test_token_security,
        test_password_hashing
    ]
    
    for test_func in tests:
        try:
            print(f"  ✓ {test_func.__name__}")
            test_func()
        except Exception as e:
            print(f"  ❌ {test_func.__name__}: {e}")
            raise
    
    print("\n🎉 All minimal authentication tests passed!")