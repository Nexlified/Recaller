from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import get_user_by_id
from app.db.session import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = get_user_by_id(db, int(token_data.sub), tenant_id=1)  # Using default tenant for now
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_tenant_context(request: Request) -> int:
    """
    Centralized utility to retrieve tenant ID from request context.
    
    This function extracts the tenant ID from the request state, which is populated
    by the tenant middleware. It provides consistent error handling and documentation
    for tenant context retrieval across all API endpoints.
    
    Args:
        request: FastAPI Request object containing tenant information in state
        
    Returns:
        int: The tenant ID associated with the current request
        
    Raises:
        HTTPException: If tenant context is not available in request state
        
    Example:
        ```python
        @router.get("/items")
        def get_items(
            request: Request,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_active_user)
        ):
            tenant_id = get_tenant_context(request)
            return crud.get_items(db, user_id=current_user.id, tenant_id=tenant_id)
        ```
    
    Note:
        This function relies on the tenant middleware being properly configured
        to populate request.state.tenant with a valid Tenant object.
    """
    try:
        # Check if request has state
        state = getattr(request, 'state', None)
        if state is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Tenant context not available. Please ensure tenant middleware is properly configured."
            )
        
        # Check if state has tenant
        tenant = getattr(state, 'tenant', None)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Tenant context not available. Please ensure tenant middleware is properly configured."
            )
        
        # Check if tenant has id
        tenant_id = getattr(tenant, 'id', None)
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid tenant context. Tenant ID is missing."
            )
        
        return tenant_id
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other exceptions and convert to HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tenant context: {str(e)}"
        )
