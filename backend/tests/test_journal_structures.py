import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.crud import journal
from app.schemas.journal import (
    JournalEntryCreate, JournalTagCreate, JournalEntryMoodEnum,
    PaginationMeta, JournalEntryListResponse
)


class TestOptimizedJournalStructures:
    """Test the new optimized data structures and pagination."""

    @pytest.fixture
    def test_entries(self, db_session: Session):
        """Create test entries for structure validation."""
        entries = []
        base_date = date.today() - timedelta(days=10)
        
        for i in range(15):
            entry_date = base_date + timedelta(days=i)
            entry_data = JournalEntryCreate(
                title=f"Test Entry {i + 1}",
                content=f"Content for test entry {i + 1}.",
                entry_date=entry_date,
                mood=JournalEntryMoodEnum.HAPPY if i % 2 == 0 else JournalEntryMoodEnum.CONTENT,
                tags=[JournalTagCreate(tag_name=f"tag_{i % 3}", tag_color="#FF0000")] if i % 4 == 0 else []
            )
            
            created_entry = journal.create_journal_entry(
                db=db_session,
                journal_entry=entry_data,
                user_id=1,
                tenant_id=1
            )
            entries.append(created_entry)
        
        return entries

    def test_pagination_metadata_structure(self, db_session: Session, test_entries):
        """Test that pagination metadata has the correct structure."""
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=5
        )
        
        # Test manual pagination metadata creation
        pagination = PaginationMeta(
            total=total_count,
            page=1,
            per_page=5,
            total_pages=(total_count + 4) // 5,  # Ceiling division
            has_next=1 < (total_count + 4) // 5,
            has_previous=1 > 1
        )
        
        assert pagination.total == 15
        assert pagination.page == 1
        assert pagination.per_page == 5
        assert pagination.total_pages == 3
        assert pagination.has_next is True
        assert pagination.has_previous is False
        
        # Test second page
        pagination_page2 = PaginationMeta(
            total=total_count,
            page=2,
            per_page=5,
            total_pages=(total_count + 4) // 5,
            has_next=2 < (total_count + 4) // 5,
            has_previous=2 > 1
        )
        
        assert pagination_page2.has_next is True
        assert pagination_page2.has_previous is True

    def test_optimized_pagination_functions(self, db_session: Session, test_entries):
        """Test the new optimized pagination functions."""
        # Test first page
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=5
        )
        
        assert len(entries) == 5
        assert total_count == 15
        
        # Test middle page
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=2,
            per_page=5
        )
        
        assert len(entries) == 5
        assert total_count == 15
        
        # Test last page
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=3,
            per_page=5
        )
        
        assert len(entries) == 5  # Last 5 entries
        assert total_count == 15

    def test_optimized_search_with_pagination(self, db_session: Session, test_entries):
        """Test optimized search with pagination."""
        entries, total_count = journal.search_entries_optimized(
            db=db_session,
            user_id=1,
            tenant_id=1,
            search_text="Test Entry",
            page=1,
            per_page=10
        )
        
        assert total_count == 15  # All entries should match
        assert len(entries) == 10  # First page
        
        # Test second page
        entries, total_count = journal.search_entries_optimized(
            db=db_session,
            user_id=1,
            tenant_id=1,
            search_text="Test Entry",
            page=2,
            per_page=10
        )
        
        assert total_count == 15
        assert len(entries) == 5  # Remaining entries

    def test_count_function_with_filters(self, db_session: Session, test_entries):
        """Test the count function with various filters."""
        # Test basic count
        count = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1
        )
        assert count == 15
        
        # Test count with mood filter
        count = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1,
            mood=JournalEntryMoodEnum.HAPPY
        )
        assert count == 8  # Every even index (0,2,4,6,8,10,12,14)
        
        # Test count with search
        count = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1,
            search_text="Test Entry"
        )
        assert count == 15  # All should match

    def test_bulk_operations_functions(self, db_session: Session, test_entries):
        """Test bulk operation functions."""
        entry_ids = [entry.id for entry in test_entries[:5]]
        
        # Test bulk update
        success_count, errors = journal.bulk_update_entries(
            db=db_session,
            user_id=1,
            tenant_id=1,
            entry_ids=entry_ids,
            updates={'is_archived': True}
        )
        
        assert success_count == 5
        assert len(errors) == 0
        
        # Verify the update worked
        count_archived = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1,
            include_archived=True
        )
        count_active = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1,
            include_archived=False
        )
        
        assert count_archived == 15  # All entries
        assert count_active == 10   # 15 - 5 archived

    def test_popular_tags_function(self, db_session: Session, test_entries):
        """Test popular tags function."""
        popular_tags = journal.get_popular_tags(
            db=db_session,
            user_id=1,
            tenant_id=1,
            limit=5
        )
        
        # Should have some tags (entries 0, 4, 8, 12 have tags)
        assert len(popular_tags) > 0
        
        # Check structure
        if len(popular_tags) > 0:
            tag = popular_tags[0]
            assert 'tag_name' in tag
            assert 'usage_count' in tag
            assert tag['usage_count'] > 0

    def test_combined_filters_performance(self, db_session: Session, test_entries):
        """Test combining multiple filters works correctly."""
        start_date = date.today() - timedelta(days=8)
        end_date = date.today() - timedelta(days=2)
        
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=20,
            mood=JournalEntryMoodEnum.HAPPY,
            start_date=start_date,
            end_date=end_date
        )
        
        # Should get entries that match both mood and date range
        assert total_count > 0
        for entry in entries:
            assert entry.mood == JournalEntryMoodEnum.HAPPY.value
            assert start_date <= entry.entry_date <= end_date
        
        # Test count function with same filters
        count = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1,
            mood=JournalEntryMoodEnum.HAPPY,
            start_date=start_date,
            end_date=end_date
        )
        
        assert count == total_count  # Should match the pagination count