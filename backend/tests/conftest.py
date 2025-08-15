import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Time, JSON
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

class TestContact(TestBase):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    visibility = Column(String(10), nullable=False, default='private', index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestSocialGroup(TestBase):
    __tablename__ = "social_groups"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    group_type = Column(String(50), nullable=False, index=True)
    privacy_level = Column(String(20), default='private')
    meets_regularly = Column(Boolean, default=False)
    meeting_frequency = Column(String(50))
    meeting_day_of_week = Column(Integer)
    meeting_time = Column(Time)
    meeting_location = Column(String(255))
    virtual_meeting_url = Column(String(500))
    founded_date = Column(Date)
    member_count = Column(Integer, default=0)
    max_members = Column(Integer)
    is_active = Column(Boolean, default=True, index=True)
    auto_add_contacts = Column(Boolean, default=False)
    group_image_url = Column(String(500))
    group_color = Column(String(7))
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestContactSocialGroupMembership(TestBase):
    __tablename__ = "contact_social_group_memberships"
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    social_group_id = Column(Integer, ForeignKey("social_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(100), default='member')
    membership_status = Column(String(50), default='active', index=True)
    joined_date = Column(Date, server_default=func.current_date())
    left_date = Column(Date)
    participation_level = Column(Integer, default=5)
    last_participated = Column(Date)
    total_events_attended = Column(Integer, default=0)
    membership_notes = Column(Text)
    invited_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestSocialGroupActivity(TestBase):
    __tablename__ = "social_group_activities"
    id = Column(Integer, primary_key=True, index=True)
    social_group_id = Column(Integer, ForeignKey("social_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    activity_type = Column(String(50))
    scheduled_date = Column(Date, index=True)
    start_time = Column(Time)
    end_time = Column(Time)
    location = Column(String(255))
    virtual_meeting_url = Column(String(500))
    status = Column(String(50), default='planned')
    max_attendees = Column(Integer)
    actual_attendees = Column(Integer, default=0)
    cost = Column(String)  # Using String for simplicity in tests instead of DECIMAL
    organizer_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestSocialGroupActivityAttendance(TestBase):
    __tablename__ = "social_group_activity_attendance"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("social_group_activities.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    attendance_status = Column(String(50), default='invited')
    rsvp_date = Column(DateTime(timezone=True))
    attendance_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Task models for testing
class TestTask(TestBase):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default='pending', index=True)
    priority = Column(String(10), nullable=False, default='medium', index=True)
    start_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True), index=True)
    completed_at = Column(DateTime(timezone=True))
    is_recurring = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestTaskContact(TestBase):
    __tablename__ = "task_contacts"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_context = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class TestTaskRecurrence(TestBase):
    __tablename__ = "task_recurrence"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    recurrence_type = Column(String(20), nullable=False)
    recurrence_interval = Column(Integer, nullable=False, default=1)
    days_of_week = Column(String(7))
    day_of_month = Column(Integer)
    end_date = Column(Date)
    max_occurrences = Column(Integer)
    lead_time_days = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class TestTaskCategory(TestBase):
    __tablename__ = "task_categories"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class TestTaskCategoryAssignment(TestBase):
    __tablename__ = "task_category_assignments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("task_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# Journal test models
class TestJournalEntry(TestBase):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    entry_date = Column(Date, nullable=False, index=True)
    mood = Column(String(20), index=True)
    location = Column(String(255))
    weather = Column(String(100))
    is_private = Column(Boolean, nullable=False, default=True)
    is_archived = Column(Boolean, nullable=False, default=False, index=True)
    entry_version = Column(Integer, nullable=False, default=1)
    parent_entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    is_encrypted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestJournalTag(TestBase):
    __tablename__ = "journal_tags"
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_name = Column(String(50), nullable=False, index=True)
    tag_color = Column(String(7))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class TestJournalAttachment(TestBase):
    __tablename__ = "journal_attachments"
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    description = Column(Text)
    is_encrypted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

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