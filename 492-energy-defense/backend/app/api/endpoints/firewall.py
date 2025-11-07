"""
Firewall log endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import FirewallLog

router = APIRouter()


class FirewallLogResponse(BaseModel):
    """Firewall log entry"""
    id: int
    log_time: datetime
    firewall_name: str
    action: str
    source_ip: str
    source_port: Optional[int]
    dest_ip: str
    dest_port: Optional[int]
    protocol: str
    threat_level: str
    
    model_config = {"from_attributes": True}


@router.get("/logs", response_model=List[FirewallLogResponse])
async def get_firewall_logs(
    action: Optional[str] = Query(default=None),
    threat_level: Optional[str] = Query(default=None),
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[FirewallLogResponse]:
    """Get firewall logs with filtering"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(FirewallLog).where(FirewallLog.log_time >= start_time)
    
    if action:
        query = query.where(FirewallLog.action == action)
    if threat_level:
        query = query.where(FirewallLog.threat_level == threat_level)
    
    query = query.order_by(desc(FirewallLog.log_time)).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [FirewallLogResponse.model_validate(log) for log in logs]
