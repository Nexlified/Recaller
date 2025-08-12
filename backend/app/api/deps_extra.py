from fastapi import Request

def get_request():
    """Dependency to get the current request"""
    from fastapi import Request
    # This is a workaround since we can't easily inject Request without parameter issues
    return None  # We'll handle this differently

def get_tenant_id():
    """Get tenant ID from request state"""
    return 1  # Default tenant ID for now