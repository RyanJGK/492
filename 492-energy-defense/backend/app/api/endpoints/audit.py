"""
Audit log endpoints for traceability and compliance
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import AuditLog

router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log entry"""
    id: int
    timestamp: datetime
    username: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    success: bool
    error_message: Optional[str]
    
    model_config = {"from_attributes": True}


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    action: Optional[str] = Query(default=None),
    resource_type: Optional[str] = Query(default=None),
    username: Optional[str] = Query(default=None),
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[AuditLogResponse]:
    """
    Get audit logs with filtering
    Provides complete traceability of system actions
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(AuditLog).where(AuditLog.timestamp >= start_time)
    
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if username:
        query = query.where(AuditLog.username == username)
    
    query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/actions")
async def get_audit_actions(
    db: AsyncSession = Depends(get_db),
) -> List[str]:
    """Get list of distinct audit actions for filtering"""
    result = await db.execute(
        select(AuditLog.action).distinct()
    )
    actions = [row[0] for row in result]
    return sorted(actions)


@router.get("/resource-types")
async def get_resource_types(
    db: AsyncSession = Depends(get_db),
) -> List[str]:
    """Get list of distinct resource types for filtering"""
    result = await db.execute(
        select(AuditLog.resource_type).distinct()
    )
    types = [row[0] for row in result]
    return sorted(types)
