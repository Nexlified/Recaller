import pytest
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.crud import journal
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalTagCreate,
    JournalEntryMoodEnum
)
from app.models.journal import JournalEntry, JournalTag


class TestJournalVersioning:
    """Test Journal versioning functionality."""
    
    def test_create_journal_entry_version_basic(self, db_session: Session):
        """Test creating a basic version of a journal entry."""
        # Create initial entry
        entry_data = JournalEntryCreate(
            content="Original content",
            entry_date=date.today(),
            title="Original title"
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Create a new version with updates
        update_data = {"content": "Updated content", "title": "Updated title"}
        new_version = journal.create_journal_entry_version(
            db=db_session,
            original_entry=original_entry,
            update_data=update_data
        )
        
        # Verify the new version
        assert new_version.id != original_entry.id
        assert new_version.content == "Updated content"
        assert new_version.title == "Updated title"
        assert new_version.entry_version == 2
        assert new_version.parent_entry_id == original_entry.id
        assert new_version.user_id == original_entry.user_id
        assert new_version.tenant_id == original_entry.tenant_id
    
    def test_update_journal_entry_creates_version(self, db_session: Session):
        """Test that updating a journal entry creates a new version."""
        # Create initial entry
        entry_data = JournalEntryCreate(
            content="Original content",
            entry_date=date.today()
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        original_id = original_entry.id
        
        # Update the entry (should create a version)
        update_data = JournalEntryUpdate(content="Updated content")
        updated_entry = journal.update_journal_entry(
            db=db_session,
            entry_id=original_id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        # Should return a new version
        assert updated_entry.id != original_id
        assert updated_entry.content == "Updated content"
        assert updated_entry.entry_version == 2
        assert updated_entry.parent_entry_id == original_id
        
        # Original entry should still exist unchanged
        original_check = journal.get_journal_entry(
            db=db_session,
            entry_id=original_id,
            user_id=1,
            tenant_id=1
        )
        assert original_check.content == "Original content"
        assert original_check.entry_version == 1
    
    def test_get_journal_entry_versions(self, db_session: Session):
        """Test retrieving all versions of a journal entry."""
        # Create initial entry
        entry_data = JournalEntryCreate(
            content="Version 1",
            entry_date=date.today()
        )
        
        entry_v1 = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Create version 2
        update_data_v2 = JournalEntryUpdate(content="Version 2")
        entry_v2 = journal.update_journal_entry(
            db=db_session,
            entry_id=entry_v1.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data_v2
        )
        
        # Create version 3
        update_data_v3 = JournalEntryUpdate(content="Version 3")
        entry_v3 = journal.update_journal_entry(
            db=db_session,
            entry_id=entry_v1.id,  # Still reference original
            user_id=1,
            tenant_id=1,
            journal_entry=update_data_v3
        )
        
        # Get all versions
        versions = journal.get_journal_entry_versions(
            db=db_session,
            entry_id=entry_v1.id,
            user_id=1,
            tenant_id=1
        )
        
        # Should have 3 versions, ordered by version desc
        assert len(versions) == 3
        assert versions[0].entry_version == 3
        assert versions[1].entry_version == 2
        assert versions[2].entry_version == 1
        assert versions[0].content == "Version 3"
        assert versions[1].content == "Version 2"
        assert versions[2].content == "Version 1"
    
    def test_get_specific_journal_entry_version(self, db_session: Session):
        """Test retrieving a specific version of a journal entry."""
        # Create initial entry and versions
        entry_data = JournalEntryCreate(
            content="Original content",
            entry_date=date.today(),
            title="Original title"
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Create version 2
        update_data = JournalEntryUpdate(content="Updated content", title="Updated title")
        journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        # Get version 1 specifically
        version_1 = journal.get_journal_entry_version(
            db=db_session,
            entry_id=original_entry.id,
            version=1,
            user_id=1,
            tenant_id=1
        )
        
        assert version_1 is not None
        assert version_1.entry_version == 1
        assert version_1.content == "Original content"
        assert version_1.title == "Original title"
        
        # Get version 2 specifically
        version_2 = journal.get_journal_entry_version(
            db=db_session,
            entry_id=original_entry.id,
            version=2,
            user_id=1,
            tenant_id=1
        )
        
        assert version_2 is not None
        assert version_2.entry_version == 2
        assert version_2.content == "Updated content"
        assert version_2.title == "Updated title"
    
    def test_revert_journal_entry_to_version(self, db_session: Session):
        """Test reverting a journal entry to a previous version."""
        # Create initial entry
        entry_data = JournalEntryCreate(
            content="Version 1 content",
            entry_date=date.today(),
            title="Version 1 title"
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Create version 2
        update_data_v2 = JournalEntryUpdate(
            content="Version 2 content",
            title="Version 2 title"
        )
        journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data_v2
        )
        
        # Create version 3
        update_data_v3 = JournalEntryUpdate(
            content="Version 3 content",
            title="Version 3 title"
        )
        journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data_v3
        )
        
        # Revert to version 1
        reverted_entry = journal.revert_journal_entry_to_version(
            db=db_session,
            entry_id=original_entry.id,
            version=1,
            user_id=1,
            tenant_id=1
        )
        
        # Should create version 4 with version 1's content
        assert reverted_entry is not None
        assert reverted_entry.entry_version == 4
        assert reverted_entry.content == "Version 1 content"
        assert reverted_entry.title == "Version 1 title"
        assert reverted_entry.parent_entry_id == original_entry.id
        
        # Verify we have 4 versions now
        versions = journal.get_journal_entry_versions(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1
        )
        assert len(versions) == 4
    
    def test_delete_journal_entry_version(self, db_session: Session):
        """Test deleting a specific version of a journal entry."""
        # Create initial entry and versions
        entry_data = JournalEntryCreate(
            content="Version 1",
            entry_date=date.today()
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Create version 2
        update_data = JournalEntryUpdate(content="Version 2")
        journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        # Create version 3
        update_data = JournalEntryUpdate(content="Version 3")
        journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        # Delete version 2
        success = journal.delete_journal_entry_version(
            db=db_session,
            entry_id=original_entry.id,
            version=2,
            user_id=1,
            tenant_id=1
        )
        
        assert success is True
        
        # Verify version 2 is gone
        version_2 = journal.get_journal_entry_version(
            db=db_session,
            entry_id=original_entry.id,
            version=2,
            user_id=1,
            tenant_id=1
        )
        assert version_2 is None
        
        # Verify versions 1 and 3 still exist
        versions = journal.get_journal_entry_versions(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1
        )
        assert len(versions) == 2
        version_numbers = [v.entry_version for v in versions]
        assert 1 in version_numbers
        assert 3 in version_numbers
        assert 2 not in version_numbers
    
    def test_cannot_delete_root_version_with_children(self, db_session: Session):
        """Test that root version cannot be deleted if children exist."""
        # Create initial entry and a version
        entry_data = JournalEntryCreate(
            content="Version 1",
            entry_date=date.today()
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Create version 2
        update_data = JournalEntryUpdate(content="Version 2")
        journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        # Try to delete version 1 (root) - should fail
        success = journal.delete_journal_entry_version(
            db=db_session,
            entry_id=original_entry.id,
            version=1,
            user_id=1,
            tenant_id=1
        )
        
        assert success is False
    
    def test_version_tags_are_copied(self, db_session: Session):
        """Test that tags are copied when creating a new version."""
        # Create initial entry with tags
        tag_data = JournalTagCreate(tag_name="test_tag", tag_color="#FF0000")
        entry_data = JournalEntryCreate(
            content="Original content",
            entry_date=date.today(),
            tags=[tag_data]
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Update to create version 2
        update_data = JournalEntryUpdate(content="Updated content")
        updated_entry = journal.update_journal_entry(
            db=db_session,
            entry_id=original_entry.id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data
        )
        
        # Check that tags were copied to the new version
        new_version_tags = db_session.query(JournalTag).filter(
            JournalTag.journal_entry_id == updated_entry.id
        ).all()
        
        assert len(new_version_tags) == 1
        assert new_version_tags[0].tag_name == "test_tag"
        assert new_version_tags[0].tag_color == "#FF0000"
        
        # Original tags should still exist
        original_tags = db_session.query(JournalTag).filter(
            JournalTag.journal_entry_id == original_entry.id
        ).all()
        
        assert len(original_tags) == 1
    
    def test_tenant_isolation_in_versioning(self, db_session: Session):
        """Test that versioning respects tenant isolation."""
        # Create entry for tenant 1
        entry_data = JournalEntryCreate(
            content="Tenant 1 entry",
            entry_date=date.today()
        )
        
        tenant1_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Try to access versions from tenant 2 - should return empty
        versions = journal.get_journal_entry_versions(
            db=db_session,
            entry_id=tenant1_entry.id,
            user_id=1,
            tenant_id=2  # Different tenant
        )
        
        assert len(versions) == 0
        
        # Try to get specific version from different tenant - should return None
        version = journal.get_journal_entry_version(
            db=db_session,
            entry_id=tenant1_entry.id,
            version=1,
            user_id=1,
            tenant_id=2
        )
        
        assert version is None
    
    def test_user_isolation_in_versioning(self, db_session: Session):
        """Test that versioning respects user isolation."""
        # Create entry for user 1
        entry_data = JournalEntryCreate(
            content="User 1 entry",
            entry_date=date.today()
        )
        
        user1_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        
        # Try to access versions from user 2 - should return empty
        versions = journal.get_journal_entry_versions(
            db=db_session,
            entry_id=user1_entry.id,
            user_id=2,  # Different user
            tenant_id=1
        )
        
        assert len(versions) == 0
    
    def test_update_without_versioning(self, db_session: Session):
        """Test updating without creating versions (backwards compatibility)."""
        # Create initial entry
        entry_data = JournalEntryCreate(
            content="Original content",
            entry_date=date.today()
        )
        
        original_entry = journal.create_journal_entry(
            db=db_session,
            journal_entry=entry_data,
            user_id=1,
            tenant_id=1
        )
        original_id = original_entry.id
        
        # Update without creating version
        update_data = JournalEntryUpdate(content="Updated content")
        updated_entry = journal.update_journal_entry(
            db=db_session,
            entry_id=original_id,
            user_id=1,
            tenant_id=1,
            journal_entry=update_data,
            create_version=False  # Disable versioning
        )
        
        # Should update in place
        assert updated_entry.id == original_id
        assert updated_entry.content == "Updated content"
        assert updated_entry.entry_version == 1  # Still version 1
        assert updated_entry.parent_entry_id is None
        
        # Should only have 1 version
        versions = journal.get_journal_entry_versions(
            db=db_session,
            entry_id=original_id,
            user_id=1,
            tenant_id=1
        )
        assert len(versions) == 1