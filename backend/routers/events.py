"""Events query endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from middleware.rbac import get_current_user, RoleChecker
from models.database import (
    AuthenticationEvent, NetworkLog, PatchStatus, VulnerabilityScan
)
from models.schemas import (
    AuthenticationEventResponse, NetworkLogResponse,
    PatchStatusResponse, VulnerabilityScanResponse,
    TokenData, EventFilters
)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get(
    "/auth",
    response_model=List[AuthenticationEventResponse],
    dependencies=[Depends(RoleChecker(['analyst', 'admin', 'observer']))]
)
async def get_authentication_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source_ip: Optional[str] = None,
    username: Optional[str] = None,
    is_suspicious: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get authentication events with optional filters.
    
    Args:
        start_date: Filter events after this date
        end_date: Filter events before this date
        source_ip: Filter by source IP address
        username: Filter by username
        is_suspicious: Filter by suspicious flag
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of authentication events
    """
    query = db.query(AuthenticationEvent)
    
    if start_date:
        query = query.filter(AuthenticationEvent.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuthenticationEvent.timestamp <= end_date)
    
    if source_ip:
        query = query.filter(AuthenticationEvent.source_ip == source_ip)
    
    if username:
        query = query.filter(AuthenticationEvent.username == username)
    
    if is_suspicious is not None:
        query = query.filter(AuthenticationEvent.is_suspicious == is_suspicious)
    
    events = query.order_by(AuthenticationEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return events


@router.get(
    "/network",
    response_model=List[NetworkLogResponse],
    dependencies=[Depends(RoleChecker(['analyst', 'admin', 'observer']))]
)
async def get_network_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source_ip: Optional[str] = None,
    destination_ip: Optional[str] = None,
    threat_indicator: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get network traffic logs with optional filters.
    
    Args:
        start_date: Filter logs after this date
        end_date: Filter logs before this date
        source_ip: Filter by source IP
        destination_ip: Filter by destination IP
        threat_indicator: Filter by threat type
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of network logs
    """
    query = db.query(NetworkLog)
    
    if start_date:
        query = query.filter(NetworkLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(NetworkLog.timestamp <= end_date)
    
    if source_ip:
        query = query.filter(NetworkLog.source_ip == source_ip)
    
    if destination_ip:
        query = query.filter(NetworkLog.destination_ip == destination_ip)
    
    if threat_indicator:
        query = query.filter(NetworkLog.threat_indicator == threat_indicator)
    
    logs = query.order_by(NetworkLog.timestamp.desc()).offset(offset).limit(limit).all()
    return logs


@router.get(
    "/patches",
    response_model=List[PatchStatusResponse],
    dependencies=[Depends(RoleChecker(['analyst', 'admin', 'observer']))]
)
async def get_patch_status(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    hostname: Optional[str] = None,
    severity: Optional[str] = None,
    affected_service: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get patch status records with optional filters.
    
    Args:
        start_date: Filter records after this date
        end_date: Filter records before this date
        hostname: Filter by hostname
        severity: Filter by severity level
        affected_service: Filter by affected service type
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of patch status records
    """
    query = db.query(PatchStatus)
    
    if start_date:
        query = query.filter(PatchStatus.timestamp >= start_date)
    
    if end_date:
        query = query.filter(PatchStatus.timestamp <= end_date)
    
    if hostname:
        query = query.filter(PatchStatus.hostname == hostname)
    
    if severity:
        query = query.filter(PatchStatus.severity == severity)
    
    if affected_service:
        query = query.filter(PatchStatus.affected_service == affected_service)
    
    records = query.order_by(PatchStatus.timestamp.desc()).offset(offset).limit(limit).all()
    return records


@router.get(
    "/vulnerabilities",
    response_model=List[VulnerabilityScanResponse],
    dependencies=[Depends(RoleChecker(['analyst', 'admin', 'observer']))]
)
async def get_vulnerability_scans(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    asset_id: Optional[str] = None,
    cve_id: Optional[str] = None,
    min_cvss: Optional[float] = None,
    exploit_available: Optional[bool] = None,
    asset_criticality: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get vulnerability scan results with optional filters.
    
    Args:
        start_date: Filter scans after this date
        end_date: Filter scans before this date
        asset_id: Filter by asset ID
        cve_id: Filter by CVE identifier
        min_cvss: Filter by minimum CVSS score
        exploit_available: Filter by exploit availability
        asset_criticality: Filter by asset criticality level
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of vulnerability scan results
    """
    query = db.query(VulnerabilityScan)
    
    if start_date:
        query = query.filter(VulnerabilityScan.timestamp >= start_date)
    
    if end_date:
        query = query.filter(VulnerabilityScan.timestamp <= end_date)
    
    if asset_id:
        query = query.filter(VulnerabilityScan.asset_id == asset_id)
    
    if cve_id:
        query = query.filter(VulnerabilityScan.cve_id == cve_id)
    
    if min_cvss is not None:
        query = query.filter(VulnerabilityScan.cvss_score >= min_cvss)
    
    if exploit_available is not None:
        query = query.filter(VulnerabilityScan.exploit_available == exploit_available)
    
    if asset_criticality:
        query = query.filter(VulnerabilityScan.asset_criticality == asset_criticality)
    
    scans = query.order_by(VulnerabilityScan.cvss_score.desc()).offset(offset).limit(limit).all()
    return scans


@router.get("/stats")
async def get_event_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get aggregated event statistics.
    
    Returns:
        Dictionary with event counts and statistics
    """
    # Build base queries
    auth_query = db.query(AuthenticationEvent)
    network_query = db.query(NetworkLog)
    patch_query = db.query(PatchStatus)
    vuln_query = db.query(VulnerabilityScan)
    
    # Apply date filters
    if start_date:
        auth_query = auth_query.filter(AuthenticationEvent.timestamp >= start_date)
        network_query = network_query.filter(NetworkLog.timestamp >= start_date)
        patch_query = patch_query.filter(PatchStatus.timestamp >= start_date)
        vuln_query = vuln_query.filter(VulnerabilityScan.timestamp >= start_date)
    
    if end_date:
        auth_query = auth_query.filter(AuthenticationEvent.timestamp <= end_date)
        network_query = network_query.filter(NetworkLog.timestamp <= end_date)
        patch_query = patch_query.filter(PatchStatus.timestamp <= end_date)
        vuln_query = vuln_query.filter(VulnerabilityScan.timestamp <= end_date)
    
    # Calculate statistics
    stats = {
        "total_auth_events": auth_query.count(),
        "suspicious_auth_events": auth_query.filter(AuthenticationEvent.is_suspicious == True).count(),
        "total_network_logs": network_query.count(),
        "network_threats": network_query.filter(NetworkLog.threat_indicator.isnot(None)).count(),
        "total_patch_records": patch_query.count(),
        "critical_patches": patch_query.filter(PatchStatus.severity == 'critical').count(),
        "total_vulnerabilities": vuln_query.count(),
        "critical_vulnerabilities": vuln_query.filter(VulnerabilityScan.cvss_score >= 9.0).count(),
        "exploitable_vulnerabilities": vuln_query.filter(VulnerabilityScan.exploit_available == True).count()
    }
    
    return stats
