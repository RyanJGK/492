"""Role-Based Access Control middleware."""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import List, Optional
from functools import wraps

from config import settings
from models.schemas import TokenData

security = HTTPBearer()


def decode_token(token: str) -> TokenData:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData with username and role
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return TokenData(username=username, role=role)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP bearer credentials
    
    Returns:
        TokenData with user information
    """
    token = credentials.credentials
    return decode_token(token)


def require_role(allowed_roles: List[str]):
    """
    Decorator to require specific roles for endpoint access.
    
    Args:
        allowed_roles: List of allowed role names
    
    Returns:
        Decorator function
    
    Example:
        @require_role(['admin', 'analyst'])
        async def admin_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs (injected by FastAPI dependency)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class RoleChecker:
    """
    Dependency class to check user roles.
    
    Example:
        @app.get("/admin", dependencies=[Depends(RoleChecker(['admin']))])
        async def admin_endpoint():
            pass
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Initialize role checker.
        
        Args:
            allowed_roles: List of allowed role names
        """
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: TokenData = Depends(get_current_user)):
        """
        Check if current user has required role.
        
        Args:
            current_user: Current user token data
        
        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        
        return current_user
