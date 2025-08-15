"""
Validation and sanitization utilities for all API inputs.

This module provides robust validation and sanitization functions to prevent
security vulnerabilities and ensure data integrity across all API endpoints.
"""

import re
import html
from typing import Optional, Union, Any
from datetime import date, datetime, timedelta
from pydantic import validator, ValidationError
import urllib.parse


class InputSanitizer:
    """Sanitizes all user inputs for security and data integrity."""
    
    # Maximum lengths to prevent DoS attacks
    MAX_SEARCH_QUERY_LENGTH = 255
    MAX_NAME_LENGTH = 255
    MAX_EMAIL_LENGTH = 320  # RFC 5321 maximum
    MAX_PHONE_LENGTH = 20
    MAX_URL_LENGTH = 2048
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_COMMENT_LENGTH = 1000
    
    # Journal-specific limits (keeping backward compatibility)
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
        
        # Check for null bytes
        if '\x00' in text:
            raise ValueError("Text contains null bytes which are not allowed")
        
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
    def sanitize_search_query(cls, query: str) -> str:
        """Sanitize search query with strict limitations."""
        if not query:
            return query
        
        # Check length first
        if len(query) > cls.MAX_SEARCH_QUERY_LENGTH:
            raise ValueError(f"Search query exceeds maximum length of {cls.MAX_SEARCH_QUERY_LENGTH} characters")
        
        # Check for null bytes
        if '\x00' in query:
            raise ValueError("Search query contains null bytes which are not allowed")
        
        # Block SQL injection patterns
        sql_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b',
            r'[;\'"\\]',  # Dangerous characters
            r'--',        # SQL comments
            r'/\*.*?\*/', # Block comments
            r'@@\w+',     # SQL variables
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError("Search query contains prohibited patterns")
        
        # Check for script/XSS patterns
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<svg[^>]*>',
            r'<img[^>]*onerror',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError("Search query contains prohibited patterns")
        
        # Remove excessive whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # HTML escape for safety
        return html.escape(query, quote=True)
    
    @classmethod
    def sanitize_name(cls, name: str) -> str:
        """Sanitize name fields (full name, organization name, etc.)."""
        if not name:
            return name
        
        return cls.sanitize_text(name, cls.MAX_NAME_LENGTH)
    
    @classmethod
    def sanitize_email(cls, email: str) -> str:
        """Sanitize email address with basic format validation."""
        if not email:
            return email
        
        # Check length
        if len(email) > cls.MAX_EMAIL_LENGTH:
            raise ValueError(f"Email exceeds maximum length of {cls.MAX_EMAIL_LENGTH} characters")
        
        # Basic email format validation (more comprehensive validation in Pydantic schemas)
        # Check for consecutive dots, start/end dots, and other issues
        if '..' in email or email.startswith('.') or email.endswith('.') or '@.' in email or '.@' in email:
            raise ValueError("Invalid email format")
        
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        # Check for dangerous characters
        if re.search(r'[<>"\'/\\;]', email):
            raise ValueError("Email contains prohibited characters")
        
        return email.lower().strip()
    
    @classmethod
    def sanitize_phone(cls, phone: str) -> str:
        """Sanitize phone number."""
        if not phone:
            return phone
        
        # Keep only digits, +, -, (, ), and spaces
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        
        # Check length after cleaning
        if len(phone) > cls.MAX_PHONE_LENGTH:
            raise ValueError(f"Phone number exceeds maximum length of {cls.MAX_PHONE_LENGTH} characters")
        
        return phone.strip()
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """Sanitize URL with security checks."""
        if not url:
            return url
        
        # Check length
        if len(url) > cls.MAX_URL_LENGTH:
            raise ValueError(f"URL exceeds maximum length of {cls.MAX_URL_LENGTH} characters")
        
        # Check for dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:', 'ftp:']
        url_lower = url.lower()
        
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                raise ValueError(f"URL protocol '{protocol}' is not allowed")
        
        # Ensure URL starts with http:// or https://
        if not re.match(r'^https?://', url_lower):
            raise ValueError("URL must start with http:// or https://")
        
        return url.strip()
    
    @classmethod
    def sanitize_description(cls, description: str) -> str:
        """Sanitize description fields."""
        if not description:
            return description
        
        return cls.sanitize_text(description, cls.MAX_DESCRIPTION_LENGTH)
    
    @classmethod
    def sanitize_comment(cls, comment: str) -> str:
        """Sanitize comment fields."""
        if not comment:
            return comment
        
        return cls.sanitize_text(comment, cls.MAX_COMMENT_LENGTH)
    
    # Journal-specific methods for backward compatibility
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
        
        # Must be alphanumeric (including Unicode letters), spaces, hyphens, and underscores
        if not re.match(r'^[\w\s_-]+$', sanitized, re.UNICODE):
            raise ValueError("Tag names must contain only letters, numbers, spaces, hyphens, and underscores")
        
        return sanitized


# Alias for backward compatibility
ContentSanitizer = InputSanitizer


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


def create_rating_validator(field_name: str):
    """Create a validator function for 1-10 rating fields."""
    def validate_rating(v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if not isinstance(v, int):
            raise ValueError(f"{field_name} must be an integer")
        if v < 1 or v > 10:
            raise ValueError(f"{field_name} must be between 1 and 10")
        return v
    return validate_rating


def create_positive_integer_validator(field_name: str):
    """Create a validator function for positive integer fields."""
    def validate_positive_integer(v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if not isinstance(v, int):
            raise ValueError(f"{field_name} must be an integer")
        if v < 0:
            raise ValueError(f"{field_name} must be 0 or positive")
        return v
    return validate_positive_integer


def create_weather_impact_validator():
    """Create a validator function for weather impact."""
    def validate_weather_impact(v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in ['positive', 'neutral', 'negative']:
            raise ValueError("Weather impact must be 'positive', 'neutral', or 'negative'")
        return v
    return validate_weather_impact


def create_significant_events_validator():
    """Create a validator function for significant events JSON array."""
    def validate_significant_events(v: Optional[Any]) -> Optional[Any]:
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("Significant events must be a list")
        # Validate each event is a string or dict with reasonable size
        for event in v:
            if isinstance(event, str):
                if len(event) > 500:  # Reasonable limit per event
                    raise ValueError("Each significant event description must be under 500 characters")
            elif isinstance(event, dict):
                # If it's a dict, validate it has reasonable structure
                if len(str(event)) > 1000:  # Reasonable limit for dict representation
                    raise ValueError("Each significant event object must be under 1000 characters when serialized")
            else:
                raise ValueError("Each significant event must be a string or object")
        # Limit total number of events
        if len(v) > 20:
            raise ValueError("Maximum 20 significant events allowed per entry")
        return v
    return validate_significant_events


class PaginationValidator:
    """Validates pagination parameters."""
    
    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 20
    MIN_PAGE = 1
    
    @classmethod
    def validate_pagination(cls, page: int = 1, per_page: int = DEFAULT_PER_PAGE) -> tuple[int, int]:
        """Validate and sanitize pagination parameters."""
        if page < cls.MIN_PAGE:
            raise ValueError(f"Page must be at least {cls.MIN_PAGE}")
        
        if per_page > cls.MAX_PER_PAGE:
            raise ValueError(f"Per page cannot exceed {cls.MAX_PER_PAGE}")
        
        if per_page < 1:
            raise ValueError("Per page must be at least 1")
        
        return page, per_page


class QueryValidator:
    """Validates and sanitizes query parameters."""
    
    @classmethod
    def validate_search_query(cls, query: Optional[str]) -> Optional[str]:
        """Validate search query parameter."""
        if not query:
            return None
        
        # Trim whitespace
        query = query.strip()
        if not query:
            return None
        
        # Use InputSanitizer for sanitization
        return InputSanitizer.sanitize_search_query(query)
    
    @classmethod
    def validate_sort_field(cls, field: Optional[str], allowed_fields: set[str]) -> Optional[str]:
        """Validate sort field parameter."""
        if not field:
            return None
        
        if field not in allowed_fields:
            raise ValueError(f"Invalid sort field. Allowed: {', '.join(sorted(allowed_fields))}")
        
        return field
    
    @classmethod
    def validate_sort_direction(cls, direction: Optional[str]) -> Optional[str]:
        """Validate sort direction parameter."""
        if not direction:
            return None
        
        direction = direction.lower()
        if direction not in ('asc', 'desc'):
            raise ValueError("Sort direction must be 'asc' or 'desc'")
        
        return direction


def create_tag_color_validator():
    """Create a validator function for tag colors."""
    
    def validate_hex_color(color: Optional[str]) -> Optional[str]:
        """Validate that color is a valid hex color."""
        if color is None:
            return None
        
        # Remove leading # if present
        if color.startswith('#'):
            color_value = color[1:]
        else:
            color_value = color
        
        # Check if it's a valid hex color (6 digits)
        if not re.match(r'^[0-9A-Fa-f]{6}$', color_value):
            raise ValueError('Color must be a valid hex color (e.g., #FF5733 or FF5733)')
        
        # Always return with # prefix
        return f'#{color_value.upper()}'
    
    return validate_hex_color


def create_journal_title_validator():
    """Create a validator function for journal entry titles."""
    def validate_title(title: Optional[str]) -> Optional[str]:
        if not title:
            return title
        return InputSanitizer.sanitize_title(title)
    return validate_title


def create_journal_content_validator():
    """Create a validator function for journal entry content."""
    def validate_content(content: str) -> str:
        if not content or not content.strip():
            raise ValueError("Content cannot be empty or only whitespace")
        return InputSanitizer.sanitize_content(content)
    return validate_content


def create_journal_location_validator():
    """Create a validator function for journal entry locations."""
    def validate_location(location: Optional[str]) -> Optional[str]:
        if not location:
            return location
        return InputSanitizer.sanitize_location(location)
    return validate_location


def create_journal_weather_validator():
    """Create a validator function for journal entry weather."""
    def validate_weather(weather: Optional[str]) -> Optional[str]:
        if not weather:
            return weather
        return InputSanitizer.sanitize_weather(weather)
    return validate_weather


def create_entry_date_validator():
    """Create a validator function for journal entry dates."""
    def validate_entry_date(entry_date: date) -> date:
        return TimestampValidator.validate_entry_date(entry_date)
    return validate_entry_date


def create_tag_name_validator():
    """Create a validator function for tag names."""
    def validate_tag_name(tag_name: str) -> str:
        return InputSanitizer.sanitize_tag_name(tag_name)
    return validate_tag_name
    """Decorator to validate request size."""
    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            # Check content length
            content_length = request.headers.get('content-length')
            if content_length:
                try:
                    size = int(content_length)
                    if size > max_body_size:
                        from fastapi import HTTPException
                        raise HTTPException(
                            status_code=413,
                            detail=f"Request body too large. Maximum size: {max_body_size} bytes"
                        )
                except ValueError:
                    pass
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
    """Create a validator function for tag colors."""
    def validate_tag_color(v: Optional[str]) -> Optional[str]:
        return ColorValidator.validate_hex_color(v)
    return validate_tag_color