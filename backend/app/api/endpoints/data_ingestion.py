"""
Data ingestion endpoints for receiving security data.
Handles auth events, patch levels, vulnerabilities, and firewall logs.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.core.dependencies import require_analyst
from app.models.user import User
from app.models.auth_event import AuthEvent
from app.models.patch_level import PatchLevel
from app.models.vulnerability_scan import VulnerabilityScan
from app.models.firewall_log import FirewallLog
from app.schemas.auth_event import AuthEvent as AuthEventSchema, AuthEventCreate
from app.schemas.patch_level import PatchLevel as PatchLevelSchema, PatchLevelCreate
from app.schemas.vulnerability_scan import VulnerabilityScan as VulnerabilityScanSchema, VulnerabilityScanCreate
from app.schemas.firewall_log import FirewallLog as FirewallLogSchema, FirewallLogCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth-events", response_model=AuthEventSchema, status_code=status.HTTP_201_CREATED)
async def create_auth_event(
    event: AuthEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Ingest authentication event data.
    
    Args:
        event: Authentication event data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        AuthEventSchema: Created authentication event
    """
    auth_event = AuthEvent(**event.model_dump())
    db.add(auth_event)
    await db.commit()
    await db.refresh(auth_event)
    
    logger.info(f"Auth event created: {auth_event.id} by user {current_user.username}")
    return auth_event


@router.post("/auth-events/bulk", response_model=List[AuthEventSchema], status_code=status.HTTP_201_CREATED)
async def create_auth_events_bulk(
    events: List[AuthEventCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Bulk ingest authentication events.
    
    Args:
        events: List of authentication event data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        List[AuthEventSchema]: Created authentication events
    """
    auth_events = [AuthEvent(**event.model_dump()) for event in events]
    db.add_all(auth_events)
    await db.commit()
    
    for event in auth_events:
        await db.refresh(event)
    
    logger.info(f"Bulk created {len(auth_events)} auth events by user {current_user.username}")
    return auth_events


@router.post("/patch-levels", response_model=PatchLevelSchema, status_code=status.HTTP_201_CREATED)
async def create_patch_level(
    patch: PatchLevelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Ingest patch level data.
    
    Args:
        patch: Patch level data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        PatchLevelSchema: Created patch level record
    """
    patch_level = PatchLevel(**patch.model_dump())
    db.add(patch_level)
    await db.commit()
    await db.refresh(patch_level)
    
    logger.info(f"Patch level created: {patch_level.id} for asset {patch_level.asset_id}")
    return patch_level


@router.post("/patch-levels/bulk", response_model=List[PatchLevelSchema], status_code=status.HTTP_201_CREATED)
async def create_patch_levels_bulk(
    patches: List[PatchLevelCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Bulk ingest patch levels.
    
    Args:
        patches: List of patch level data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        List[PatchLevelSchema]: Created patch level records
    """
    patch_levels = [PatchLevel(**patch.model_dump()) for patch in patches]
    db.add_all(patch_levels)
    await db.commit()
    
    for patch in patch_levels:
        await db.refresh(patch)
    
    logger.info(f"Bulk created {len(patch_levels)} patch levels")
    return patch_levels


@router.post("/vulnerabilities", response_model=VulnerabilityScanSchema, status_code=status.HTTP_201_CREATED)
async def create_vulnerability_scan(
    vuln: VulnerabilityScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Ingest vulnerability scan data.
    
    Args:
        vuln: Vulnerability scan data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        VulnerabilityScanSchema: Created vulnerability scan record
    """
    vulnerability = VulnerabilityScan(**vuln.model_dump())
    db.add(vulnerability)
    await db.commit()
    await db.refresh(vulnerability)
    
    logger.info(f"Vulnerability scan created: {vulnerability.id} for asset {vulnerability.asset_id}")
    return vulnerability


@router.post("/vulnerabilities/bulk", response_model=List[VulnerabilityScanSchema], status_code=status.HTTP_201_CREATED)
async def create_vulnerability_scans_bulk(
    vulns: List[VulnerabilityScanCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Bulk ingest vulnerability scans.
    
    Args:
        vulns: List of vulnerability scan data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        List[VulnerabilityScanSchema]: Created vulnerability scan records
    """
    vulnerabilities = [VulnerabilityScan(**vuln.model_dump()) for vuln in vulns]
    db.add_all(vulnerabilities)
    await db.commit()
    
    for vuln in vulnerabilities:
        await db.refresh(vuln)
    
    logger.info(f"Bulk created {len(vulnerabilities)} vulnerability scans")
    return vulnerabilities


@router.post("/firewall-logs", response_model=FirewallLogSchema, status_code=status.HTTP_201_CREATED)
async def create_firewall_log(
    log: FirewallLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Ingest firewall log data.
    
    Args:
        log: Firewall log data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        FirewallLogSchema: Created firewall log entry
    """
    firewall_log = FirewallLog(**log.model_dump())
    db.add(firewall_log)
    await db.commit()
    await db.refresh(firewall_log)
    
    logger.info(f"Firewall log created: {firewall_log.id}")
    return firewall_log


@router.post("/firewall-logs/bulk", response_model=List[FirewallLogSchema], status_code=status.HTTP_201_CREATED)
async def create_firewall_logs_bulk(
    logs: List[FirewallLogCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Bulk ingest firewall logs.
    
    Args:
        logs: List of firewall log data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        List[FirewallLogSchema]: Created firewall log entries
    """
    firewall_logs = [FirewallLog(**log.model_dump()) for log in logs]
    db.add_all(firewall_logs)
    await db.commit()
    
    for log in firewall_logs:
        await db.refresh(log)
    
    logger.info(f"Bulk created {len(firewall_logs)} firewall logs")
    return firewall_logs
