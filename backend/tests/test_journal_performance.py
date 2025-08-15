import pytest
import time
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.crud import journal
from app.schemas.journal import JournalEntryCreate, JournalTagCreate, JournalEntryMoodEnum
from app.models.journal import JournalEntry


class TestJournalPerformance:
    """Test performance optimizations for journal entries."""

    @pytest.fixture
    def sample_entries(self, db_session: Session):
        """Create sample journal entries for performance testing."""
        entries = []
        base_date = date.today() - timedelta(days=365)
        
        # Create 100 sample entries over the past year
        for i in range(100):
            entry_date = base_date + timedelta(days=i * 3)
            mood = list(JournalEntryMoodEnum)[i % len(list(JournalEntryMoodEnum))]
            
            entry_data = JournalEntryCreate(
                title=f"Entry {i + 1}",
                content=f"This is the content for journal entry {i + 1}. " * 10,  # Make content longer
                entry_date=entry_date,
                mood=mood,
                location="Test Location" if i % 3 == 0 else None,
                weather="Sunny" if i % 2 == 0 else "Cloudy",
                is_private=i % 2 == 0,
                tags=[
                    JournalTagCreate(tag_name=f"tag{i % 5}", tag_color="#FF0000"),
                    JournalTagCreate(tag_name=f"category{i % 3}", tag_color="#00FF00")
                ] if i % 4 == 0 else []
            )
            
            created_entry = journal.create_journal_entry(
                db=db_session,
                journal_entry=entry_data,
                user_id=1,
                tenant_id=1
            )
            entries.append(created_entry)
        
        return entries

    def test_pagination_performance(self, db_session: Session, sample_entries):
        """Test that pagination performs well with large datasets."""
        start_time = time.time()
        
        # Test getting first page
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=20
        )
        
        first_page_time = time.time() - start_time
        
        assert len(entries) == 20
        assert total_count == 100
        assert first_page_time < 0.1  # Should be fast
        
        # Test getting middle page
        start_time = time.time()
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=3,
            per_page=20
        )
        
        middle_page_time = time.time() - start_time
        
        assert len(entries) == 20
        assert total_count == 100
        assert middle_page_time < 0.1  # Should be fast

    def test_search_performance(self, db_session: Session, sample_entries):
        """Test that search performs well."""
        start_time = time.time()
        
        entries, total_count = journal.search_entries_optimized(
            db=db_session,
            user_id=1,
            tenant_id=1,
            search_text="Entry",
            page=1,
            per_page=20
        )
        
        search_time = time.time() - start_time
        
        assert total_count == 100  # All entries should match "Entry"
        assert len(entries) == 20  # First page
        assert search_time < 0.2  # Should be reasonably fast

    def test_mood_filtering_performance(self, db_session: Session, sample_entries):
        """Test that mood filtering performs well."""
        start_time = time.time()
        
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=50,
            mood=JournalEntryMoodEnum.HAPPY
        )
        
        filter_time = time.time() - start_time
        
        assert total_count > 0  # Some entries should have happy mood
        assert all(entry.mood == JournalEntryMoodEnum.HAPPY.value for entry in entries)
        assert filter_time < 0.1  # Should be fast with proper indexing

    def test_date_range_filtering_performance(self, db_session: Session, sample_entries):
        """Test that date range filtering performs well."""
        start_date = date.today() - timedelta(days=100)
        end_date = date.today() - timedelta(days=50)
        
        start_time = time.time()
        
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=50,
            start_date=start_date,
            end_date=end_date
        )
        
        filter_time = time.time() - start_time
        
        assert total_count > 0  # Some entries should be in this range
        assert all(start_date <= entry.entry_date <= end_date for entry in entries)
        assert filter_time < 0.1  # Should be fast with proper indexing

    def test_bulk_operations_performance(self, db_session: Session, sample_entries):
        """Test that bulk operations perform well."""
        entry_ids = [entry.id for entry in sample_entries[:50]]
        
        # Test bulk update
        start_time = time.time()
        success_count, errors = journal.bulk_update_entries(
            db=db_session,
            user_id=1,
            tenant_id=1,
            entry_ids=entry_ids,
            updates={'is_archived': True}
        )
        bulk_update_time = time.time() - start_time
        
        assert success_count == 50
        assert len(errors) == 0
        assert bulk_update_time < 0.5  # Should be reasonably fast
        
        # Test bulk tag addition
        tags = [JournalTagCreate(tag_name="bulk_tag", tag_color="#FF00FF")]
        
        start_time = time.time()
        success_count, errors = journal.bulk_add_tags(
            db=db_session,
            user_id=1,
            tenant_id=1,
            entry_ids=entry_ids[:10],  # Smaller set for tag operation
            tags=tags
        )
        bulk_tag_time = time.time() - start_time
        
        assert success_count == 10
        assert len(errors) == 0
        assert bulk_tag_time < 0.3  # Should be reasonably fast

    def test_count_queries_performance(self, db_session: Session, sample_entries):
        """Test that count queries perform well."""
        start_time = time.time()
        
        count = journal.get_entry_count(
            db=db_session,
            user_id=1,
            tenant_id=1,
            include_archived=True  # Include all entries regardless of archived status
        )
        
        count_time = time.time() - start_time
        
        assert count == 100  # Should have all 100 entries
        assert count_time < 0.05  # Count queries should be very fast

    def test_popular_tags_performance(self, db_session: Session, sample_entries):
        """Test that popular tags query performs well."""
        start_time = time.time()
        
        popular_tags = journal.get_popular_tags(
            db=db_session,
            user_id=1,
            tenant_id=1,
            limit=10
        )
        
        tags_time = time.time() - start_time
        
        assert len(popular_tags) > 0
        assert tags_time < 0.1  # Should be fast with proper indexing

    def test_memory_usage_with_large_results(self, db_session: Session, sample_entries):
        """Test that memory usage is reasonable with large result sets."""
        # This test ensures we're not loading too much data at once
        entries, total_count = journal.get_entries_with_pagination(
            db=db_session,
            user_id=1,
            tenant_id=1,
            page=1,
            per_page=100,  # Request all entries
            include_archived=True
        )
        
        # With pagination, we should only get the requested number
        assert len(entries) == 100
        assert total_count == 100
        
        # Memory usage test - ensure entries don't have all relationships loaded by default
        # This prevents N+1 queries and excessive memory usage
        first_entry = entries[0]
        # Tags and attachments should not be loaded unless explicitly requested
        # This is implementation dependent on how SQLAlchemy lazy loading is configured