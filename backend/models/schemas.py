"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Authentication schemas
class UserLogin(BaseModel):
    """User login request."""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """User information response."""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Event schemas
class AuthenticationEventResponse(BaseModel):
    """Authentication event response."""
    id: int
    timestamp: datetime
    source_ip: Optional[str]
    username: Optional[str]
    event_type: Optional[str]
    failure_reason: Optional[str]
    geolocation: Optional[str]
    is_suspicious: bool
    
    class Config:
        from_attributes = True


class PatchStatusResponse(BaseModel):
    """Patch status response."""
    id: int
    timestamp: datetime
    hostname: Optional[str]
    os_type: Optional[str]
    missing_patches: List[str]
    severity: Optional[str]
    days_unpatched: Optional[int]
    affected_service: Optional[str]
    
    class Config:
        from_attributes = True


class NetworkLogResponse(BaseModel):
    """Network log response."""
    id: int
    timestamp: datetime
    source_ip: Optional[str]
    destination_ip: Optional[str]
    port: Optional[int]
    protocol: Optional[str]
    bytes_transferred: Optional[int]
    packet_count: Optional[int]
    is_encrypted: Optional[bool]
    threat_indicator: Optional[str]
    
    class Config:
        from_attributes = True


class VulnerabilityScanResponse(BaseModel):
    """Vulnerability scan response."""
    id: int
    timestamp: datetime
    asset_id: Optional[str]
    cve_id: Optional[str]
    cvss_score: Optional[Decimal]
    exploit_available: Optional[bool]
    asset_criticality: Optional[str]
    remediation_status: Optional[str]
    
    class Config:
        from_attributes = True


class AIAnalysisResponse(BaseModel):
    """AI analysis response."""
    id: int
    timestamp: datetime
    analysis_type: Optional[str]
    confidence_score: Optional[Decimal]
    threat_level: Optional[str]
    affected_systems: List[str]
    recommendation: Optional[str]
    false_positive_feedback: Optional[bool]
    analyst_notes: Optional[str]
    
    class Config:
        from_attributes = True


# Analysis request schemas
class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection analysis."""
    start_date: datetime
    end_date: datetime
    event_type: str = Field(..., description="Type of events to analyze: 'auth', 'network', 'vulnerability'")


class FeedbackRequest(BaseModel):
    """Request to submit false positive feedback."""
    analysis_id: int
    is_false_positive: bool
    notes: Optional[str] = None


# Configuration schemas
class ModelWeightsUpdate(BaseModel):
    """Request to update model weights."""
    config_key: str
    weights: dict[str, float]


class ReplayControlRequest(BaseModel):
    """Request to control data replay."""
    action: str = Field(..., description="Action: 'start', 'pause', 'reset'")
    scenario: Optional[str] = Field(None, description="Scenario name: 'scada_brute_force', 'eternalblue', etc.")


# Dashboard schemas
class ThreatOverview(BaseModel):
    """Threat overview for dashboard."""
    threat_level: str
    confidence_score: float
    active_threats: int
    affected_systems: List[str]
    recent_alerts: List[AIAnalysisResponse]


class EventFilters(BaseModel):
    """Query filters for events."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source_ip: Optional[str] = None
    threat_level: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)
