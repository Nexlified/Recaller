import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func

from app.main import app
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash

# Create a simple base for just our test models
TestBase = declarative_base()

# Simple test models - just what we need for user tests
class TestTenant(TestBase):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class TestUser(TestBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True, server_default="1")

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_simple.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    """Create test database and tables."""
    TestBase.metadata.create_all(bind=engine)
    yield
    TestBase.metadata.drop_all(bind=engine)


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
    tenant = db_session.query(TestTenant).filter(TestTenant.id == 1).first()
    if not tenant:
        tenant = TestTenant(
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
    user = TestUser(
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        is_active=test_user_data["is_active"],
        tenant_id=test_tenant.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
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
    user = TestUser(
        email=test_superuser_data["email"],
        hashed_password=get_password_hash(test_superuser_data["password"]),
        full_name=test_superuser_data["full_name"],
        is_active=test_superuser_data["is_active"],
        is_superuser=True,
        tenant_id=test_tenant.id,
    )
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