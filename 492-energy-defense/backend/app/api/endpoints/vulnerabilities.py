"""
Vulnerability management endpoints
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Vulnerability, VulnerabilityScan

router = APIRouter()


class VulnerabilityResponse(BaseModel):
    """Vulnerability details"""
    id: int
    vuln_id: str
    title: str
    severity: str
    cvss_score: Optional[float]
    cve_id: Optional[str]
    affected_system: str
    status: str
    detected_at: datetime
    
    model_config = {"from_attributes": True}


class ScanResponse(BaseModel):
    """Vulnerability scan summary"""
    id: int
    scan_id: UUID
    scan_time: datetime
    target_system: str
    status: str
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    
    model_config = {"from_attributes": True}


@router.get("/", response_model=List[VulnerabilityResponse])
async def get_vulnerabilities(
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[VulnerabilityResponse]:
    """Get vulnerabilities with filtering"""
    query = select(Vulnerability)
    
    if status:
        query = query.where(Vulnerability.status == status)
    if severity:
        query = query.where(Vulnerability.severity == severity)
    
    query = query.order_by(desc(Vulnerability.detected_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    vulns = result.scalars().all()
    
    return [VulnerabilityResponse.model_validate(v) for v in vulns]


@router.get("/scans", response_model=List[ScanResponse])
async def get_scans(
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> List[ScanResponse]:
    """Get recent vulnerability scans"""
    result = await db.execute(
        select(VulnerabilityScan)
        .order_by(desc(VulnerabilityScan.scan_time))
        .limit(limit)
    )
    scans = result.scalars().all()
    
    return [ScanResponse.model_validate(scan) for scan in scans]
