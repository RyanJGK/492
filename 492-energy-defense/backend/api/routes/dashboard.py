"""
Dashboard routes - aggregated statistics and trends
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List

from api.database import get_db
from api.models import (
    User, VulnerabilityScan, PatchLevel, FirewallLog, 
    AIAnalysis, SeverityLevel
)
from api.schemas import DashboardStats, ThreatTrend
from api.middleware.auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated dashboard statistics
    Available to all authenticated users
    """
    # Total critical vulnerabilities
    vuln_result = await db.execute(
        select(func.count(VulnerabilityScan.id))
        .where(VulnerabilityScan.severity == SeverityLevel.CRITICAL)
    )
    critical_vulns = vuln_result.scalar() or 0
    
    # Pending patches
    patch_result = await db.execute(
        select(func.count(PatchLevel.id))
        .where(PatchLevel.patch_status == 'outdated')
    )
    pending_patches = patch_result.scalar() or 0
    
    # Firewall blocks today
    today = datetime.utcnow().date()
    firewall_result = await db.execute(
        select(func.count(FirewallLog.id))
        .where(
            and_(
                FirewallLog.action == 'deny',
                func.date(FirewallLog.log_timestamp) == today
            )
        )
    )
    firewall_blocks = firewall_result.scalar() or 0
    
    # Total threats (high severity firewall events)
    threat_result = await db.execute(
        select(func.count(FirewallLog.id))
        .where(FirewallLog.threat_indicator == True)
    )
    total_threats = threat_result.scalar() or 0
    
    # AI analyses count
    ai_result = await db.execute(
        select(func.count(AIAnalysis.id))
    )
    ai_count = ai_result.scalar() or 0
    
    # Average AI confidence
    confidence_result = await db.execute(
        select(func.avg(AIAnalysis.confidence_score))
    )
    avg_confidence = confidence_result.scalar()
    
    return DashboardStats(
        total_threats=total_threats,
        critical_vulnerabilities=critical_vulns,
        pending_patches=pending_patches,
        firewall_blocks_today=firewall_blocks,
        ai_analyses_count=ai_count,
        average_confidence=float(avg_confidence) if avg_confidence else None
    )


@router.get("/trends/threats", response_model=List[ThreatTrend])
async def get_threat_trends(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get threat trends over time
    Returns daily counts grouped by severity
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.date(FirewallLog.log_timestamp).label('date'),
            FirewallLog.severity,
            func.count(FirewallLog.id).label('count')
        )
        .where(
            and_(
                FirewallLog.threat_indicator == True,
                FirewallLog.log_timestamp >= start_date
            )
        )
        .group_by(func.date(FirewallLog.log_timestamp), FirewallLog.severity)
        .order_by(func.date(FirewallLog.log_timestamp))
    )
    
    trends = []
    for row in result:
        trends.append(ThreatTrend(
            date=row.date,
            count=row.count,
            severity=row.severity
        ))
    
    return trends
