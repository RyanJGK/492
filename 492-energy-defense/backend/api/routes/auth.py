"""
Authentication routes - login, logout, token refresh
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from datetime import datetime

from api.database import get_db
from api.schemas import LoginRequest, Token, UserResponse
from api.models import User
from api.middleware.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    log_auth_event,
    get_current_active_user,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    Logs authentication attempt for audit trail
    """
    user = await authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        # Log failed login attempt
        await log_auth_event(
            db=db,
            event_type="failed_login",
            success=False,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            failure_reason="Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(last_login=datetime.utcnow())
    )
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Log successful login
    await log_auth_event(
        db=db,
        event_type="login",
        success=True,
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user (token invalidation handled client-side)
    Logs logout event for audit
    """
    await log_auth_event(
        db=db,
        event_type="logout",
        success=True,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    # Token refresh logic would go here
    # For production, implement proper refresh token validation
    current_user: User = Depends(get_current_active_user)
):
    """Refresh access token using refresh token"""
    access_token = create_access_token(
        data={"sub": current_user.username, "role": current_user.role.value}
    )
    refresh_token = create_refresh_token(data={"sub": current_user.username})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
