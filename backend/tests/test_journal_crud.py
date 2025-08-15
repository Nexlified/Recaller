import pytest
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.crud import journal
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalTagCreate,
    JournalEntryMoodEnum
)
from app.models.journal import JournalEntry, JournalTag


class TestJournalCRUD:
    """Test Journal CRUD operations."""
    
    def test_create_journal_entry_minimal(self, db_session: Session):
        """Test creating a journal entry with minimal data."""
        entry_data = JournalEntryCreate(
            content="This is my first journal entry.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_entry.id is not None
        assert created_entry.content == "This is my first journal entry."
        assert created_entry.user_id == 1
        assert created_entry.tenant_id == 1
        assert created_entry.entry_date == date.today()
        assert created_entry.is_private is True  # Default value
        assert created_entry.is_archived is False  # Default value
    
    def test_create_journal_entry_full(self, db_session: Session):
        """Test creating a journal entry with full data."""
        tag_data = JournalTagCreate(
            tag_name="happy", 
            tag_color="#FFD700"
        )
        
        entry_data = JournalEntryCreate(
            title="A Great Day",
            content="Today was amazing! I finished my project and celebrated with friends.",
            entry_date=date.today(),
            mood=JournalEntryMoodEnum.VERY_HAPPY,
            location="Home",
            weather="Sunny",
            is_private=False,
            tags=[tag_data]
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        assert created_entry.id is not None
        assert created_entry.title == "A Great Day"
        assert created_entry.mood == JournalEntryMoodEnum.VERY_HAPPY.value
        assert created_entry.location == "Home"
        assert created_entry.weather == "Sunny"
        assert created_entry.is_private is False
        assert len(created_entry.tags) == 1
        assert created_entry.tags[0].tag_name == "happy"
        assert created_entry.tags[0].tag_color == "#FFD700"
    
    def test_get_journal_entry(self, db_session: Session):
        """Test retrieving a journal entry."""
        # Create an entry first
        entry_data = JournalEntryCreate(
            content="Test entry for retrieval.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Retrieve the entry
        retrieved_entry = journal.get_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1
        )
        
        assert retrieved_entry is not None
        assert retrieved_entry.id == created_entry.id
        assert retrieved_entry.content == "Test entry for retrieval."
    
    def test_get_journal_entry_wrong_user(self, db_session: Session):
        """Test that users can only access their own entries."""
        # Create an entry for user 1
        entry_data = JournalEntryCreate(
            content="Private entry for user 1.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Try to retrieve as user 2 - should return None
        retrieved_entry = journal.get_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=2,  # Different user
            tenant_id=1
        )
        
        assert retrieved_entry is None
    
    def test_update_journal_entry(self, db_session: Session):
        """Test updating a journal entry."""
        # Create an entry first
        entry_data = JournalEntryCreate(
            content="Original content.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Update the entry
        update_data = JournalEntryUpdate(
            title="Updated Title",
            content="Updated content with more details.",
            mood=JournalEntryMoodEnum.HAPPY
        )
        
        updated_entry = journal.update_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        assert updated_entry is not None
        assert updated_entry.title == "Updated Title"
        assert updated_entry.content == "Updated content with more details."
        assert updated_entry.mood == JournalEntryMoodEnum.HAPPY.value
    
    def test_delete_journal_entry(self, db_session: Session):
        """Test deleting a journal entry."""
        # Create an entry first
        entry_data = JournalEntryCreate(
            content="Entry to be deleted.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Delete the entry
        success = journal.delete_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1
        )
        
        assert success is True
        
        # Verify entry is deleted
        deleted_entry = journal.get_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1
        )
        
        assert deleted_entry is None
    
    def test_archive_journal_entry(self, db_session: Session):
        """Test archiving a journal entry."""
        # Create an entry first
        entry_data = JournalEntryCreate(
            content="Entry to be archived.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Archive the entry
        archived_entry = journal.archive_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1,
            archive=True
        )
        
        assert archived_entry is not None
        assert archived_entry.is_archived is True
        
        # Unarchive the entry
        unarchived_entry = journal.archive_journal_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1,
            archive=False
        )
        
        assert unarchived_entry is not None
        assert unarchived_entry.is_archived is False
    
    def test_add_and_remove_tag(self, db_session: Session):
        """Test adding and removing tags from an entry."""
        # Create an entry first
        entry_data = JournalEntryCreate(
            content="Entry for tag testing.",
            entry_date=date.today()
        )
        
        created_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Add a tag
        tag_data = JournalTagCreate(
            tag_name="test-tag",
            tag_color="#FF5733"
        )
        
        added_tag = journal.add_tag_to_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1,
            tag=tag_data
        )
        
        assert added_tag is not None
        assert added_tag.tag_name == "test-tag"
        assert added_tag.tag_color == "#FF5733"
        assert added_tag.journal_entry_id == created_entry.id
        
        # Remove the tag
        success = journal.remove_tag_from_entry(
            db=db_session,
            entry_id=created_entry.id,
            user_id=1,
            tenant_id=1,
            tag_name="test-tag"
        )
        
        assert success is True
    
    def test_tenant_isolation(self, db_session: Session):
        """Test that tenant isolation works correctly."""
        # Create entries for different tenants
        entry_data = JournalEntryCreate(
            content="Entry for tenant 1.",
            entry_date=date.today()
        )
        
        entry_tenant1 = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        entry_tenant2 = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=2
        )
        
        # User from tenant 1 should not see tenant 2's entry
        retrieved_entry = journal.get_journal_entry(
            db=db_session,
            entry_id=entry_tenant2.id,
            user_id=1,
            tenant_id=1  # Different tenant
        )
        
        assert retrieved_entry is None
        
        # User from tenant 2 should see their own entry
        retrieved_entry = journal.get_journal_entry(
            db=db_session,
            entry_id=entry_tenant2.id,
            user_id=1,
            tenant_id=2  # Same tenant
        )
        
        assert retrieved_entry is not None
        assert retrieved_entry.id == entry_tenant2.id