#!/usr/bin/env python3
"""
Registration API Integration Test

This script tests the registration and login functionality to verify that
the SQLAlchemy relationship issues have been resolved.

Usage:
    cd backend
    python test_registration_api.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api import deps

def setup_test_database():
    """Setup SQLite test database with proper schema"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Override the database dependency
    app.dependency_overrides[deps.get_db] = override_get_db

    # Create test tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
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
        
        conn.commit()

    return TestClient(app)

def test_user_registration(client):
    """Test user registration endpoint"""
    print("Testing user registration...")
    
    registration_data = {
        'email': 'integration_test@example.com',
        'password': 'integrationtest123',
        'full_name': 'Integration Test User'
    }
    
    response = client.post('/api/v1/register', json=registration_data)
    
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        return False
    
    user_data = response.json()
    
    # Validate response structure
    required_fields = ['id', 'email', 'full_name', 'is_active', 'created_at']
    for field in required_fields:
        if field not in user_data:
            print(f"❌ Missing field in response: {field}")
            return False
    
    # Validate data correctness
    if user_data['email'] != registration_data['email']:
        print(f"❌ Email mismatch: expected {registration_data['email']}, got {user_data['email']}")
        return False
    
    if user_data['full_name'] != registration_data['full_name']:
        print(f"❌ Full name mismatch: expected {registration_data['full_name']}, got {user_data['full_name']}")
        return False
    
    if not user_data['is_active']:
        print("❌ User should be active by default")
        return False
    
    # Security check - password should not be in response
    if 'password' in user_data or 'hashed_password' in user_data:
        print("❌ Password data found in response - security issue!")
        return False
    
    print("✅ Registration test passed")
    return user_data

def test_user_login(client, email, password):
    """Test user login endpoint"""
    print("Testing user login...")
    
    response = client.post('/api/v1/login', data={
        'username': email,
        'password': password
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    login_data = response.json()
    
    # Validate response structure
    if 'access_token' not in login_data:
        print("❌ Missing access_token in login response")
        return False
    
    if 'token_type' not in login_data:
        print("❌ Missing token_type in login response")
        return False
    
    if login_data['token_type'] != 'bearer':
        print(f"❌ Wrong token type: expected 'bearer', got {login_data['token_type']}")
        return False
    
    # JWT tokens should be reasonably long
    if len(login_data['access_token']) < 50:
        print(f"❌ Access token seems too short: {len(login_data['access_token'])} characters")
        return False
    
    print("✅ Login test passed")
    return login_data

def test_duplicate_registration(client, email):
    """Test that duplicate registration is properly rejected"""
    print("Testing duplicate registration rejection...")
    
    registration_data = {
        'email': email,
        'password': 'anotherpassword123',
        'full_name': 'Another User'
    }
    
    response = client.post('/api/v1/register', json=registration_data)
    
    if response.status_code != 400:
        print(f"❌ Duplicate registration should return 400, got {response.status_code}")
        return False
    
    error_data = response.json()
    if 'detail' not in error_data or 'already exists' not in error_data['detail']:
        print(f"❌ Wrong error message for duplicate registration: {error_data}")
        return False
    
    print("✅ Duplicate registration test passed")
    return True

def test_invalid_login(client, email):
    """Test login with invalid password"""
    print("Testing invalid login...")
    
    response = client.post('/api/v1/login', data={
        'username': email,
        'password': 'wrongpassword'
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    if response.status_code != 400:
        print(f"❌ Invalid login should return 400, got {response.status_code}")
        return False
    
    error_data = response.json()
    if 'detail' not in error_data or 'Incorrect email or password' not in error_data['detail']:
        print(f"❌ Wrong error message for invalid login: {error_data}")
        return False
    
    print("✅ Invalid login test passed")
    return True

def main():
    """Run all integration tests"""
    print("🚀 Starting Registration API Integration Tests")
    print("=" * 50)
    
    try:
        # Setup
        client = setup_test_database()
        
        # Test 1: Registration
        user_data = test_user_registration(client)
        if not user_data:
            return False
        
        # Test 2: Login
        login_data = test_user_login(client, user_data['email'], 'integrationtest123')
        if not login_data:
            return False
        
        # Test 3: Duplicate registration
        if not test_duplicate_registration(client, user_data['email']):
            return False
        
        # Test 4: Invalid login
        if not test_invalid_login(client, user_data['email']):
            return False
        
        print("=" * 50)
        print("🎉 All integration tests passed!")
        print("\n✅ Registration API is working correctly")
        print("✅ Login API is working correctly")
        print("✅ Error handling is working correctly")
        print("✅ Security measures are in place")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            os.remove('./test_integration.db')
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)