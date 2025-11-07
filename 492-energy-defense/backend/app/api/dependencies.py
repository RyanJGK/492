"""
Shared dependencies for API endpoints
Provides reusable functionality across routes
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.models import AuditLog

logger = structlog.get_logger()


async def log_audit_action(
    db: AsyncSession,
    action: str,
    resource_type: str,
    user_id: Optional[UUID] = None,
    username: Optional[str] = None,
    resource_id: Optional[str] = None,
    changes: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> AuditLog:
    """
    Create an audit log entry
    Used to track all system actions for compliance and traceability
    """
    audit_entry = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message,
        metadata=metadata or {},
    )
    
    db.add(audit_entry)
    await db.flush()
    
    logger.info(
        "audit_logged",
        action=action,
        resource_type=resource_type,
        user=username,
        success=success,
    )
    
    return audit_entry


def check_role_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user role has required permissions
    Role hierarchy: admin > analyst > observer
    """
    role_hierarchy = {
        "admin": 3,
        "analyst": 2,
        "observer": 1,
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level
