"""
Vulnerability scan routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from api.database import get_db
from api.models import User, VulnerabilityScan, SeverityLevel, EventStatus
from api.schemas import VulnerabilityScanCreate, VulnerabilityScanResponse
from api.middleware.auth import get_current_active_user, require_analyst

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("/", response_model=List[VulnerabilityScanResponse])
async def list_vulnerabilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[SeverityLevel] = None,
    status: Optional[EventStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List vulnerability scans with filtering
    Available to all authenticated users
    """
    query = select(VulnerabilityScan)
    
    if severity:
        query = query.where(VulnerabilityScan.severity == severity)
    if status:
        query = query.where(VulnerabilityScan.status == status)
    
    query = query.offset(skip).limit(limit).order_by(VulnerabilityScan.scan_timestamp.desc())
    
    result = await db.execute(query)
    vulnerabilities = result.scalars().all()
    
    return vulnerabilities


@router.get("/{scan_id}", response_model=VulnerabilityScanResponse)
async def get_vulnerability(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific vulnerability scan by ID"""
    result = await db.execute(
        select(VulnerabilityScan).where(VulnerabilityScan.scan_id == scan_id)
    )
    vulnerability = result.scalar_one_or_none()
    
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability scan not found")
    
    return vulnerability


@router.post("/", response_model=VulnerabilityScanResponse)
async def create_vulnerability(
    vulnerability: VulnerabilityScanCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new vulnerability scan record
    Requires Analyst or Admin role
    """
    db_vulnerability = VulnerabilityScan(**vulnerability.dict())
    db.add(db_vulnerability)
    await db.commit()
    await db.refresh(db_vulnerability)
    
    return db_vulnerability


@router.get("/stats/summary")
async def get_vulnerability_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get vulnerability statistics summary"""
    result = await db.execute(
        select(
            VulnerabilityScan.severity,
            func.count(VulnerabilityScan.id).label('count')
        )
        .group_by(VulnerabilityScan.severity)
    )
    
    summary = {row.severity.value: row.count for row in result}
    
    return {"severity_counts": summary}
