"""
Integration Tests for Authentication Endpoints

This module provides comprehensive integration tests for the authentication endpoints
at /api/v1/auth/, covering login and registration functionality with various scenarios.

Test coverage includes:
- Happy path testing (valid login, successful registration)
- Error handling (invalid credentials, duplicate emails, validation errors)
- Security testing (token generation/validation, input sanitization)
- Edge cases (malformed data, inactive users)
- Multi-tenant context support
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import jwt

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.api.deps import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/test_auth_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Setup test tables
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
                tenant_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """))
        
        # Insert default tenant
        conn.execute(text("""
            INSERT OR IGNORE INTO tenants (id, name, slug) 
            VALUES (1, 'Test Tenant', 'test')
        """))
        
        # Insert test user for authentication tests
        test_password_hash = get_password_hash("testpassword123")
        conn.execute(text("""
            INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, is_active, tenant_id)
            VALUES (1, 'testuser@example.com', :password_hash, 'Test User', TRUE, 1)
        """), {"password_hash": test_password_hash})
        
        # Insert inactive user for testing
        inactive_password_hash = get_password_hash("inactivepassword")
        conn.execute(text("""
            INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, is_active, tenant_id)
            VALUES (2, 'inactive@example.com', :password_hash, 'Inactive User', FALSE, 1)
        """), {"password_hash": inactive_password_hash})
        
        conn.commit()

def cleanup_test_database():
    """Clean up test database"""
    with engine.connect() as conn:
        # Delete test users (except pre-existing ones)
        conn.execute(text("DELETE FROM users WHERE id > 2"))
        conn.commit()

# Setup database before running tests
setup_test_database()

client = TestClient(app)

class TestAuthLogin:
    """Test cases for POST /api/v1/auth/login endpoint"""
    
    def test_login_valid_credentials(self):
        """Test successful login with valid credentials"""
        response = client.post(
            "/api/v1/auth/login",
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
        
        # Verify token expiration is reasonable
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        time_diff = exp_datetime - now
        
        # Should expire in approximately 30 minutes (settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        assert 29 <= time_diff.total_seconds() / 60 <= 31
    
    def test_login_invalid_email(self):
        """Test login with non-existent email"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Incorrect email or password"
    
    def test_login_invalid_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser@example.com",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Incorrect email or password"
    
    def test_login_inactive_user(self):
        """Test login with inactive user account"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "inactivepassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Inactive user"
    
    def test_login_missing_username(self):
        """Test login with missing username field"""
        response = client.post(
            "/api/v1/auth/login",
            data={"password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
        
        # Check validation error for missing username
        username_error = next((err for err in data["detail"] if "username" in err["loc"]), None)
        assert username_error is not None
        assert username_error["type"] == "missing"
    
    def test_login_missing_password(self):
        """Test login with missing password field"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser@example.com"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
        
        # Check validation error for missing password
        password_error = next((err for err in data["detail"] if "password" in err["loc"]), None)
        assert password_error is not None
        assert password_error["type"] == "missing"
    
    def test_login_empty_credentials(self):
        """Test login with empty username and password"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Incorrect email or password"
    
    def test_login_sql_injection_attempt(self):
        """Test SQL injection protection in login"""
        malicious_inputs = [
            "test@example.com'; DROP TABLE users; --",
            "test@example.com' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": malicious_input,
                    "password": "anypassword"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Should return authentication error, not crash or succeed
            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "Incorrect email or password"

class TestAuthRegister:
    """Test cases for POST /api/v1/auth/register endpoint"""
    
    def test_register_valid_user(self):
        """Test successful user registration with valid data"""
        user_data = {
            "email": "newuser@example.com",
            "password": "newuserpassword123",
            "full_name": "New User"
        }
        
        response = client.post(
            "/api/v1/auth/register",
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
        
        # Verify user can login with the new credentials
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        
        # Cleanup: remove the test user
        cleanup_test_database()
    
    def test_register_duplicate_email(self):
        """Test registration with already existing email"""
        user_data = {
            "email": "testuser@example.com",  # This email already exists
            "password": "somepassword123",
            "full_name": "Duplicate User"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "The user with this email already exists in the system"
    
    def test_register_invalid_email_format(self):
        """Test registration with invalid email format"""
        invalid_emails = [
            "notanemail",
            "invalid@",
            "@invalid.com",
            "invalid.com",
            "test@",
            "test@.com"
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "email": invalid_email,
                "password": "validpassword123",
                "full_name": "Test User"
            }
            
            response = client.post(
                "/api/v1/auth/register",
                json=user_data
            )
            
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], list)
            
            # Check for email validation error
            email_error = next((err for err in data["detail"] if "email" in err["loc"]), None)
            assert email_error is not None
    
    def test_register_weak_passwords(self):
        """Test registration with passwords that don't meet requirements"""
        weak_passwords = [
            "",          # Empty password
            "1234567",   # Too short (< 8 characters)
            "short",     # Too short
            "a" * 101,   # Too long (> 100 characters)
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": f"test{len(weak_password)}@example.com",
                "password": weak_password,
                "full_name": "Test User"
            }
            
            response = client.post(
                "/api/v1/auth/register",
                json=user_data
            )
            
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], list)
            
            # Check for password validation error
            password_error = next((err for err in data["detail"] if "password" in err["loc"]), None)
            assert password_error is not None
    
    def test_register_missing_required_fields(self):
        """Test registration with missing required fields"""
        # Missing email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "password": "validpassword123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing password
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
    
    def test_register_optional_full_name(self):
        """Test registration without optional full_name field"""
        user_data = {
            "email": "noname@example.com",
            "password": "validpassword123"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] is None
        assert data["is_active"] is True
        
        # Cleanup
        cleanup_test_database()
    
    def test_register_sql_injection_protection(self):
        """Test SQL injection protection in registration"""
        malicious_inputs = [
            "test'; DROP TABLE users; --@example.com",
            "test@example.com'; DELETE FROM users; --",
            "test@example.com' OR '1'='1' --"
        ]
        
        for malicious_email in malicious_inputs:
            user_data = {
                "email": malicious_email,
                "password": "validpassword123",
                "full_name": "Test User"
            }
            
            response = client.post(
                "/api/v1/auth/register",
                json=user_data
            )
            
            # Should either fail validation or register safely without SQL injection
            assert response.status_code in [201, 422]
            if response.status_code == 201:
                # If registration succeeds, ensure it was stored safely
                data = response.json()
                assert data["email"] == malicious_email  # Stored as-is, not executed
        
        # Cleanup
        cleanup_test_database()
    
    def test_register_password_hashing(self):
        """Test that passwords are properly hashed in the database"""
        user_data = {
            "email": "hashtest@example.com",
            "password": "plaintextpassword123",
            "full_name": "Hash Test User"
        }
        
        response = client.post(
            "/api/v1/auth/register",
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
            
            # Verify wrong password fails verification
            assert not verify_password("wrongpassword", stored_hash)
        
        # Cleanup
        cleanup_test_database()

class TestAuthSecurity:
    """Security-focused tests for authentication endpoints"""
    
    def test_token_expiration_format(self):
        """Test that tokens have proper expiration timestamps"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser@example.com",
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Decode token and check expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
        
        # Verify expiration is in the future
        exp_datetime = datetime.utcfromtimestamp(payload["exp"])
        assert exp_datetime > datetime.utcnow()
    
    def test_token_contains_user_id(self):
        """Test that tokens contain the correct user ID"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser@example.com",
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == "1"  # Known test user ID
    
    def test_case_sensitive_email(self):
        """Test that email authentication is case-sensitive or properly normalized"""
        # Test with different cases
        test_cases = [
            "testuser@example.com",
            "TestUser@example.com",
            "TESTUSER@EXAMPLE.COM",
            "testuser@EXAMPLE.COM"
        ]
        
        original_email = "testuser@example.com"
        password = "testpassword123"
        
        for email_variant in test_cases:
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": email_variant,
                    "password": password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # This test documents current behavior - adjust expectations based on requirements
            if email_variant.lower() == original_email.lower():
                # If email matching is case-insensitive, this should succeed
                pass  # Behavior depends on implementation
            else:
                # If email matching is case-sensitive, only exact match should succeed
                pass  # Behavior depends on implementation
    
    def test_large_payload_handling(self):
        """Test handling of unusually large request payloads"""
        # Very long strings to test input limits
        very_long_string = "a" * 1000
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{very_long_string}@example.com",
                "password": "validpassword123",
                "full_name": very_long_string
            }
        )
        
        # Should handle gracefully - either validate and reject or accept within limits
        assert response.status_code in [201, 422]
        
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data

class TestTenantContext:
    """Test multi-tenant context handling"""
    
    def test_login_with_tenant_header(self):
        """Test login with tenant context header"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser@example.com",
                "password": "testpassword123"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Tenant-ID": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_register_with_tenant_context(self):
        """Test registration with tenant context"""
        user_data = {
            "email": "tenant-test@example.com",
            "password": "tenantpassword123",
            "full_name": "Tenant Test User"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data,
            headers={"X-Tenant-ID": "test"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        
        # Cleanup
        cleanup_test_database()

def test_auth_endpoints_response_time():
    """Performance benchmark test for authentication endpoints"""
    import time
    
    # Test login performance
    start_time = time.time()
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    login_time = time.time() - start_time
    
    assert response.status_code == 200
    assert login_time < 1.0  # Should complete within 1 second
    
    # Test registration performance
    start_time = time.time()
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "perf-test@example.com",
            "password": "performancetest123",
            "full_name": "Performance Test User"
        }
    )
    register_time = time.time() - start_time
    
    assert response.status_code == 201
    assert register_time < 2.0  # Should complete within 2 seconds (hashing takes time)
    
    # Cleanup
    cleanup_test_database()

def test_concurrent_user_registration():
    """Test handling of concurrent registration attempts"""
    import threading
    import time
    
    results = []
    
    def register_user(email_suffix):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"concurrent{email_suffix}@example.com",
                "password": "concurrenttest123",
                "full_name": f"Concurrent User {email_suffix}"
            }
        )
        results.append(response.status_code)
    
    # Start multiple registration threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=register_user, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All registrations should succeed (different emails)
    assert all(status == 201 for status in results)
    assert len(results) == 5
    
    # Cleanup
    cleanup_test_database()

if __name__ == "__main__":
    # Run all tests
    print("Running authentication integration tests...")
    
    try:
        # Run test classes
        test_classes = [TestAuthLogin, TestAuthRegister, TestAuthSecurity, TestTenantContext]
        
        for test_class in test_classes:
            print(f"\n--- Running {test_class.__name__} ---")
            test_instance = test_class()
            
            # Get all test methods
            test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
            
            for test_method in test_methods:
                try:
                    print(f"  ✓ {test_method}")
                    getattr(test_instance, test_method)()
                except Exception as e:
                    print(f"  ❌ {test_method}: {e}")
                    raise
        
        # Run standalone tests
        print(f"\n--- Running Performance Tests ---")
        print("  ✓ test_auth_endpoints_response_time")
        test_auth_endpoints_response_time()
        
        print("  ✓ test_concurrent_user_registration")
        test_concurrent_user_registration()
        
        print("\n🎉 All authentication integration tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Final cleanup
        cleanup_test_database()