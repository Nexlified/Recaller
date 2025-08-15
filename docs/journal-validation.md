# Journal Entry Validation and Security

This document describes the robust validation and sanitization features implemented for journal entries in Recaller to ensure data integrity and prevent security vulnerabilities.

## Overview

The journal validation system provides multiple layers of security:

1. **Content Sanitization** - Prevents XSS attacks and malicious content
2. **Input Length Limits** - Prevents DoS attacks through oversized content
3. **Timestamp Validation** - Ensures reasonable date boundaries
4. **Field-Specific Validation** - Validates tags, locations, and other metadata
5. **Unicode Support** - Proper handling of international characters

## Security Features

### Content Sanitization

All text content is automatically sanitized to prevent security vulnerabilities:

```python
# Example: HTML content is escaped
input: "I love <b>bold</b> text"
output: "I love &lt;b&gt;bold&lt;/b&gt; text"

# Example: Script injection is blocked
input: "<script>alert('xss')</script>Content"
result: ValidationError - "Content contains potentially malicious script patterns"
```

**Blocked Patterns:**
- `<script>` tags
- `javascript:` URLs
- Event handlers (`onclick`, `onload`, etc.)
- `<iframe>`, `<object>`, `<embed>` tags
- `<form>` tags
- `data:text/html` URLs
- `vbscript:` URLs
- `file://` URLs

### Length Limits

To prevent denial-of-service attacks, content has reasonable limits:

- **Title**: 255 characters maximum
- **Content**: 50,000 characters maximum (~50KB of text)
- **Location**: 255 characters maximum
- **Weather**: 100 characters maximum
- **Tag Name**: 50 characters maximum

### Timestamp Validation

Entry dates must be within reasonable bounds:

- **Minimum Date**: January 1, 1900
- **Maximum Future Date**: 30 days from today

```python
# Valid dates
date.today()           # ✓ Today
date(2023, 1, 1)      # ✓ Recent past
date.today() + timedelta(days=10)  # ✓ Near future

# Invalid dates
date(1800, 1, 1)      # ✗ Too far in past
date.today() + timedelta(days=100)  # ✗ Too far in future
```

### Tag Validation

Tag names and colors are strictly validated:

**Tag Names:**
- 1-50 characters
- Letters, numbers, spaces, hyphens, underscores only
- Unicode characters supported (café, 学习, etc.)
- No HTML/URL special characters (`<>"/\&;`)

**Tag Colors:**
- Must be valid hex color codes: `#RRGGBB`
- Examples: `#FF5733`, `#000000`, `#FFFFFF`

```python
# Valid tags
JournalTagCreate(tag_name="happy", tag_color="#FFD700")        # ✓
JournalTagCreate(tag_name="work-stuff", tag_color="#FF5733")   # ✓
JournalTagCreate(tag_name="café_time", tag_color="#8B4513")    # ✓

# Invalid tags
JournalTagCreate(tag_name="tag<script>", tag_color="#FF5733")  # ✗ Special chars
JournalTagCreate(tag_name="valid", tag_color="red")            # ✗ Invalid color
```

## Whitespace Normalization

Excessive whitespace is normalized to prevent abuse while preserving formatting:

- **Consecutive Spaces**: Limited to 10 spaces maximum
- **Consecutive Newlines**: Limited to 5 newlines maximum
- **Leading/Trailing**: Whitespace is trimmed

## API Error Responses

When validation fails, the API returns detailed error information:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["content"],
      "msg": "Value error, Content contains potentially malicious script patterns",
      "input": "<script>alert('xss')</script>Content"
    }
  ]
}
```

## Implementation Details

### Core Classes

**`ContentSanitizer`** - Main sanitization class
- `sanitize_text()` - General text sanitization
- `sanitize_title()` - Title-specific validation
- `sanitize_content()` - Journal content validation
- `sanitize_tag_name()` - Tag name validation

**`TimestampValidator`** - Date validation
- `validate_entry_date()` - Entry date boundary checking

**`ColorValidator`** - Color validation
- `validate_hex_color()` - Hex color format validation

### Pydantic Integration

Validation is integrated into Pydantic schemas using custom validators:

```python
class JournalEntryBase(BaseModel):
    content: str = Field(..., min_length=1)
    
    # Custom validator for security
    _validate_content = validator('content', allow_reuse=True)(create_journal_content_validator())
```

## Testing

The validation system includes comprehensive tests covering:

- **Content Sanitization**: XSS prevention, HTML escaping
- **Security Boundaries**: Script injection, URL validation
- **Length Validation**: DoS prevention
- **Unicode Support**: International character handling
- **Edge Cases**: Null bytes, encoded attacks, mixed content

Run validation tests:
```bash
cd backend
python -m pytest tests/test_journal_validation.py -v
```

## Best Practices

### For Developers

1. **Always use the schema validators** - Don't bypass validation
2. **Test with malicious content** - Ensure security measures work
3. **Consider internationalization** - Test with Unicode content
4. **Monitor length limits** - Adjust as needed for user experience

### For Users

1. **Content is automatically sanitized** - HTML will be escaped
2. **Reasonable length limits** - Very long content will be rejected
3. **Date restrictions** - Entries must be within reasonable timeframes
4. **Tag naming** - Use simple, descriptive tag names

## Security Considerations

### What This Protects Against

- **Cross-Site Scripting (XSS)** - HTML/JavaScript injection
- **Denial of Service** - Oversized content attacks
- **Data Injection** - Malicious data patterns
- **Time-based Attacks** - Invalid timestamp abuse

### What This Doesn't Protect Against

- **Application-level vulnerabilities** - Server-side issues
- **Authentication bypass** - User access controls
- **Database injection** - SQL injection (handled by ORM)
- **Network-level attacks** - DDoS, man-in-the-middle

## Performance Impact

The validation system is designed for minimal performance impact:

- **Regex patterns**: Compiled once, reused
- **Length checks**: O(1) operations
- **Text processing**: Linear with content length
- **Typical overhead**: <1ms for normal journal entries

## Migration and Compatibility

The validation system:

- **Preserves existing data** - No migration required
- **Backward compatible** - Existing API contracts unchanged
- **Progressive enhancement** - Adds security without breaking functionality
- **Configurable limits** - Can be adjusted via constants

## Troubleshooting

### Common Issues

**"Content contains potentially malicious script patterns"**
- Remove HTML tags from content
- Check for JavaScript URLs
- Avoid event handlers in text

**"Entry date cannot be before..."**
- Use dates after January 1, 1900
- Don't set entries too far in the future

**"Tag names must contain only letters..."**
- Use alphanumeric characters, spaces, hyphens, underscores
- Avoid special characters like `<>&"/\;`

**"Text exceeds maximum length..."**
- Reduce content length (max 50KB)
- Split very long entries into multiple parts

### Debug Mode

For development, you can test validation directly:

```python
from app.core.validation import ContentSanitizer

# Test content sanitization
try:
    result = ContentSanitizer.sanitize_content("Your content here")
    print(f"Sanitized: {result}")
except ValueError as e:
    print(f"Validation error: {e}")
```