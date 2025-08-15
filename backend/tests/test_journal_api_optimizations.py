import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.crud import journal
from app.schemas.journal import JournalEntryCreate, JournalTagCreate, JournalEntryMoodEnum


class TestJournalAPIOptimizations:
    """Test optimized journal API endpoints."""

    @pytest.fixture
    def sample_data(self, db_session: Session):
        """Create sample data for API testing."""
        entries = []
        base_date = date.today() - timedelta(days=30)
        
        # Create 25 sample entries
        for i in range(25):
            entry_date = base_date + timedelta(days=i)
            mood = list(JournalEntryMoodEnum)[i % len(list(JournalEntryMoodEnum))]
            
            entry_data = JournalEntryCreate(
                title=f"API Test Entry {i + 1}",
                content=f"Content for API test entry {i + 1}. This is some sample text.",
                entry_date=entry_date,
                mood=mood,
                location="Test Location" if i % 3 == 0 else None,
                weather="Sunny" if i % 2 == 0 else "Rainy",
                is_private=i % 2 == 0,
                tags=[
                    JournalTagCreate(tag_name=f"api_tag_{i % 3}", tag_color="#FF0000")
                ] if i % 5 == 0 else []
            )
            
            created_entry = journal.create_journal_entry(
                db=db_session,
                journal_entry=entry_data,
                user_id=1,
                tenant_id=1
            )
            entries.append(created_entry)
        
        return entries

    def test_list_entries_with_pagination(self, client: TestClient, sample_data):
        """Test the optimized list endpoint with pagination."""
        # Test first page
        response = client.get("/api/v1/journal/?page=1&per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) == 10
        
        pagination = data["pagination"]
        assert pagination["total"] == 25
        assert pagination["page"] == 1
        assert pagination["per_page"] == 10
        assert pagination["total_pages"] == 3
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is False

        # Test middle page
        response = client.get("/api/v1/journal/?page=2&per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 10
        pagination = data["pagination"]
        assert pagination["page"] == 2
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is True

        # Test last page
        response = client.get("/api/v1/journal/?page=3&per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 5  # Remaining entries
        pagination = data["pagination"]
        assert pagination["page"] == 3
        assert pagination["has_next"] is False
        assert pagination["has_previous"] is True

    def test_list_entries_with_search_pagination(self, client: TestClient, sample_data):
        """Test search with pagination."""
        response = client.get("/api/v1/journal/?search=API Test&page=1&per_page=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        
        # All entries should match the search
        assert data["pagination"]["total"] == 25
        assert len(data["items"]) == 5
        
        # Verify search results
        for item in data["items"]:
            assert "API Test" in item["title"]

    def test_list_entries_with_filters(self, client: TestClient, sample_data):
        """Test filtering with pagination."""
        # Test mood filter
        response = client.get(f"/api/v1/journal/?mood={JournalEntryMoodEnum.HAPPY.value}&page=1&per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        for item in data["items"]:
            assert item["mood"] == JournalEntryMoodEnum.HAPPY.value

        # Test date range filter
        start_date = (date.today() - timedelta(days=20)).isoformat()
        end_date = (date.today() - timedelta(days=10)).isoformat()
        
        response = client.get(f"/api/v1/journal/?start_date={start_date}&end_date={end_date}&page=1&per_page=20")
        assert response.status_code == 200
        
        data = response.json()
        # Should have entries in the date range
        assert data["pagination"]["total"] > 0

    def test_bulk_update_entries(self, client: TestClient, sample_data):
        """Test bulk update endpoint."""
        # Get some entry IDs
        entry_ids = [entry.id for entry in sample_data[:5]]
        
        response = client.post("/api/v1/journal/bulk-update", json={
            "entry_ids": entry_ids,
            "is_archived": True
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success_count"] == 5
        assert data["failed_count"] == 0
        assert len(data["errors"]) == 0

    def test_bulk_tag_entries(self, client: TestClient, sample_data):
        """Test bulk tagging endpoint."""
        entry_ids = [entry.id for entry in sample_data[:3]]
        
        response = client.post("/api/v1/journal/bulk-tag", json={
            "entry_ids": entry_ids,
            "tags_to_add": [
                {"tag_name": "bulk_test", "tag_color": "#00FF00"}
            ]
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success_count"] == 3
        assert len(data["errors"]) == 0

    def test_popular_tags_endpoint(self, client: TestClient, sample_data):
        """Test popular tags endpoint."""
        response = client.get("/api/v1/journal/tags/popular?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Should have some tags from our sample data
        if len(data) > 0:
            tag = data[0]
            assert "tag_name" in tag
            assert "usage_count" in tag

    def test_pagination_edge_cases(self, client: TestClient, sample_data):
        """Test pagination edge cases."""
        # Test page beyond available data
        response = client.get("/api/v1/journal/?page=10&per_page=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 0
        assert data["pagination"]["total"] == 25

        # Test very large per_page (should be capped)
        response = client.get("/api/v1/journal/?page=1&per_page=150")
        assert response.status_code == 422  # Validation error

        # Test invalid page number
        response = client.get("/api/v1/journal/?page=0&per_page=10")
        assert response.status_code == 422  # Validation error

    def test_performance_with_filters(self, client: TestClient, sample_data):
        """Test that filtered queries maintain good performance."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/journal/?search=test&mood=happy&page=1&per_page=20")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond quickly

    def test_archived_entries_filtering(self, client: TestClient, sample_data):
        """Test that archived entries are properly filtered."""
        # First archive some entries
        entry_ids = [sample_data[0].id, sample_data[1].id]
        client.post("/api/v1/journal/bulk-update", json={
            "entry_ids": entry_ids,
            "is_archived": True
        })
        
        # Test default behavior (should exclude archived)
        response = client.get("/api/v1/journal/?page=1&per_page=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["pagination"]["total"] == 23  # 25 - 2 archived
        
        # Test including archived
        response = client.get("/api/v1/journal/?include_archived=true&page=1&per_page=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["pagination"]["total"] == 25  # All entries

    def test_response_format_consistency(self, client: TestClient, sample_data):
        """Test that all responses follow the expected format."""
        response = client.get("/api/v1/journal/?page=1&per_page=5")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check top-level structure
        required_keys = ["items", "pagination"]
        for key in required_keys:
            assert key in data
        
        # Check pagination structure
        pagination_keys = ["total", "page", "per_page", "total_pages", "has_next", "has_previous"]
        for key in pagination_keys:
            assert key in data["pagination"]
        
        # Check items structure
        if len(data["items"]) > 0:
            item = data["items"][0]
            required_item_keys = ["id", "title", "entry_date", "mood", "is_private", "is_archived", "created_at"]
            for key in required_item_keys:
                assert key in item