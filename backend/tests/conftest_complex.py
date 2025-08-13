import os
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api import deps
from app.db.base_class import Base
from app.core.config import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate
from app.core.security import create_access_token

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db):
    """Create a database session for testing."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


def override_get_db(db_session):
    """Override the get_db dependency for testing."""
    def _get_db():
        yield db_session
    return _get_db


@pytest.fixture
def client(db_session):
    """Create a test client with database session override."""
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant."""
    # Create default tenant if it doesn't exist
    tenant = db_session.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant:
        tenant = Tenant(
            id=1, 
            name="Default Tenant", 
            slug="default-tenant",
            is_active=True
        )
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user_data():
    """Test user data for creating users."""
    return {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "is_active": True
    }


@pytest.fixture
def test_user(db_session, test_tenant, test_user_data):
    """Create a test user."""
    user_create = UserCreate(**test_user_data)
    user = create_user(db_session, obj_in=user_create, tenant_id=test_tenant.id)
    return user


@pytest.fixture
def test_superuser_data():
    """Test superuser data."""
    return {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "adminpassword123",
        "is_active": True
    }


@pytest.fixture
def test_superuser(db_session, test_tenant, test_superuser_data):
    """Create a test superuser."""
    user_create = UserCreate(**test_superuser_data)
    user = create_user(db_session, obj_in=user_create, tenant_id=test_tenant.id)
    # Manually set superuser status since it's not in UserCreate
    user.is_superuser = True
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    access_token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(test_superuser):
    """Create authentication headers for test superuser."""
    access_token = create_access_token(subject=str(test_superuser.id))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def invalid_auth_headers():
    """Create invalid authentication headers."""
    return {"Authorization": "Bearer invalid_token"}


@pytest.fixture
def test_user_update_data():
    """Test data for updating user profiles."""
    return {
        "full_name": "Updated Test User",
        "email": "updated.testuser@example.com"
    }