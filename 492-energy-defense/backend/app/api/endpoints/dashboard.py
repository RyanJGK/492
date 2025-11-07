"""
Dashboard aggregation endpoints
Provides real-time metrics and summaries for the main interface
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.session import get_db
from app.db.models import (
    AuthEvent, Vulnerability, FirewallLog, AIThreatAnalysis, Patch
)

logger = structlog.get_logger()
router = APIRouter()


class DashboardSummary(BaseModel):
    """Dashboard overview statistics"""
    total_events: int
    critical_threats: int
    high_threats: int
    open_vulnerabilities: int
    pending_patches: int
    ai_analyses_24h: int
    last_updated: datetime


class ThreatTrend(BaseModel):
    """Threat trend over time"""
    timestamp: datetime
    threat_count: int
    severity: str


class CategoryBreakdown(BaseModel):
    """Breakdown by category"""
    category: str
    count: int
    percentage: float


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    """
    Get high-level dashboard summary
    Aggregates key metrics from all data sources
    """
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    # Count auth events
    auth_count_result = await db.execute(
        select(func.count(AuthEvent.id)).where(
            AuthEvent.event_time >= last_24h
        )
    )
    total_events = auth_count_result.scalar() or 0
    
    # Count open vulnerabilities
    vuln_result = await db.execute(
        select(func.count(Vulnerability.id)).where(
            Vulnerability.status.in_(["open", "acknowledged", "in_remediation"])
        )
    )
    open_vulnerabilities = vuln_result.scalar() or 0
    
    # Count pending patches
    patch_result = await db.execute(
        select(func.count(Patch.id)).where(
            Patch.status.in_(["pending", "scheduled"])
        )
    )
    pending_patches = patch_result.scalar() or 0
    
    # Count AI analyses in last 24h
    ai_result = await db.execute(
        select(func.count(AIThreatAnalysis.id)).where(
            AIThreatAnalysis.analysis_time >= last_24h
        )
    )
    ai_analyses = ai_result.scalar() or 0
    
    # Count critical and high threats
    critical_result = await db.execute(
        select(func.count(AIThreatAnalysis.id)).where(
            and_(
                AIThreatAnalysis.severity == "critical",
                AIThreatAnalysis.analysis_time >= last_24h,
            )
        )
    )
    critical_threats = critical_result.scalar() or 0
    
    high_result = await db.execute(
        select(func.count(AIThreatAnalysis.id)).where(
            and_(
                AIThreatAnalysis.severity == "high",
                AIThreatAnalysis.analysis_time >= last_24h,
            )
        )
    )
    high_threats = high_result.scalar() or 0
    
    return DashboardSummary(
        total_events=total_events,
        critical_threats=critical_threats,
        high_threats=high_threats,
        open_vulnerabilities=open_vulnerabilities,
        pending_patches=pending_patches,
        ai_analyses_24h=ai_analyses,
        last_updated=now,
    )


@router.get("/threats/trends", response_model=List[ThreatTrend])
async def get_threat_trends(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
) -> List[ThreatTrend]:
    """
    Get threat trends over time
    Returns hourly aggregation of threat counts by severity
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Query AI threat analyses grouped by hour and severity
    result = await db.execute(
        select(
            func.date_trunc("hour", AIThreatAnalysis.analysis_time).label("hour"),
            AIThreatAnalysis.severity,
            func.count(AIThreatAnalysis.id).label("count"),
        )
        .where(AIThreatAnalysis.analysis_time >= start_time)
        .group_by("hour", AIThreatAnalysis.severity)
        .order_by("hour")
    )
    
    trends = []
    for row in result:
        trends.append(
            ThreatTrend(
                timestamp=row.hour,
                threat_count=row.count,
                severity=row.severity,
            )
        )
    
    return trends


@router.get("/threats/categories", response_model=List[CategoryBreakdown])
async def get_threat_categories(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
) -> List[CategoryBreakdown]:
    """
    Get threat breakdown by category
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(
            AIThreatAnalysis.threat_category,
            func.count(AIThreatAnalysis.id).label("count"),
        )
        .where(AIThreatAnalysis.analysis_time >= start_time)
        .group_by(AIThreatAnalysis.threat_category)
        .order_by(func.count(AIThreatAnalysis.id).desc())
    )
    
    rows = result.all()
    total = sum(row.count for row in rows)
    
    breakdowns = []
    for row in rows:
        percentage = (row.count / total * 100) if total > 0 else 0
        breakdowns.append(
            CategoryBreakdown(
                category=row.threat_category,
                count=row.count,
                percentage=round(percentage, 2),
            )
        )
    
    return breakdowns


@router.get("/vulnerabilities/by-severity", response_model=Dict[str, int])
async def get_vulnerabilities_by_severity(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int]:
    """Get vulnerability counts grouped by severity"""
    result = await db.execute(
        select(
            Vulnerability.severity,
            func.count(Vulnerability.id).label("count"),
        )
        .where(Vulnerability.status.in_(["open", "acknowledged", "in_remediation"]))
        .group_by(Vulnerability.severity)
    )
    
    severity_counts = {row.severity: row.count for row in result}
    
    # Ensure all severities are present
    for severity in ["critical", "high", "medium", "low", "info"]:
        if severity not in severity_counts:
            severity_counts[severity] = 0
    
    return severity_counts


@router.get("/firewall/top-blocked-ips", response_model=List[Dict[str, Any]])
async def get_top_blocked_ips(
    limit: int = Query(default=10, ge=1, le=50),
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get most frequently blocked IP addresses"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(
            FirewallLog.source_ip,
            func.count(FirewallLog.id).label("block_count"),
            func.max(FirewallLog.threat_level).label("max_threat"),
        )
        .where(
            and_(
                FirewallLog.action.in_(["deny", "drop", "reject"]),
                FirewallLog.log_time >= start_time,
            )
        )
        .group_by(FirewallLog.source_ip)
        .order_by(func.count(FirewallLog.id).desc())
        .limit(limit)
    )
    
    blocked_ips = []
    for row in result:
        blocked_ips.append({
            "source_ip": str(row.source_ip),
            "block_count": row.block_count,
            "max_threat_level": row.max_threat,
        })
    
    return blocked_ips


@router.get("/system-health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get overall system health indicators
    """
    # Check data freshness
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    auth_recent = await db.execute(
        select(func.max(AuthEvent.event_time))
    )
    last_auth = auth_recent.scalar()
    
    firewall_recent = await db.execute(
        select(func.max(FirewallLog.log_time))
    )
    last_firewall = firewall_recent.scalar()
    
    ai_recent = await db.execute(
        select(func.max(AIThreatAnalysis.analysis_time))
    )
    last_ai = ai_recent.scalar()
    
    return {
        "status": "operational",
        "database": "connected",
        "data_sources": {
            "auth_events": {
                "status": "active" if last_auth and last_auth >= last_24h else "stale",
                "last_event": last_auth.isoformat() if last_auth else None,
            },
            "firewall_logs": {
                "status": "active" if last_firewall and last_firewall >= last_24h else "stale",
                "last_event": last_firewall.isoformat() if last_firewall else None,
            },
            "ai_analysis": {
                "status": "active" if last_ai and last_ai >= last_24h else "stale",
                "last_analysis": last_ai.isoformat() if last_ai else None,
            },
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
