"""
Tests for journal entry validation and sanitization.

This module tests the security and data integrity features added to journal entries.
"""
import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate, JournalTagCreate, JournalTagUpdate,
    JournalEntryMoodEnum
)
from app.core.validation import (
    ContentSanitizer, TimestampValidator, ColorValidator
)


class TestContentSanitization:
    """Test content sanitization functionality."""
    
    def test_sanitize_basic_text(self):
        """Test basic text sanitization."""
        text = "This is normal text content."
        result = ContentSanitizer.sanitize_text(text)
        assert result == text
    
    def test_sanitize_html_content(self):
        """Test HTML escaping."""
        html_content = '<script>alert("xss")</script>Hello <b>world</b>'
        with pytest.raises(ValueError, match="malicious script patterns"):
            ContentSanitizer.sanitize_text(html_content)
    
    def test_sanitize_javascript_injection(self):
        """Test JavaScript injection prevention."""
        malicious_inputs = [
            'javascript:alert("xss")',
            '<img src="x" onerror="alert(1)">',
            '<iframe src="data:text/html,<script>alert(1)</script>"></iframe>',
            '<object data="javascript:alert(1)"></object>',
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValueError, match="malicious script patterns|suspicious URL patterns"):
                ContentSanitizer.sanitize_text(malicious_input)
    
    def test_length_validation(self):
        """Test content length validation."""
        long_content = "a" * 1000
        with pytest.raises(ValueError, match="exceeds maximum length"):
            ContentSanitizer.sanitize_text(long_content, max_length=500)
    
    def test_excessive_whitespace_normalization(self):
        """Test normalization of excessive whitespace."""
        content_with_spaces = "Hello" + " " * 20 + "world"
        result = ContentSanitizer.sanitize_text(content_with_spaces)
        assert result.count(" ") == 10  # Should be limited to 10 spaces
        
        # Test with internal newlines (not at start/end)
        content_with_newlines = "Start" + "\n" * 10 + "Middle" + "\n" * 8 + "End"
        result = ContentSanitizer.sanitize_text(content_with_newlines)
        # The first sequence of 10 newlines gets reduced to 5
        # The second sequence of 8 newlines gets reduced to 5  
        # But then the \s{10,} regex might further modify it
        assert result.count("\n") == 5  # Should be limited by \n{5,} regex
    
    def test_title_sanitization(self):
        """Test title-specific sanitization."""
        valid_title = "My Journal Entry"
        result = ContentSanitizer.sanitize_title(valid_title)
        assert result == valid_title
        
        # Test None handling
        assert ContentSanitizer.sanitize_title(None) is None
        
        # Test length limit
        long_title = "a" * 300
        with pytest.raises(ValueError):
            ContentSanitizer.sanitize_title(long_title)
    
    def test_tag_name_sanitization(self):
        """Test tag name sanitization."""
        valid_tags = ["happy", "work-stuff", "life_events", "family time", "café_time", "学习"]
        for tag in valid_tags:
            result = ContentSanitizer.sanitize_tag_name(tag)
            assert result == tag
        
        invalid_tags = [
            "tag<script>",
            "tag&amp;",
            "tag/slash",
            "tag\\backslash",
            "tag\"quote",
        ]
        for tag in invalid_tags:
            with pytest.raises(ValueError, match="special characters|letters, numbers"):
                ContentSanitizer.sanitize_tag_name(tag)


class TestTimestampValidation:
    """Test timestamp validation functionality."""
    
    def test_valid_entry_dates(self):
        """Test valid entry dates."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        future_date = today + timedelta(days=10)
        
        for test_date in [today, yesterday, future_date]:
            result = TimestampValidator.validate_entry_date(test_date)
            assert result == test_date
    
    def test_ancient_date_rejection(self):
        """Test rejection of dates too far in the past."""
        ancient_date = date(1800, 1, 1)
        with pytest.raises(ValueError, match="cannot be before"):
            TimestampValidator.validate_entry_date(ancient_date)
    
    def test_far_future_date_rejection(self):
        """Test rejection of dates too far in the future."""
        far_future = date.today() + timedelta(days=100)
        with pytest.raises(ValueError, match="more than .* days in the future"):
            TimestampValidator.validate_entry_date(far_future)


class TestColorValidation:
    """Test color validation functionality."""
    
    def test_valid_hex_colors(self):
        """Test valid hex color validation."""
        valid_colors = ["#FF5733", "#000000", "#FFFFFF", "#ff5733"]
        for color in valid_colors:
            result = ColorValidator.validate_hex_color(color)
            assert result == color.upper()
    
    def test_invalid_hex_colors(self):
        """Test invalid hex color rejection."""
        invalid_colors = [
            "red",
            "#FF",
            "#GGGGGG",
            "#FF5733AA",  # Too long
            "FF5733",     # Missing #
        ]
        for color in invalid_colors:
            with pytest.raises(ValueError, match="valid hex code"):
                ColorValidator.validate_hex_color(color)
    
    def test_none_color_handling(self):
        """Test None color handling."""
        assert ColorValidator.validate_hex_color(None) is None


class TestJournalEntryValidation:
    """Test journal entry schema validation."""
    
    def test_valid_entry_creation(self):
        """Test creating a valid journal entry."""
        entry_data = JournalEntryCreate(
            title="My Day",
            content="Today was a good day. I accomplished a lot!",
            entry_date=date.today(),
            mood=JournalEntryMoodEnum.HAPPY,
            location="Home",
            weather="Sunny"
        )
        
        assert entry_data.title == "My Day"
        assert entry_data.content == "Today was a good day. I accomplished a lot!"
        assert entry_data.mood == JournalEntryMoodEnum.HAPPY
    
    def test_malicious_content_rejection(self):
        """Test rejection of malicious content."""
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content='<script>alert("xss")</script>Malicious content',
                entry_date=date.today()
            )
    
    def test_empty_content_rejection(self):
        """Test rejection of empty content."""
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content="",
                entry_date=date.today()
            )
        
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content="   ",  # Only whitespace
                entry_date=date.today()
            )
    
    def test_invalid_date_rejection(self):
        """Test rejection of invalid dates."""
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content="Valid content",
                entry_date=date(1800, 1, 1)  # Too old
            )
    
    def test_long_content_rejection(self):
        """Test rejection of overly long content."""
        very_long_content = "a" * 60000  # Exceeds max length
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content=very_long_content,
                entry_date=date.today()
            )
    
    def test_malicious_location_rejection(self):
        """Test rejection of malicious location data."""
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content="Valid content",
                entry_date=date.today(),
                location='<script>alert("location")</script>'
            )
    
    def test_entry_update_validation(self):
        """Test journal entry update validation."""
        # Valid update
        update_data = JournalEntryUpdate(
            title="Updated Title",
            content="Updated content"
        )
        assert update_data.title == "Updated Title"
        
        # Invalid update with malicious content
        with pytest.raises(ValidationError):
            JournalEntryUpdate(
                content='<script>alert("update")</script>'
            )


class TestJournalTagValidation:
    """Test journal tag schema validation."""
    
    def test_valid_tag_creation(self):
        """Test creating valid tags."""
        tag_data = JournalTagCreate(
            tag_name="happy",
            tag_color="#FF5733"
        )
        
        assert tag_data.tag_name == "happy"
        assert tag_data.tag_color == "#FF5733"
    
    def test_invalid_tag_name_rejection(self):
        """Test rejection of invalid tag names."""
        with pytest.raises(ValidationError):
            JournalTagCreate(
                tag_name="tag<script>",
                tag_color="#FF5733"
            )
    
    def test_invalid_color_rejection(self):
        """Test rejection of invalid colors."""
        with pytest.raises(ValidationError):
            JournalTagCreate(
                tag_name="valid_tag",
                tag_color="red"  # Not a hex code
            )
    
    def test_tag_update_validation(self):
        """Test tag update validation."""
        # Valid update
        update_data = JournalTagUpdate(
            tag_name="updated_tag",
            tag_color="#000000"
        )
        assert update_data.tag_name == "updated_tag"
        assert update_data.tag_color == "#000000"
        
        # Invalid update
        with pytest.raises(ValidationError):
            JournalTagUpdate(
                tag_name="tag/invalid"
            )


class TestSecurityBoundaries:
    """Test security boundary conditions."""
    
    def test_unicode_handling(self):
        """Test proper handling of Unicode characters."""
        unicode_content = "Today I felt 😊 and had café with friends! Naïve approach didn't work."
        entry_data = JournalEntryCreate(
            content=unicode_content,
            entry_date=date.today()
        )
        # Should handle Unicode properly
        assert "😊" in entry_data.content
        assert "café" in entry_data.content
    
    def test_mixed_content_attack(self):
        """Test mixed content attacks."""
        mixed_attack = """
        This looks like normal content but contains:
        <iframe src="javascript:alert('xss')"></iframe>
        hidden malicious code.
        """
        
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content=mixed_attack,
                entry_date=date.today()
            )
    
    def test_encoded_attacks(self):
        """Test encoded attack prevention."""
        # HTML entity encoded script
        encoded_attack = "&lt;script&gt;alert('xss')&lt;/script&gt;"
        
        # This should pass validation since it's already HTML encoded
        # but our validator will escape it further for safety
        entry_data = JournalEntryCreate(
            content=encoded_attack,
            entry_date=date.today()
        )
        
        # The content should be double-escaped for safety
        assert "&amp;lt;" in entry_data.content
    
    def test_null_byte_injection(self):
        """Test null byte injection prevention."""
        null_content = "Normal content\x00and more content"
        # Should handle gracefully - Python strings handle null bytes
        entry_data = JournalEntryCreate(
            content=null_content,
            entry_date=date.today()
        )
        # Null bytes should be preserved but sanitized
        assert entry_data.content == "Normal content\x00and more content"
        
        # Test content with both null bytes AND script (should be rejected for the script)
        malicious_null_content = "Normal content\x00<script>alert('xss')</script>"
        with pytest.raises(ValidationError):
            JournalEntryCreate(
                content=malicious_null_content,
                entry_date=date.today()
            )