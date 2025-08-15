"""
Test configuration validation, specifically SECRET_KEY security requirements.
"""
import pytest
import secrets
import os
from pydantic_core import ValidationError

def test_secret_key_minimum_length():
    """Test that SECRET_KEY must be at least 32 characters long."""
    from app.core.config import Settings
    
    # Test short secret key (should fail)
    with pytest.raises(ValidationError) as exc_info:
        Settings(SECRET_KEY="short")
    
    error = exc_info.value.errors()[0]
    assert "must be at least 32 characters long" in error["msg"]
    assert "Current length: 5" in error["msg"]

def test_secret_key_weak_defaults():
    """Test that known weak default values are rejected."""
    from app.core.config import Settings
    
    weak_secrets = [
        "your-secret-key",
        "your-secret-key-change-in-production", 
        "secret",
        "secret-key",
        "development-secret",
        "dev-secret",
        "test-secret",
        "default-secret",
        "change-me",
        "changeme",
    ]
    
    for weak_secret in weak_secrets:
        with pytest.raises(ValidationError) as exc_info:
            Settings(SECRET_KEY=weak_secret)
        
        error = exc_info.value.errors()[0]
        assert "cannot be a default/weak value" in error["msg"]

def test_secret_key_weak_patterns():
    """Test that predictable patterns are rejected."""
    from app.core.config import Settings
    
    weak_patterns = [
        "your_secret_key_12345678901234567",  # 32+ chars, becomes "yoursecretkey"
        "your-secret-key-12345678901234567",  # 32+ chars, becomes "yoursecretkey"
        "your secret key 12345678901234567",  # 32+ chars, becomes "yoursecretkey"
        "secret_key_1234567890123456789012",  # 32+ chars, becomes "secretkey"
        "my_secret_12345678901234567890123",  # 32+ chars, becomes "mysecret"
        "password_123456789012345678901234",  # 32+ chars, becomes "password"
        "admin_123456789012345678901234567",  # 32+ chars, becomes "admin"
    ]
    
    for weak_pattern in weak_patterns:
        with pytest.raises(ValidationError) as exc_info:
            Settings(SECRET_KEY=weak_pattern)
        
        error = exc_info.value.errors()[0]
        assert "appears to be a weak/predictable value" in error["msg"]

def test_secret_key_strong_secret():
    """Test that a properly strong secret key is accepted."""
    from app.core.config import Settings
    
    # Generate a strong secret key
    strong_secret = secrets.token_urlsafe(32)
    
    # This should not raise any validation errors
    settings = Settings(SECRET_KEY=strong_secret)
    assert settings.SECRET_KEY == strong_secret
    assert len(settings.SECRET_KEY) >= 32

def test_secret_key_minimum_valid_length():
    """Test that exactly 32 character strong secret is accepted."""
    from app.core.config import Settings
    
    # Create a 32-character secret that's not predictable
    strong_secret = "a1b2c3d4e5f678901234567890123456"
    assert len(strong_secret) == 32
    
    # This should not raise any validation errors
    settings = Settings(SECRET_KEY=strong_secret)
    assert settings.SECRET_KEY == strong_secret

def test_secret_key_non_string():
    """Test that non-string SECRET_KEY values are rejected."""
    from app.core.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(SECRET_KEY=123)
    
    error = exc_info.value.errors()[0]
    assert "SECRET_KEY must be a string" in error["msg"]

def test_secret_key_case_insensitive_validation():
    """Test that weak secret validation is case-insensitive."""
    from app.core.config import Settings
    
    weak_secrets = [
        "YOUR-SECRET-KEY",
        "Secret-Key",
        "CHANGE-ME",
        "Your_Secret_Key",
    ]
    
    for weak_secret in weak_secrets:
        with pytest.raises(ValidationError) as exc_info:
            Settings(SECRET_KEY=weak_secret)
        
        error = exc_info.value.errors()[0]
        assert "cannot be a default/weak value" in error["msg"] or "appears to be a weak/predictable value" in error["msg"]

def test_helpful_error_message():
    """Test that error messages include helpful guidance."""
    from app.core.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(SECRET_KEY="short")
    
    error = exc_info.value.errors()[0]
    assert "python -c \"import secrets; print(secrets.token_urlsafe(32))\"" in error["msg"]