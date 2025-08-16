import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.models.gift import Gift, GiftIdea, GiftStatus, GiftPriority
from app.crud import gift as gift_crud
from app.schemas.gift_system import GiftCreate, GiftUpdate, GiftIdeaCreate, GiftIdeaUpdate
from tests.utils.utils import random_email, random_lower_string


client = TestClient(app)


class TestGiftCRUD:
    """Test Gift CRUD operations"""
    
    @pytest.fixture
    def sample_gift_data(self):
        return {
            "title": "Test Gift",
            "description": "A test gift for someone special",
            "category": "electronics",
            "recipient_name": "John Doe",
            "occasion": "birthday",
            "occasion_date": date(2024, 6, 15),
            "budget_amount": Decimal("100.00"),
            "currency": "USD",
            "status": GiftStatus.IDEA.value,
            "priority": GiftPriority.MEDIUM.value,
            "gift_details": {"color": "blue", "size": "medium"},
            "notes": "Perfect for tech enthusiast"
        }
    
    def test_create_gift(self, db: Session, sample_gift_data):
        """Test creating a gift"""
        gift_in = GiftCreate(**sample_gift_data)
        gift = gift_crud.create_gift(
            db=db,
            obj_in=gift_in,
            user_id=1,
            tenant_id=1
        )
        
        assert gift.title == sample_gift_data["title"]
        assert gift.description == sample_gift_data["description"]
        assert gift.category == sample_gift_data["category"]
        assert gift.user_id == 1
        assert gift.tenant_id == 1
        assert gift.is_active == True
        
    def test_get_gift(self, db: Session, sample_gift_data):
        """Test retrieving a gift by ID"""
        gift_in = GiftCreate(**sample_gift_data)
        created_gift = gift_crud.create_gift(
            db=db,
            obj_in=gift_in,
            user_id=1,
            tenant_id=1
        )
        
        retrieved_gift = gift_crud.get_gift(
            db=db,
            gift_id=created_gift.id,
            tenant_id=1
        )
        
        assert retrieved_gift is not None
        assert retrieved_gift.id == created_gift.id
        assert retrieved_gift.title == sample_gift_data["title"]
        
    def test_get_gift_with_user_access(self, db: Session, sample_gift_data):
        """Test retrieving a gift with user access check"""
        gift_in = GiftCreate(**sample_gift_data)
        created_gift = gift_crud.create_gift(
            db=db,
            obj_in=gift_in,
            user_id=1,
            tenant_id=1
        )
        
        # User owns the gift
        retrieved_gift = gift_crud.get_gift_with_user_access(
            db=db,
            gift_id=created_gift.id,
            user_id=1,
            tenant_id=1
        )
        assert retrieved_gift is not None
        
        # Different user should not access the gift
        no_access_gift = gift_crud.get_gift_with_user_access(
            db=db,
            gift_id=created_gift.id,
            user_id=2,
            tenant_id=1
        )
        assert no_access_gift is None
        
    def test_update_gift(self, db: Session, sample_gift_data):
        """Test updating a gift"""
        gift_in = GiftCreate(**sample_gift_data)
        created_gift = gift_crud.create_gift(
            db=db,
            obj_in=gift_in,
            user_id=1,
            tenant_id=1
        )
        
        update_data = GiftUpdate(
            title="Updated Gift Title",
            status=GiftStatus.PURCHASED.value,
            actual_amount=Decimal("95.50")
        )
        
        updated_gift = gift_crud.update_gift(
            db=db,
            db_obj=created_gift,
            obj_in=update_data
        )
        
        assert updated_gift.title == "Updated Gift Title"
        assert updated_gift.status == GiftStatus.PURCHASED.value
        assert updated_gift.actual_amount == Decimal("95.50")
        # Original fields should remain unchanged
        assert updated_gift.description == sample_gift_data["description"]
        
    def test_delete_gift(self, db: Session, sample_gift_data):
        """Test soft deleting a gift"""
        gift_in = GiftCreate(**sample_gift_data)
        created_gift = gift_crud.create_gift(
            db=db,
            obj_in=gift_in,
            user_id=1,
            tenant_id=1
        )
        
        deleted_gift = gift_crud.delete_gift(db=db, db_obj=created_gift)
        
        assert deleted_gift.is_active == False
        
        # Should not be retrievable via normal get methods
        retrieved_gift = gift_crud.get_gift(
            db=db,
            gift_id=created_gift.id,
            tenant_id=1
        )
        assert retrieved_gift is None
        
    def test_get_gifts_with_filters(self, db: Session):
        """Test retrieving gifts with various filters"""
        # Create multiple gifts with different attributes
        gift1_data = {
            "title": "Gift 1",
            "category": "electronics",
            "status": GiftStatus.IDEA.value,
            "occasion": "birthday"
        }
        gift2_data = {
            "title": "Gift 2", 
            "category": "clothing",
            "status": GiftStatus.PURCHASED.value,
            "occasion": "christmas"
        }
        
        gift1 = gift_crud.create_gift(
            db=db,
            obj_in=GiftCreate(**gift1_data),
            user_id=1,
            tenant_id=1
        )
        gift2 = gift_crud.create_gift(
            db=db,
            obj_in=GiftCreate(**gift2_data),
            user_id=1,
            tenant_id=1
        )
        
        # Test category filter
        electronics_gifts = gift_crud.get_gifts(
            db=db,
            user_id=1,
            tenant_id=1,
            category="electronics"
        )
        assert len(electronics_gifts) == 1
        assert electronics_gifts[0].title == "Gift 1"
        
        # Test status filter
        purchased_gifts = gift_crud.get_gifts(
            db=db,
            user_id=1,
            tenant_id=1,
            status=GiftStatus.PURCHASED.value
        )
        assert len(purchased_gifts) == 1
        assert purchased_gifts[0].title == "Gift 2"


class TestGiftIdeaCRUD:
    """Test Gift Idea CRUD operations"""
    
    @pytest.fixture
    def sample_idea_data(self):
        return {
            "title": "Test Gift Idea",
            "description": "A creative gift idea",
            "category": "hobbies",
            "target_demographic": "young adult",
            "suitable_occasions": ["birthday", "graduation"],
            "price_range_min": Decimal("25.00"),
            "price_range_max": Decimal("75.00"),
            "currency": "USD",
            "idea_details": {"interests": ["sports", "music"]},
            "rating": 4,
            "tags": ["creative", "unique"],
            "notes": "Great for creative people"
        }
    
    def test_create_gift_idea(self, db: Session, sample_idea_data):
        """Test creating a gift idea"""
        idea_in = GiftIdeaCreate(**sample_idea_data)
        idea = gift_crud.create_gift_idea(
            db=db,
            obj_in=idea_in,
            user_id=1,
            tenant_id=1
        )
        
        assert idea.title == sample_idea_data["title"]
        assert idea.category == sample_idea_data["category"]
        assert idea.rating == sample_idea_data["rating"]
        assert idea.user_id == 1
        assert idea.tenant_id == 1
        assert idea.is_active == True
        assert idea.times_gifted == 0
        
    def test_search_gift_ideas(self, db: Session):
        """Test searching gift ideas"""
        # Create test ideas
        idea1_data = {
            "title": "Smartphone Accessories",
            "description": "Cool tech gadgets",
            "category": "electronics"
        }
        idea2_data = {
            "title": "Cooking Equipment",
            "description": "Kitchen tools for chefs",
            "category": "kitchen"
        }
        
        idea1 = gift_crud.create_gift_idea(
            db=db,
            obj_in=GiftIdeaCreate(**idea1_data),
            user_id=1,
            tenant_id=1
        )
        idea2 = gift_crud.create_gift_idea(
            db=db,
            obj_in=GiftIdeaCreate(**idea2_data),
            user_id=1,
            tenant_id=1
        )
        
        # Search by title
        results = gift_crud.search_gift_ideas(
            db=db,
            user_id=1,
            tenant_id=1,
            query="smartphone"
        )
        assert len(results) == 1
        assert results[0].title == "Smartphone Accessories"
        
        # Search by description
        results = gift_crud.search_gift_ideas(
            db=db,
            user_id=1,
            tenant_id=1,
            query="kitchen"
        )
        assert len(results) == 1
        assert results[0].title == "Cooking Equipment"
        
    def test_mark_gift_idea_as_gifted(self, db: Session, sample_idea_data):
        """Test marking a gift idea as gifted"""
        idea_in = GiftIdeaCreate(**sample_idea_data)
        created_idea = gift_crud.create_gift_idea(
            db=db,
            obj_in=idea_in,
            user_id=1,
            tenant_id=1
        )
        
        # Mark as gifted
        gifted_date = date(2024, 6, 15)
        updated_idea = gift_crud.mark_gift_idea_as_gifted(
            db=db,
            db_obj=created_idea,
            gifted_date=gifted_date
        )
        
        assert updated_idea.times_gifted == 1
        assert updated_idea.last_gifted_date == gifted_date
        
        # Mark as gifted again
        gift_crud.mark_gift_idea_as_gifted(db=db, db_obj=updated_idea)
        db.refresh(updated_idea)
        assert updated_idea.times_gifted == 2
        
    def test_get_popular_gift_ideas(self, db: Session):
        """Test getting popular gift ideas"""
        # Create ideas with different usage counts
        idea1 = gift_crud.create_gift_idea(
            db=db,
            obj_in=GiftIdeaCreate(title="Popular Idea", rating=5),
            user_id=1,
            tenant_id=1
        )
        idea2 = gift_crud.create_gift_idea(
            db=db,
            obj_in=GiftIdeaCreate(title="Less Popular Idea", rating=3),
            user_id=1,
            tenant_id=1
        )
        
        # Mark first idea as gifted multiple times
        gift_crud.mark_gift_idea_as_gifted(db=db, db_obj=idea1)
        gift_crud.mark_gift_idea_as_gifted(db=db, db_obj=idea1)
        gift_crud.mark_gift_idea_as_gifted(db=db, db_obj=idea2)
        
        popular_ideas = gift_crud.get_popular_gift_ideas(
            db=db,
            user_id=1,
            tenant_id=1,
            limit=10
        )
        
        # Should be ordered by times_gifted DESC, then rating DESC
        assert len(popular_ideas) == 2
        assert popular_ideas[0].title == "Popular Idea"
        assert popular_ideas[0].times_gifted == 2


class TestGiftAnalytics:
    """Test gift analytics functionality"""
    
    def test_get_gift_analytics(self, db: Session):
        """Test gift analytics calculation"""
        # Create test data
        gift1 = gift_crud.create_gift(
            db=db,
            obj_in=GiftCreate(
                title="Gift 1",
                status=GiftStatus.IDEA.value,
                category="electronics",
                budget_amount=Decimal("100.00"),
                actual_amount=Decimal("95.00")
            ),
            user_id=1,
            tenant_id=1
        )
        
        gift2 = gift_crud.create_gift(
            db=db,
            obj_in=GiftCreate(
                title="Gift 2",
                status=GiftStatus.PURCHASED.value,
                category="books",
                budget_amount=Decimal("50.00"),
                actual_amount=Decimal("45.00")
            ),
            user_id=1,
            tenant_id=1
        )
        
        idea1 = gift_crud.create_gift_idea(
            db=db,
            obj_in=GiftIdeaCreate(title="Idea 1"),
            user_id=1,
            tenant_id=1
        )
        
        analytics = gift_crud.get_gift_analytics(
            db=db,
            user_id=1,
            tenant_id=1
        )
        
        assert analytics["total_gifts"] == 2
        assert analytics["total_ideas"] == 1
        assert analytics["status_breakdown"]["idea"] == 1
        assert analytics["status_breakdown"]["purchased"] == 1
        assert analytics["category_breakdown"]["electronics"] == 1
        assert analytics["category_breakdown"]["books"] == 1
        assert analytics["budget_analytics"]["total_budget"] == 150.0
        assert analytics["budget_analytics"]["total_spent"] == 140.0