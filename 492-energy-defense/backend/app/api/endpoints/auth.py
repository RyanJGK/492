"""
Authentication endpoints
Role-based access simulation for demo purposes
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.session import get_db
from app.db.models import User, AuditLog
from app.api.dependencies import log_audit_action

logger = structlog.get_logger()
router = APIRouter()


class RoleRequest(BaseModel):
    """Request to switch user role"""
    role: str
    username: Optional[str] = None


class UserResponse(BaseModel):
    """User information response"""
    id: UUID
    username: str
    role: str
    last_login: Optional[datetime]
    is_active: bool


@router.post("/switch-role", response_model=UserResponse)
async def switch_role(
    request: RoleRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Switch to a different role view (Admin/Analyst/Observer)
    For demo purposes - simulates role-based access
    """
    valid_roles = ["admin", "analyst", "observer"]
    
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )
    
    # Get or create user for the role
    username = request.username or f"{request.role}_user"
    
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create user if doesn't exist
        user = User(
            username=username,
            role=request.role,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        logger.info("user_created", username=username, role=request.role)
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Log the action
    await log_audit_action(
        db=db,
        user_id=user.id,
        username=user.username,
        action="role_switch",
        resource_type="authentication",
        resource_id=str(user.id),
        metadata={"new_role": request.role},
    )
    
    await db.commit()
    
    logger.info("role_switched", username=user.username, role=user.role)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        last_login=user.last_login,
        is_active=user.is_active,
    )


@router.get("/current-user", response_model=UserResponse)
async def get_current_user(
    username: str = "admin_user",
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get current user information
    For demo - defaults to admin_user
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        last_login=user.last_login,
        is_active=user.is_active,
    )


@router.get("/roles")
async def get_available_roles():
    """Get list of available roles with descriptions"""
    return {
        "roles": [
            {
                "name": "admin",
                "description": "Full system access including AI weight configuration",
                "capabilities": [
                    "View all dashboards and alerts",
                    "Configure AI model weights",
                    "Adjust sensitivity thresholds",
                    "Submit evaluation feedback",
                    "Access audit logs",
                ]
            },
            {
                "name": "analyst",
                "description": "Full visibility with feedback submission",
                "capabilities": [
                    "View all dashboards and alerts",
                    "Submit evaluation feedback on AI flagging",
                    "Access detailed analysis reports",
                    "View historical trends",
                ]
            },
            {
                "name": "observer",
                "description": "Read-only monitoring access",
                "capabilities": [
                    "View dashboards and summaries",
                    "Monitor real-time metrics",
                    "Access presentation views",
                ]
            },
        ]
    }
