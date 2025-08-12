import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Text, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api import deps
from app.db.base import Base
from app.core.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override ARRAY types for SQLite compatibility
def patch_array_types():
    """Replace PostgreSQL ARRAY types with JSON for SQLite testing"""
    from app.models import contact
    import sqlalchemy as sa
    
    # Replace ARRAY columns with JSON for testing
    for column_name, column in contact.Contact.__table__.columns.items():
        if hasattr(column.type, '__class__') and 'ARRAY' in str(column.type.__class__):
            column.type = JSON()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_tenant_id():
    return 1

app.dependency_overrides[deps.get_db] = override_get_db
app.dependency_overrides[deps.get_tenant_id] = override_get_tenant_id

@pytest.fixture
def client():
    # Patch array types before creating tables
    try:
        patch_array_types()
    except:
        pass  # Ignore patching errors for now
    
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    try:
        patch_array_types()
    except:
        pass  # Ignore patching errors for now
        
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)