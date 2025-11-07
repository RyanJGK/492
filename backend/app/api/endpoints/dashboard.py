"""
Dashboard endpoints for data visualization and monitoring.
Provides aggregated views of security data for different user roles.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
import logging

from app.core.database import get_db
from app.core.dependencies import require_observer
from app.models.user import User
from app.models.auth_event import AuthEvent
from app.models.patch_level import PatchLevel
from app.models.vulnerability_scan import VulnerabilityScan
from app.models.firewall_log import FirewallLog
from app.models.ai_analysis import AIAnalysis
from app.schemas.auth_event import AuthEvent as AuthEventSchema
from app.schemas.patch_level import PatchLevel as PatchLevelSchema
from app.schemas.vulnerability_scan import VulnerabilityScan as VulnerabilityScanSchema
from app.schemas.firewall_log import FirewallLog as FirewallLogSchema
from app.schemas.ai_analysis import AIAnalysis as AIAnalysisSchema

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/auth-events", response_model=List[AuthEventSchema])
async def get_auth_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = None,
    success: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_observer)
):
    """
    Get authentication events with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Filter by user ID
        success: Filter by success status
        db: Database session
        current_user: Current authenticated user with observer+ role
        
    Returns:
        List[AuthEventSchema]: List of authentication events
    """
    query = select(AuthEvent)
    
    if user_id:
        query = query.where(AuthEvent.user_id == user_id)
    if success is not None:
        query = query.where(AuthEvent.success == success)
    
    query = query.order_by(desc(AuthEvent.timestamp)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return events


@router.get("/patch-levels", response_model=List[PatchLevelSchema])
async def get_patch_levels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    compliance_status: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_observer)
):
    """
    Get patch levels with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        compliance_status: Filter by compliance status
        asset_type: Filter by asset type
        db: Database session
        current_user: Current authenticated user with observer+ role
        
    Returns:
        List[PatchLevelSchema]: List of patch level records
    """
    query = select(PatchLevel)
    
    if compliance_status:
        query = query.where(PatchLevel.compliance_status == compliance_status)
    if asset_type:
        query = query.where(PatchLevel.asset_type == asset_type)
    
    query = query.order_by(desc(PatchLevel.criticality_score)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    patches = result.scalars().all()
    
    return patches


@router.get("/vulnerabilities", response_model=List[VulnerabilityScanSchema])
async def get_vulnerabilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    asset_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_observer)
):
    """
    Get vulnerability scans with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        severity: Filter by severity
        status: Filter by status
        asset_id: Filter by asset ID
        db: Database session
        current_user: Current authenticated user with observer+ role
        
    Returns:
        List[VulnerabilityScanSchema]: List of vulnerability scan records
    """
    query = select(VulnerabilityScan)
    
    if severity:
        query = query.where(VulnerabilityScan.severity == severity)
    if status:
        query = query.where(VulnerabilityScan.status == status)
    if asset_id:
        query = query.where(VulnerabilityScan.asset_id == asset_id)
    
    query = query.order_by(desc(VulnerabilityScan.cvss_score)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    vulns = result.scalars().all()
    
    return vulns


@router.get("/firewall-logs", response_model=List[FirewallLogSchema])
async def get_firewall_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    threat_detected: Optional[bool] = None,
    source_ip: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_observer)
):
    """
    Get firewall logs with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        action: Filter by action
        threat_detected: Filter by threat detection
        source_ip: Filter by source IP
        db: Database session
        current_user: Current authenticated user with observer+ role
        
    Returns:
        List[FirewallLogSchema]: List of firewall log entries
    """
    query = select(FirewallLog)
    
    if action:
        query = query.where(FirewallLog.action == action)
    if threat_detected is not None:
        query = query.where(FirewallLog.threat_detected == threat_detected)
    if source_ip:
        query = query.where(FirewallLog.source_ip == source_ip)
    
    query = query.order_by(desc(FirewallLog.timestamp)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs


@router.get("/ai-analyses", response_model=List[AIAnalysisSchema])
async def get_ai_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    analysis_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_observer)
):
    """
    Get AI analyses with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        analysis_type: Filter by analysis type
        severity: Filter by severity
        db: Database session
        current_user: Current authenticated user with observer+ role
        
    Returns:
        List[AIAnalysisSchema]: List of AI analysis records
    """
    query = select(AIAnalysis)
    
    if analysis_type:
        query = query.where(AIAnalysis.analysis_type == analysis_type)
    if severity:
        query = query.where(AIAnalysis.severity == severity)
    
    query = query.order_by(desc(AIAnalysis.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    analyses = result.scalars().all()
    
    return analyses


@router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_observer)
):
    """
    Get dashboard summary with key metrics.
    
    Args:
        db: Database session
        current_user: Current authenticated user with observer+ role
        
    Returns:
        dict: Summary statistics for the dashboard
    """
    # Get counts for last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    # Auth events
    auth_total = await db.execute(select(func.count(AuthEvent.id)))
    auth_failed_24h = await db.execute(
        select(func.count(AuthEvent.id))
        .where(and_(AuthEvent.success == False, AuthEvent.timestamp >= last_24h))
    )
    
    # Patch levels
    critical_patches = await db.execute(
        select(func.count(PatchLevel.id))
        .where(PatchLevel.compliance_status == 'critical')
    )
    
    # Vulnerabilities
    critical_vulns = await db.execute(
        select(func.count(VulnerabilityScan.id))
        .where(and_(
            VulnerabilityScan.severity == 'critical',
            VulnerabilityScan.status == 'open'
        ))
    )
    high_vulns = await db.execute(
        select(func.count(VulnerabilityScan.id))
        .where(and_(
            VulnerabilityScan.severity == 'high',
            VulnerabilityScan.status == 'open'
        ))
    )
    
    # Firewall logs
    threats_24h = await db.execute(
        select(func.count(FirewallLog.id))
        .where(and_(FirewallLog.threat_detected == True, FirewallLog.timestamp >= last_24h))
    )
    
    # AI analyses
    ai_critical = await db.execute(
        select(func.count(AIAnalysis.id))
        .where(AIAnalysis.severity == 'critical')
    )
    
    return {
        "auth_events": {
            "total": auth_total.scalar() or 0,
            "failed_24h": auth_failed_24h.scalar() or 0
        },
        "patch_compliance": {
            "critical_assets": critical_patches.scalar() or 0
        },
        "vulnerabilities": {
            "critical_open": critical_vulns.scalar() or 0,
            "high_open": high_vulns.scalar() or 0
        },
        "firewall": {
            "threats_24h": threats_24h.scalar() or 0
        },
        "ai_analysis": {
            "critical_findings": ai_critical.scalar() or 0
        },
        "generated_at": datetime.utcnow().isoformat()
    }
