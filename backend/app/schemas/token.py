from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    JWT access token response model.
    
    This model represents the response returned after successful authentication.
    The access token should be included in the Authorization header for protected endpoints.
    """
    access_token: str = Field(
        ...,
        description="JWT access token for API authentication",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        default="bearer",
        description="Token type, always 'bearer' for JWT tokens",
        example="bearer"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "bearer"
            }
        }

class TokenPayload(BaseModel):
    """
    JWT token payload structure.
    
    This model represents the decoded payload of a JWT token.
    Used internally for token validation and user identification.
    """
    sub: Optional[int] = Field(
        None,
        description="Subject (user ID) extracted from the JWT token",
        example=123
    )
