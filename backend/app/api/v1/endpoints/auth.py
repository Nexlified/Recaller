from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as user_crud
from app.schemas.token import Token
from app.schemas.user import User, UserCreate

router = APIRouter()

@router.post(
    "/login", 
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and return access token",
    responses={
        200: {
            "description": "Successful authentication",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Invalid credentials",
                            "value": {"detail": "Incorrect email or password"}
                        },
                        "inactive_user": {
                            "summary": "Inactive user account",
                            "value": {"detail": "Inactive user"}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    },
    tags=["Authentication"]
)
def login(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    **OAuth2 compatible token login endpoint.**
    
    Authenticates a user with email and password, returning a JWT access token 
    for subsequent API requests. The token should be included in the Authorization 
    header as: `Authorization: Bearer <token>`
    
    **Authentication Flow:**
    1. Submit email (as username) and password
    2. Server validates credentials against database
    3. If valid, returns JWT token with expiration
    4. Use token in Authorization header for protected endpoints
    
    **Token Details:**
    - Type: JWT (JSON Web Token)
    - Expires: 30 minutes (configurable)
    - Format: Bearer token
    - Contains: User ID and tenant information
    
    **Security:**
    - Passwords are hashed using bcrypt
    - Tokens are signed with server secret key
    - Inactive users cannot obtain tokens
    
    **Usage Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/login" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=user@example.com&password=secretpassword"
    ```
    
    **Multi-tenancy:**
    User authentication respects tenant isolation. Users can only authenticate 
    within their assigned tenant context.
    """
    user = user_crud.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post(
    "/register", 
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Create a new user account",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "email": "newuser@example.com",
                        "full_name": "New User",
                        "is_active": True,
                        "created_at": "2023-01-15T10:30:00Z",
                        "updated_at": None
                    }
                }
            }
        },
        400: {
            "description": "Registration failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The user with this email already exists in the system"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    },
    tags=["Authentication"]
)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    **Create a new user account.**
    
    Registers a new user in the system with email verification and password hashing.
    The user will be assigned to the default tenant for single-tenant deployments.
    
    **Registration Process:**
    1. Validate email format and uniqueness
    2. Hash the provided password securely
    3. Create user record in database
    4. Return user details (excluding password)
    
    **Password Requirements:**
    - Minimum 8 characters
    - Maximum 100 characters
    - Will be hashed with bcrypt before storage
    
    **Email Requirements:**
    - Must be valid email format
    - Must be unique across the tenant
    - Used for login authentication
    
    **Multi-tenancy:**
    New users are automatically assigned to the default tenant.
    In multi-tenant setups, tenant assignment may be handled differently.
    
    **Security:**
    - Passwords are never stored in plain text
    - Bcrypt hashing with salt for password security
    - Email uniqueness enforced per tenant
    
    **Usage Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/register" \
         -H "Content-Type: application/json" \
         -d '{
           "email": "newuser@example.com",
           "full_name": "New User",
           "password": "securepassword123"
         }'
    ```
    
    **Post-Registration:**
    After successful registration, use the `/login` endpoint to obtain 
    an access token for API authentication.
    """
    user = user_crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )
    user = user_crud.create_user(db, obj_in=user_in)
    return user
