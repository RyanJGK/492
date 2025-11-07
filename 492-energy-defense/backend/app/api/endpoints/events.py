"""
Authentication events endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import AuthEvent

router = APIRouter()


class AuthEventResponse(BaseModel):
    """Authentication event details"""
    id: int
    event_time: datetime
    event_type: str
    username: str
    source_ip: str
    success: bool
    severity: str
    failure_reason: Optional[str] = None
    
    model_config = {"from_attributes": True}


@router.get("/auth", response_model=List[AuthEventResponse])
async def get_auth_events(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    severity: Optional[str] = Query(default=None),
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
) -> List[AuthEventResponse]:
    """
    Get authentication events with filtering
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(AuthEvent).where(
        AuthEvent.event_time >= start_time
    )
    
    if severity:
        query = query.where(AuthEvent.severity == severity)
    
    query = query.order_by(desc(AuthEvent.event_time)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [AuthEventResponse.model_validate(event) for event in events]


@router.get("/auth/{event_id}", response_model=AuthEventResponse)
async def get_auth_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
) -> AuthEventResponse:
    """Get specific authentication event"""
    result = await db.execute(
        select(AuthEvent).where(AuthEvent.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    return AuthEventResponse.model_validate(event)
