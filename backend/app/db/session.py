from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

from app.core.config import settings

# Use SQLite for testing if PostgreSQL is not available
try:
    # Try PostgreSQL first
    engine = create_engine(
        settings.DATABASE_URI,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
    )
    # Test connection
    with engine.connect() as conn:
        pass
except:
    # Fall back to SQLite for testing
    engine = create_engine(
        "sqlite:///./recaller_test.db",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
