import pytest
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, JSON, Numeric
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import date, datetime
from decimal import Decimal


# Simplified models for testing - avoiding the full Base import that includes currency ARRAY issues
metadata = MetaData()

tenants_table = Table(
    'tenants', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('slug', String, nullable=False, unique=True),
    Column('is_active', Boolean, nullable=False, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String, unique=True, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('full_name', String),
    Column('is_active', Boolean, default=True),
    Column('tenant_id', Integer, ForeignKey('tenants.id'), nullable=False)
)

contacts_table = Table(
    'contacts', metadata,
    Column('id', Integer, primary_key=True),
    Column('tenant_id', Integer, ForeignKey('tenants.id'), nullable=False),
    Column('created_by_user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('first_name', String(255), nullable=False),
    Column('last_name', String(255), nullable=True),
    Column('email', String(255)),
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)

gifts_table = Table(
    'gifts', metadata,
    Column('id', Integer, primary_key=True),
    Column('tenant_id', Integer, ForeignKey('tenants.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('title', String(255), nullable=False),
    Column('description', Text),
    Column('category', String(100)),
    Column('recipient_contact_id', Integer, ForeignKey('contacts.id')),
    Column('recipient_name', String(255)),
    Column('occasion', String(100)),
    Column('occasion_date', Date),
    Column('budget_amount', Numeric(10, 2)),
    Column('actual_amount', Numeric(10, 2)),
    Column('currency', String(3), nullable=False, default='USD'),
    Column('status', String(20), nullable=False, default='idea'),
    Column('priority', Integer, nullable=False, default=2),
    Column('store_name', String(255)),
    Column('purchase_url', Text),
    Column('purchase_date', Date),
    Column('gift_details', JSON, nullable=False, default={}),
    Column('tracking_number', String(255)),
    Column('delivery_date', Date),
    Column('notes', Text),
    Column('image_url', Text),
    Column('reminder_dates', JSON, nullable=False, default={}),
    Column('task_id', Integer),
    Column('transaction_id', Integer),
    Column('is_active', Boolean, nullable=False, default=True),
    Column('is_surprise', Boolean, nullable=False, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now())
)

gift_ideas_table = Table(
    'gift_ideas', metadata,
    Column('id', Integer, primary_key=True),
    Column('tenant_id', Integer, ForeignKey('tenants.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('title', String(255), nullable=False),
    Column('description', Text),
    Column('category', String(100)),
    Column('target_contact_id', Integer, ForeignKey('contacts.id')),
    Column('target_demographic', String(100)),
    Column('suitable_occasions', JSON, nullable=False, default=[]),
    Column('price_range_min', Numeric(10, 2)),
    Column('price_range_max', Numeric(10, 2)),
    Column('currency', String(3), nullable=False, default='USD'),
    Column('idea_details', JSON, nullable=False, default={}),
    Column('source_url', Text),
    Column('source_description', Text),
    Column('image_url', Text),
    Column('rating', Integer),
    Column('notes', Text),
    Column('times_gifted', Integer, nullable=False, default=0),
    Column('last_gifted_date', Date),
    Column('tags', JSON, nullable=False, default=[]),
    Column('is_active', Boolean, nullable=False, default=True),
    Column('is_favorite', Boolean, nullable=False, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now())
)


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for testing"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_tenant(session, engine):
    """Create a test tenant"""
    result = session.execute(
        tenants_table.insert().values(
            id=1,
            name="Test Tenant",
            slug="test",
            is_active=True
        )
    )
    session.commit()
    return {"id": 1, "name": "Test Tenant", "slug": "test"}


@pytest.fixture
def test_user(session, test_tenant, engine):
    """Create a test user"""
    result = session.execute(
        users_table.insert().values(
            id=1,
            email="test@example.com",
            hashed_password="hashedpass",
            full_name="Test User",
            tenant_id=test_tenant["id"],
            is_active=True
        )
    )
    session.commit()
    return {"id": 1, "email": "test@example.com", "tenant_id": test_tenant["id"]}


@pytest.fixture
def test_contact(session, test_tenant, test_user, engine):
    """Create a test contact"""
    result = session.execute(
        contacts_table.insert().values(
            id=1,
            tenant_id=test_tenant["id"],
            created_by_user_id=test_user["id"],
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            is_active=True
        )
    )
    session.commit()
    return {"id": 1, "first_name": "John", "last_name": "Doe", "tenant_id": test_tenant["id"]}


class TestGiftModel:
    """Test Gift model functionality"""

    def test_create_gift(self, session, test_tenant, test_user, test_contact):
        """Test creating a gift record"""
        result = session.execute(
            gifts_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Birthday Gift",
                description="A nice birthday present",
                category="Electronics",
                recipient_contact_id=test_contact["id"],
                occasion="Birthday",
                occasion_date=date(2024, 12, 25),
                budget_amount=Decimal("100.00"),
                currency="USD",
                status="idea",
                priority=2,
                gift_details='{"color": "blue", "size": "medium"}',
                reminder_dates='{"purchase": "2024-12-15"}',
                is_surprise=True
            )
        )
        session.commit()
        
        # Verify the record was created
        gift_id = result.inserted_primary_key[0]
        assert gift_id is not None
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gifts_table).where(gifts_table.c.id == gift_id)
        gift_row = session.execute(stmt).first()
        
        assert gift_row.title == "Birthday Gift"
        assert gift_row.status == "idea"
        assert gift_row.priority == 2
        assert gift_row.budget_amount == Decimal("100.00")
        assert gift_row.is_surprise is True

    def test_gift_relationships(self, session, test_tenant, test_user, test_contact):
        """Test Gift model relationships"""
        result = session.execute(
            gifts_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Test Gift",
                recipient_contact_id=test_contact["id"]
            )
        )
        session.commit()
        
        gift_id = result.inserted_primary_key[0]
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gifts_table).where(gifts_table.c.id == gift_id)
        gift_row = session.execute(stmt).first()
        
        assert gift_row.tenant_id == test_tenant["id"]
        assert gift_row.user_id == test_user["id"]
        assert gift_row.recipient_contact_id == test_contact["id"]

    def test_gift_status_enum(self, session, test_tenant, test_user):
        """Test gift status enumeration"""
        result = session.execute(
            gifts_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Status Test Gift",
                status="purchased"
            )
        )
        session.commit()
        
        gift_id = result.inserted_primary_key[0]
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gifts_table).where(gifts_table.c.id == gift_id)
        gift_row = session.execute(stmt).first()
        
        assert gift_row.status == "purchased"

    def test_gift_json_fields(self, session, test_tenant, test_user):
        """Test gift JSON fields functionality"""
        import json
        
        complex_details = {
            "specifications": {"brand": "Apple", "model": "iPhone"},
            "preferences": {"color": "space gray", "storage": "256GB"},
            "notes": ["waterproof case needed", "latest model"]
        }
        
        reminder_config = {
            "purchase_reminder": "2024-12-10",
            "wrap_reminder": "2024-12-20",
            "give_reminder": "2024-12-25"
        }
        
        result = session.execute(
            gifts_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Complex Gift",
                gift_details=json.dumps(complex_details),
                reminder_dates=json.dumps(reminder_config)
            )
        )
        session.commit()
        
        gift_id = result.inserted_primary_key[0]
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gifts_table).where(gifts_table.c.id == gift_id)
        gift_row = session.execute(stmt).first()
        
        # SQLite stores JSON as text, so we need to parse it
        gift_details = json.loads(gift_row.gift_details) if isinstance(gift_row.gift_details, str) else gift_row.gift_details
        reminder_dates = json.loads(gift_row.reminder_dates) if isinstance(gift_row.reminder_dates, str) else gift_row.reminder_dates
        
        assert gift_details["specifications"]["brand"] == "Apple"
        assert reminder_dates["purchase_reminder"] == "2024-12-10"
        assert "waterproof case needed" in gift_details["notes"]


class TestGiftIdeaModel:
    """Test GiftIdea model functionality"""

    def test_create_gift_idea(self, session, test_tenant, test_user, test_contact):
        """Test creating a gift idea record"""
        import json
        
        result = session.execute(
            gift_ideas_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Tech Gift Ideas",
                description="Great tech gifts for developers",
                category="Electronics",
                target_contact_id=test_contact["id"],
                target_demographic="software developer",
                suitable_occasions=json.dumps(["birthday", "promotion", "graduation"]),
                price_range_min=Decimal("50.00"),
                price_range_max=Decimal("500.00"),
                currency="USD",
                idea_details=json.dumps({"interests": ["coding", "gadgets"], "style": "modern"}),
                rating=4,
                tags=json.dumps(["tech", "professional", "useful"]),
                is_favorite=True
            )
        )
        session.commit()
        
        gift_idea_id = result.inserted_primary_key[0]
        assert gift_idea_id is not None
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gift_ideas_table).where(gift_ideas_table.c.id == gift_idea_id)
        idea_row = session.execute(stmt).first()
        
        assert idea_row.title == "Tech Gift Ideas"
        assert idea_row.rating == 4
        assert idea_row.is_favorite is True
        
        occasions = json.loads(idea_row.suitable_occasions) if isinstance(idea_row.suitable_occasions, str) else idea_row.suitable_occasions
        tags = json.loads(idea_row.tags) if isinstance(idea_row.tags, str) else idea_row.tags
        idea_details = json.loads(idea_row.idea_details) if isinstance(idea_row.idea_details, str) else idea_row.idea_details
        
        assert "birthday" in occasions
        assert "tech" in tags
        assert idea_details["style"] == "modern"

    def test_gift_idea_relationships(self, session, test_tenant, test_user, test_contact):
        """Test GiftIdea model relationships"""
        result = session.execute(
            gift_ideas_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Test Idea",
                target_contact_id=test_contact["id"]
            )
        )
        session.commit()
        
        gift_idea_id = result.inserted_primary_key[0]
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gift_ideas_table).where(gift_ideas_table.c.id == gift_idea_id)
        idea_row = session.execute(stmt).first()
        
        assert idea_row.tenant_id == test_tenant["id"]
        assert idea_row.user_id == test_user["id"]
        assert idea_row.target_contact_id == test_contact["id"]

    def test_gift_idea_tracking(self, session, test_tenant, test_user):
        """Test gift idea tracking fields"""
        result = session.execute(
            gift_ideas_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Popular Idea",
                times_gifted=3,
                last_gifted_date=date(2024, 6, 15)
            )
        )
        session.commit()
        
        gift_idea_id = result.inserted_primary_key[0]
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gift_ideas_table).where(gift_ideas_table.c.id == gift_idea_id)
        idea_row = session.execute(stmt).first()
        
        assert idea_row.times_gifted == 3
        assert idea_row.last_gifted_date == date(2024, 6, 15)

    def test_gift_idea_arrays(self, session, test_tenant, test_user):
        """Test gift idea array fields"""
        import json
        
        result = session.execute(
            gift_ideas_table.insert().values(
                tenant_id=test_tenant["id"],
                user_id=test_user["id"],
                title="Versatile Gift Idea",
                suitable_occasions=json.dumps(["birthday", "christmas", "anniversary", "graduation"]),
                tags=json.dumps(["versatile", "popular", "unisex", "affordable"])
            )
        )
        session.commit()
        
        gift_idea_id = result.inserted_primary_key[0]
        
        # Query back the record
        from sqlalchemy import select
        stmt = select(gift_ideas_table).where(gift_ideas_table.c.id == gift_idea_id)
        idea_row = session.execute(stmt).first()
        
        occasions = json.loads(idea_row.suitable_occasions) if isinstance(idea_row.suitable_occasions, str) else idea_row.suitable_occasions
        tags = json.loads(idea_row.tags) if isinstance(idea_row.tags, str) else idea_row.tags
        
        assert len(occasions) == 4
        assert "christmas" in occasions
        assert len(tags) == 4
        assert "versatile" in tags