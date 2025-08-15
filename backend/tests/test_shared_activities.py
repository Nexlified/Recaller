"""
Test for shared activities implementation.
Basic validation that the modules import correctly and schemas validate.
"""

import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from app.main import app

# Import our new modules to validate they work
from app.models.shared_activity import SharedActivity, SharedActivityParticipant, ActivityType, ActivityStatus
from app.schemas.shared_activity import SharedActivityCreate, SharedActivityParticipantCreate
from app.crud.shared_activity import create_activity_with_participants, get_activities_by_user

client = TestClient(app)


class TestSharedActivityModels:
    """Test shared activity models and schemas."""
    
    def test_activity_enums(self):
        """Test that all enums are properly defined."""
        # Test ActivityType enum
        assert ActivityType.DINNER.value == "dinner"
        assert ActivityType.MOVIE.value == "movie"
        assert ActivityType.OTHER.value == "other"
        
        # Test ActivityStatus enum
        assert ActivityStatus.PLANNED.value == "planned"
        assert ActivityStatus.COMPLETED.value == "completed"
        assert ActivityStatus.CANCELLED.value == "cancelled"
        assert ActivityStatus.POSTPONED.value == "postponed"
    
    def test_participant_schema_validation(self):
        """Test participant schema validation."""
        # Valid participant
        valid_participant = SharedActivityParticipantCreate(
            contact_id=1,
            participation_level="organizer",
            attendance_status="confirmed"
        )
        assert valid_participant.contact_id == 1
        assert valid_participant.participation_level == "organizer"
        assert valid_participant.attendance_status == "confirmed"
        
        # Test invalid participation level
        with pytest.raises(ValueError):
            SharedActivityParticipantCreate(
                contact_id=1,
                participation_level="invalid_level",
                attendance_status="confirmed"
            )
        
        # Test invalid attendance status
        with pytest.raises(ValueError):
            SharedActivityParticipantCreate(
                contact_id=1,
                participation_level="organizer",
                attendance_status="invalid_status"
            )
    
    def test_activity_schema_validation(self):
        """Test activity schema validation."""
        # Valid activity with participants
        valid_activity = SharedActivityCreate(
            activity_type="dinner",
            title="Team Dinner",
            description="Monthly team dinner",
            activity_date=date.today(),
            participants=[
                SharedActivityParticipantCreate(
                    contact_id=1,
                    participation_level="organizer",
                    attendance_status="confirmed"
                )
            ]
        )
        assert valid_activity.activity_type == "dinner"
        assert valid_activity.title == "Team Dinner"
        assert len(valid_activity.participants) == 1
        
        # Test validation - must have at least one organizer
        with pytest.raises(ValueError, match="At least one organizer is required"):
            SharedActivityCreate(
                activity_type="dinner",
                title="Team Dinner",
                activity_date=date.today(),
                participants=[
                    SharedActivityParticipantCreate(
                        contact_id=1,
                        participation_level="participant",  # No organizer
                        attendance_status="confirmed"
                    )
                ]
            )
        
        # Test validation - must have at least one participant (Pydantic v2 format)
        with pytest.raises(ValueError, match="List should have at least 1 item"):
            SharedActivityCreate(
                activity_type="dinner",
                title="Team Dinner",
                activity_date=date.today(),
                participants=[]  # No participants
            )


class TestSharedActivityImportValidation:
    """Test that shared activity modules import correctly and basic structure is valid."""
    
    def test_api_module_imports(self):
        """Test that API modules import correctly."""
        # This validates the structure without database dependency
        from app.api.v1.endpoints import shared_activities
        assert hasattr(shared_activities, 'router')
        
        # Check that the router has the expected endpoints
        route_paths = [route.path for route in shared_activities.router.routes]
        assert "/" in route_paths  # Base endpoint
        assert "/upcoming" in route_paths  # Upcoming endpoint
        assert "/insights" in route_paths  # Insights endpoint
        assert "/{activity_id}" in route_paths  # Single activity endpoint


class TestSharedActivityValidation:
    """Test shared activity validation rules."""
    
    def test_quality_rating_validation(self):
        """Test quality rating must be between 1-10."""
        # Valid rating
        valid_activity = SharedActivityCreate(
            activity_type="dinner",
            title="Test Dinner",
            activity_date=date.today(),
            quality_rating=8,
            participants=[
                SharedActivityParticipantCreate(
                    contact_id=1,
                    participation_level="organizer",
                    attendance_status="confirmed"
                )
            ]
        )
        assert valid_activity.quality_rating == 8
        
        # Invalid rating (too low)
        with pytest.raises(ValueError):
            SharedActivityCreate(
                activity_type="dinner",
                title="Test Dinner",
                activity_date=date.today(),
                quality_rating=0,  # Invalid
                participants=[
                    SharedActivityParticipantCreate(
                        contact_id=1,
                        participation_level="organizer",
                        attendance_status="confirmed"
                    )
                ]
            )
        
        # Invalid rating (too high)
        with pytest.raises(ValueError):
            SharedActivityCreate(
                activity_type="dinner",
                title="Test Dinner",
                activity_date=date.today(),
                quality_rating=11,  # Invalid
                participants=[
                    SharedActivityParticipantCreate(
                        contact_id=1,
                        participation_level="organizer",
                        attendance_status="confirmed"
                    )
                ]
            )
    
    def test_title_validation(self):
        """Test title validation."""
        # Valid title
        valid_activity = SharedActivityCreate(
            activity_type="dinner",
            title="Valid Title",
            activity_date=date.today(),
            participants=[
                SharedActivityParticipantCreate(
                    contact_id=1,
                    participation_level="organizer",
                    attendance_status="confirmed"
                )
            ]
        )
        assert valid_activity.title == "Valid Title"
        
        # Invalid title (empty)
        with pytest.raises(ValueError):
            SharedActivityCreate(
                activity_type="dinner",
                title="",  # Invalid - empty
                activity_date=date.today(),
                participants=[
                    SharedActivityParticipantCreate(
                        contact_id=1,
                        participation_level="organizer",
                        attendance_status="confirmed"
                    )
                ]
            )
        
        # Invalid title (too long)
        long_title = "a" * 300  # Longer than 255 characters
        with pytest.raises(ValueError):
            SharedActivityCreate(
                activity_type="dinner",
                title=long_title,  # Invalid - too long
                activity_date=date.today(),
                participants=[
                    SharedActivityParticipantCreate(
                        contact_id=1,
                        participation_level="organizer",
                        attendance_status="confirmed"
                    )
                ]
            )