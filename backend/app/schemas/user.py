from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr = Field(
        ...,
        description="User's email address, used for login and notifications",
        example="john.doe@example.com"
    )
    full_name: Optional[str] = Field(
        None,
        description="User's full display name",
        example="John Doe",
        max_length=100
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="Whether the user account is active and can log in",
        example=True
    )

class UserCreate(UserBase):
    """
    User creation model for registration.
    
    Contains all fields required to create a new user account.
    The password will be hashed before storage.
    """
    password: str = Field(
        ...,
        description="User's password (will be hashed before storage)",
        min_length=8,
        max_length=100,
        example="securepassword123"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "password": "securepassword123",
                "is_active": True
            }
        }

class UserUpdate(BaseModel):
    """
    User update model for profile modifications.
    
    All fields are optional for partial updates.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="User's email address, used for login and notifications",
        example="john.doe@example.com"
    )
    full_name: Optional[str] = Field(
        None,
        description="User's full display name",
        example="John Doe",
        max_length=100
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the user account is active and can log in",
        example=True
    )
    password: Optional[str] = Field(
        None,
        description="New password (will be hashed before storage)",
        min_length=8,
        max_length=100
    )

class UserInDBBase(UserBase):
    """Base user model with database fields."""
    id: int = Field(
        ...,
        description="Unique user identifier",
        example=123
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the user account was created",
        example="2023-01-15T10:30:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the user account was last updated",
        example="2023-01-20T14:45:00Z"
    )

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """
    User model for API responses.
    
    This is the public representation of a user, excluding sensitive fields.
    """
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-20T14:45:00Z"
            }
        }

class UserInDB(UserInDBBase):
    """
    User model for database storage.
    
    Internal model that includes the hashed password.
    Should never be returned in API responses.
    """
    hashed_password: str = Field(
        ...,
        description="Hashed password (internal use only)"
    )
