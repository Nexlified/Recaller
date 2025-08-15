"""
Validation and sanitization utilities for journal entries.

This module provides robust validation and sanitization functions to prevent
security vulnerabilities and ensure data integrity for journal entries.
"""

import re
import html
from typing import Optional
from datetime import date, datetime, timedelta
from pydantic import validator, ValidationError


class ContentSanitizer:
    """Sanitizes journal content for security and data integrity."""
    
    # Maximum lengths to prevent DoS attacks
    MAX_TITLE_LENGTH = 255
    MAX_CONTENT_LENGTH = 50000  # ~50KB of text
    MAX_LOCATION_LENGTH = 255
    MAX_WEATHER_LENGTH = 100
    MAX_TAG_NAME_LENGTH = 50
    
    # Patterns for potentially malicious content
    SCRIPT_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<form[^>]*>',
    ]
    
    # Suspicious URL patterns
    SUSPICIOUS_URL_PATTERNS = [
        r'data:text/html',
        r'vbscript:',
        r'file://',
    ]
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text content for security.
        
        Args:
            text: Raw text input
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValueError: If content is too long or contains suspicious patterns
        """
        if not text:
            return text
            
        # Check length limits first
        if max_length and len(text) > max_length:
            raise ValueError(f"Text exceeds maximum length of {max_length} characters")
        
        # Check for script injections BEFORE HTML escaping (case-insensitive)
        for pattern in cls.SCRIPT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                raise ValueError("Content contains potentially malicious script patterns")
        
        # Check for suspicious URLs BEFORE HTML escaping
        for pattern in cls.SUSPICIOUS_URL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Content contains suspicious URL patterns")
        
        # HTML escape to prevent XSS
        sanitized = html.escape(text, quote=True)
        
        # Remove excessive whitespace but preserve intentional formatting
        sanitized = re.sub(r'\s{10,}', ' ' * 10, sanitized)  # Limit consecutive spaces
        sanitized = re.sub(r'\n{5,}', '\n' * 5, sanitized)   # Limit consecutive newlines
        
        # Only strip leading/trailing whitespace, preserve internal structure
        return sanitized.strip()
    
    @classmethod
    def sanitize_title(cls, title: Optional[str]) -> Optional[str]:
        """Sanitize journal entry title."""
        if not title:
            return title
        return cls.sanitize_text(title, cls.MAX_TITLE_LENGTH)
    
    @classmethod
    def sanitize_content(cls, content: str) -> str:
        """Sanitize journal entry content."""
        return cls.sanitize_text(content, cls.MAX_CONTENT_LENGTH)
    
    @classmethod
    def sanitize_location(cls, location: Optional[str]) -> Optional[str]:
        """Sanitize location field."""
        if not location:
            return location
        return cls.sanitize_text(location, cls.MAX_LOCATION_LENGTH)
    
    @classmethod
    def sanitize_weather(cls, weather: Optional[str]) -> Optional[str]:
        """Sanitize weather field."""
        if not weather:
            return weather
        return cls.sanitize_text(weather, cls.MAX_WEATHER_LENGTH)
    
    @classmethod
    def sanitize_tag_name(cls, tag_name: str) -> str:
        """Sanitize tag name."""
        # Additional restrictions for tags
        sanitized = cls.sanitize_text(tag_name, cls.MAX_TAG_NAME_LENGTH)
        
        # Tag names should not contain special HTML/URL characters
        if re.search(r'[<>"\'/\\&;]', sanitized):
            raise ValueError("Tag names cannot contain special characters")
        
        # Must be alphanumeric with hyphens, underscores, and spaces
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', sanitized):
            raise ValueError("Tag names must contain only letters, numbers, spaces, hyphens, and underscores")
        
        return sanitized


class TimestampValidator:
    """Validates timestamps for journal entries."""
    
    # Reasonable date bounds
    MIN_ENTRY_DATE = date(1900, 1, 1)
    MAX_FUTURE_DAYS = 30  # Allow entries up to 30 days in the future
    
    @classmethod
    def validate_entry_date(cls, entry_date: date) -> date:
        """
        Validate journal entry date.
        
        Args:
            entry_date: The date to validate
            
        Returns:
            Validated date
            
        Raises:
            ValueError: If date is outside reasonable bounds
        """
        if entry_date < cls.MIN_ENTRY_DATE:
            raise ValueError(f"Entry date cannot be before {cls.MIN_ENTRY_DATE}")
        
        max_future_date = date.today() + timedelta(days=cls.MAX_FUTURE_DAYS)
        if entry_date > max_future_date:
            raise ValueError(f"Entry date cannot be more than {cls.MAX_FUTURE_DAYS} days in the future")
        
        return entry_date


class ColorValidator:
    """Validates color values for tags."""
    
    @classmethod
    def validate_hex_color(cls, color: Optional[str]) -> Optional[str]:
        """
        Validate hex color code.
        
        Args:
            color: Hex color string
            
        Returns:
            Validated color or None
            
        Raises:
            ValueError: If color format is invalid
        """
        if not color:
            return color
        
        # Must be exactly 7 characters: # + 6 hex digits
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("Color must be a valid hex code (e.g., #FF5733)")
        
        return color.upper()  # Normalize to uppercase


def create_journal_content_validator():
    """Create a validator function for journal content."""
    def validate_content(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return ContentSanitizer.sanitize_content(v)
    return validate_content


def create_journal_title_validator():
    """Create a validator function for journal title."""
    def validate_title(v: Optional[str]) -> Optional[str]:
        return ContentSanitizer.sanitize_title(v)
    return validate_title


def create_journal_location_validator():
    """Create a validator function for journal location."""
    def validate_location(v: Optional[str]) -> Optional[str]:
        return ContentSanitizer.sanitize_location(v)
    return validate_location


def create_journal_weather_validator():
    """Create a validator function for journal weather."""
    def validate_weather(v: Optional[str]) -> Optional[str]:
        return ContentSanitizer.sanitize_weather(v)
    return validate_weather


def create_entry_date_validator():
    """Create a validator function for entry date."""
    def validate_entry_date(v: date) -> date:
        return TimestampValidator.validate_entry_date(v)
    return validate_entry_date


def create_tag_name_validator():
    """Create a validator function for tag names."""
    def validate_tag_name(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tag name cannot be empty")
        return ContentSanitizer.sanitize_tag_name(v)
    return validate_tag_name


def create_tag_color_validator():
    """Create a validator function for tag colors."""
    def validate_tag_color(v: Optional[str]) -> Optional[str]:
        return ColorValidator.validate_hex_color(v)
    return validate_tag_color