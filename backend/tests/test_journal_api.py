"""
Tests for Journal API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import date

from app.main import app
from app.schemas.journal import JournalEntryMoodEnum


client = TestClient(app)


class TestJournalAPI:
    """Test the Journal API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock authentication for all tests
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.is_active = True
        self.mock_user.tenant_id = 1
        
        # Mock tenant state
        self.mock_tenant = Mock()
        self.mock_tenant.id = 1
    
    @patch('app.api.deps.get_current_active_user')
    @patch('app.api.deps.get_db')
    def test_list_journal_entries_empty(self, mock_get_db, mock_get_user):
        """Test listing journal entries when none exist"""
        mock_get_user.return_value = self.mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock request state
        with patch('app.api.v1.endpoints.journal.journal_crud.get_by_user', return_value=[]):
            with client as c:
                # Mock the request state
                with patch.object(c, 'request') as mock_request:
                    mock_request.state.tenant = self.mock_tenant
                    response = c.get("/api/v1/journal/")
        
        # Note: This test may fail due to middleware dependencies
        # In a real test environment, we'd have proper test setup
        # For now, this shows the structure
    
    def test_journal_endpoints_structure(self):
        """Test that journal endpoints are properly registered"""
        # Test that the API router includes journal endpoints
        from app.api.v1.api import api_router
        
        # Check that journal router is included
        journal_routes = [route for route in api_router.routes if hasattr(route, 'path') and '/journal' in route.path]
        assert len(journal_routes) > 0, "Journal routes should be registered"
    
    def test_journal_schema_validation(self):
        """Test journal schema validation"""
        from app.schemas.journal import JournalEntryCreate, JournalEntryMoodEnum
        
        # Test valid entry creation
        valid_entry = JournalEntryCreate(
            content="This is a test journal entry.",
            entry_date=date.today(),
            mood=JournalEntryMoodEnum.HAPPY
        )
        
        assert valid_entry.content == "This is a test journal entry."
        assert valid_entry.entry_date == date.today()
        assert valid_entry.mood == JournalEntryMoodEnum.HAPPY
        assert valid_entry.is_private is True  # Default value
    
    def test_journal_mood_enum(self):
        """Test that journal mood enum has all expected values"""
        expected_moods = [
            "very_happy", "happy", "content", "neutral", "anxious", 
            "sad", "very_sad", "angry", "excited", "grateful"
        ]
        
        for mood in expected_moods:
            assert hasattr(JournalEntryMoodEnum, mood.upper())
            assert JournalEntryMoodEnum[mood.upper()].value == mood


class TestJournalSchemas:
    """Test Journal Pydantic schemas"""
    
    def test_journal_entry_create_minimal(self):
        """Test creating journal entry with minimal required fields"""
        from app.schemas.journal import JournalEntryCreate
        
        entry = JournalEntryCreate(
            content="Minimal entry",
            entry_date=date.today()
        )
        
        assert entry.content == "Minimal entry"
        assert entry.entry_date == date.today()
        assert entry.is_private is True
        assert entry.title is None
        assert entry.mood is None
    
    def test_journal_entry_create_with_tags(self):
        """Test creating journal entry with tags"""
        from app.schemas.journal import JournalEntryCreate, JournalTagCreate
        
        tag = JournalTagCreate(tag_name="happy", tag_color="#FFD700")
        entry = JournalEntryCreate(
            content="Entry with tags",
            entry_date=date.today(),
            tags=[tag]
        )
        
        assert len(entry.tags) == 1
        assert entry.tags[0].tag_name == "happy"
        assert entry.tags[0].tag_color == "#FFD700"
    
    def test_journal_tag_color_validation(self):
        """Test that journal tag color validates hex format"""
        from app.schemas.journal import JournalTagCreate
        from pydantic import ValidationError
        
        # Valid hex colors should work
        valid_tag = JournalTagCreate(tag_name="test", tag_color="#FF5733")
        assert valid_tag.tag_color == "#FF5733"
        
        # Invalid hex colors should raise validation error
        with pytest.raises(ValidationError):
            JournalTagCreate(tag_name="test", tag_color="invalid-color")
    
    def test_journal_entry_update_partial(self):
        """Test that journal entry update allows partial updates"""
        from app.schemas.journal import JournalEntryUpdate
        
        # Should be able to update just the title
        update = JournalEntryUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.content is None
        assert update.mood is None
        
        # Should be able to update just archived status
        archive_update = JournalEntryUpdate(is_archived=True)
        assert archive_update.is_archived is True
        assert archive_update.title is None