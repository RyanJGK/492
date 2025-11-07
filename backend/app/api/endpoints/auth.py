"""
Authentication endpoints for user login and token management.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.models.auth_event import AuthEvent
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import User as UserSchema, UserCreate
from app.core.security import get_password_hash
from app.core.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        credentials: User login credentials
        request: HTTP request for IP address
        db: Database session
        
    Returns:
        Token: Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        # Log failed authentication attempt
        auth_event = AuthEvent(
            user_id=user.id if user else None,
            event_type="login_failure",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            failure_reason="Invalid credentials",
            risk_score=65
        )
        db.add(auth_event)
        await db.commit()
        
        logger.warning(f"Failed login attempt for username: {credentials.username} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Log successful authentication
    auth_event = AuthEvent(
        user_id=user.id,
        event_type="login_success",
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent", ""),
        success=True,
        risk_score=5
    )
    db.add(auth_event)
    await db.commit()
    
    logger.info(f"Successful login for user: {credentials.username} from {client_ip}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserSchema: Created user
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"New user registered: {user.username} with role: {user.role}")
    
    return user


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Args:
        user: Current authenticated user
        
    Returns:
        UserSchema: Current user information
    """
    return user
