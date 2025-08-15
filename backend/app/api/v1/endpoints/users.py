from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status, Path, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps import get_tenant_context
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()

@router.get(
    "/", 
    response_model=List[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="Retrieve a paginated list of users within the current tenant",
    responses={
        200: {
            "description": "List of users retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "email": "admin@example.com",
                            "full_name": "Administrator",
                            "is_active": True,
                            "created_at": "2023-01-10T08:00:00Z",
                            "updated_at": "2023-01-15T12:30:00Z"
                        },
                        {
                            "id": 2,
                            "email": "user@example.com",
                            "full_name": "Regular User",
                            "is_active": True,
                            "created_at": "2023-01-12T10:15:00Z",
                            "updated_at": None
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        403: {
            "description": "Insufficient permissions",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    },
    tags=["User Management"]
)
def read_users(
    request: Request,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of users to skip for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of users to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **Retrieve a paginated list of users.**
    
    Returns all users within the current tenant with pagination support.
    Users can only see other users within the same tenant.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    - Active user account
    
    **Pagination:**
    - Use `skip` parameter to offset results
    - Use `limit` parameter to control page size
    - Maximum limit is 1000 users per request
    
    **Multi-tenancy:**
    - Only returns users from the authenticated user's tenant
    - Tenant isolation is automatically enforced
    
    **Usage Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=10" \
         -H "Authorization: Bearer <your-token>"
    ```
    
    **Response:**
    Returns an array of user objects without sensitive information like passwords.
    """
    tenant_id = get_tenant_context(request)
    users = user_crud.get_users(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return users

@router.get(
    "/me", 
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Retrieve the authenticated user's profile information",
    responses={
        200: {
            "description": "Current user profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "email": "john.doe@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "created_at": "2023-01-15T10:30:00Z",
                        "updated_at": "2023-01-20T14:45:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        }
    },
    tags=["User Management"]
)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **Get the current authenticated user's profile.**
    
    Returns the profile information for the currently authenticated user.
    This endpoint is commonly used to get user details after login.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    - Active user account
    
    **Security:**
    - Only returns the authenticated user's own profile
    - No sensitive information like passwords included
    
    **Usage Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/users/me" \
         -H "Authorization: Bearer <your-token>"
    ```
    
    **Common Use Cases:**
    - Display user profile in frontend applications
    - Verify token validity and get user context
    - Check user permissions and account status
    """
    return current_user

@router.put(
    "/me", 
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Update Current User Profile",
    description="Update the authenticated user's profile information",
    responses={
        200: {
            "description": "User profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "email": "john.doe@newemail.com",
                        "full_name": "John Updated Doe",
                        "is_active": True,
                        "created_at": "2023-01-15T10:30:00Z",
                        "updated_at": "2023-01-25T16:20:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "examples": {
                        "email_exists": {
                            "summary": "Email already in use",
                            "value": {"detail": "Email already registered to another user"}
                        },
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "value": {"detail": "Invalid email address format"}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
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
    tags=["User Management"]
)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None, description="New password (optional)", min_length=8),
    full_name: str = Body(None, description="Updated full name (optional)", max_length=100),
    email: str = Body(None, description="Updated email address (optional)"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **Update the current authenticated user's profile.**
    
    Allows users to update their own profile information including name, email, and password.
    All fields are optional - only provide fields you want to update.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    - Active user account
    
    **Updatable Fields:**
    - `full_name`: Display name (max 100 characters)
    - `email`: Email address (must be unique within tenant)
    - `password`: New password (min 8 characters, will be hashed)
    
    **Security:**
    - Password is hashed before storage
    - Email uniqueness is enforced within tenant
    - Users can only update their own profile
    
    **Usage Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/v1/users/me" \
         -H "Authorization: Bearer <your-token>" \
         -H "Content-Type: application/json" \
         -d '{
           "full_name": "Updated Name",
           "email": "newemail@example.com"
         }'
    ```
    
    **Password Update Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/v1/users/me" \
         -H "Authorization: Bearer <your-token>" \
         -H "Content-Type: application/json" \
         -d '{
           "password": "newsecurepassword123"
         }'
    ```
    
    **Response:**
    Returns the updated user profile. Passwords are never included in responses.
    """
    from app.core.validation import InputSanitizer
    from fastapi import HTTPException
    
    # Sanitize inputs
    try:
        if email is not None:
            email = InputSanitizer.sanitize_email(email)
        
        if full_name is not None:
            full_name = InputSanitizer.sanitize_name(full_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = user_crud.update_user(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get(
    "/{user_id}", 
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Get User by ID",
    description="Retrieve a specific user's profile by their ID",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 456,
                        "email": "other.user@example.com",
                        "full_name": "Other User",
                        "is_active": True,
                        "created_at": "2023-01-18T09:00:00Z",
                        "updated_at": "2023-01-22T11:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Insufficient permissions",
            "content": {
                "application/json": {
                    "example": {"detail": "The user doesn't have enough privileges"}
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    },
    tags=["User Management"]
)
def read_user_by_id(
    request: Request,
    user_id: int = Path(..., description="Unique identifier of the user to retrieve"),
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    **Get a specific user's profile by their ID.**
    
    Retrieves the profile of a user specified by their unique ID.
    Access is restricted based on permissions and tenant isolation.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    - Active user account
    
    **Access Control:**
    - Users can always access their own profile
    - Superusers can access any user within their tenant
    - Regular users cannot access other users' profiles
    
    **Multi-tenancy:**
    - Users can only access profiles within their tenant
    - Cross-tenant access is automatically blocked
    
    **Usage Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/users/456" \
         -H "Authorization: Bearer <your-token>"
    ```
    
    **Common Use Cases:**
    - Admin users managing team members
    - User profile lookups in team applications
    - Verification of user details by authorized personnel
    """
    tenant_id = get_tenant_context(request)
    user = user_crud.get_user_by_id(db, user_id=user_id, tenant_id=tenant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user == current_user:
        return user
    if not getattr(current_user, 'is_superuser', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The user doesn't have enough privileges"
        )
    return user

@router.put(
    "/{user_id}", 
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Update User by ID",
    description="Update a specific user's profile (admin only)",
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 456,
                        "email": "updated.user@example.com",
                        "full_name": "Updated User Name",
                        "is_active": False,
                        "created_at": "2023-01-18T09:00:00Z",
                        "updated_at": "2023-01-25T14:20:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Insufficient permissions",
            "content": {
                "application/json": {
                    "example": {"detail": "The user doesn't have enough privileges"}
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "The user with this id does not exist in the system"}
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
    tags=["User Management"]
)
def update_user(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., description="Unique identifier of the user to update"),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    **Update a user's profile by their ID (admin only).**
    
    Allows administrators to update any user's profile within their tenant.
    This endpoint is restricted to superusers for administrative purposes.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    - Superuser privileges required
    
    **Access Control:**
    - Only superusers can update other users
    - Users are restricted to their own tenant
    - All profile fields can be modified
    
    **Updatable Fields:**
    - `full_name`: Display name
    - `email`: Email address (must be unique)
    - `password`: New password (will be hashed)
    - `is_active`: Account status (enable/disable user)
    
    **Administrative Use Cases:**
    - Deactivate user accounts
    - Reset user passwords
    - Update user contact information
    - Manage team member profiles
    
    **Security:**
    - Passwords are hashed before storage
    - Email uniqueness enforced within tenant
    - Audit trail maintained for administrative changes
    
    **Usage Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/v1/users/456" \
         -H "Authorization: Bearer <admin-token>" \
         -H "Content-Type: application/json" \
         -d '{
           "full_name": "Updated Name",
           "is_active": false
         }'
    ```
    
    **Password Reset Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/v1/users/456" \
         -H "Authorization: Bearer <admin-token>" \
         -H "Content-Type: application/json" \
         -d '{
           "password": "temporarypassword123"
         }'
    ```
    """
    tenant_id = get_tenant_context(request)
    user = user_crud.get_user_by_id(db, user_id=user_id, tenant_id=tenant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist in the system",
        )
    if not getattr(current_user, 'is_superuser', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The user doesn't have enough privileges"
        )
    user = user_crud.update_user(db, db_obj=user, obj_in=user_in)
    return user
