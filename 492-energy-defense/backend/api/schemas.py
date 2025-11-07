"""
Pydantic schemas for request/response validation
Enforces type safety and input sanitization
"""
from pydantic import BaseModel, EmailStr, Field, validator, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from api.models import UserRole, SeverityLevel, EventStatus


# ============ Authentication Schemas ============

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


# ============ User Schemas ============

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.OBSERVER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str


# ============ Auth Event Schemas ============

class AuthEventCreate(BaseModel):
    user_id: Optional[int] = None
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuthEventResponse(BaseModel):
    id: int
    event_type: str
    ip_address: Optional[str] = None
    success: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ============ Patch Level Schemas ============

class PatchLevelCreate(BaseModel):
    system_name: str = Field(..., max_length=255)
    component_name: str = Field(..., max_length=255)
    current_version: Optional[str] = None
    latest_version: Optional[str] = None
    patch_status: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    cve_ids: Optional[List[str]] = None
    last_patched: Optional[datetime] = None
    next_scheduled_patch: Optional[datetime] = None


class PatchLevelResponse(PatchLevelCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Vulnerability Scan Schemas ============

class VulnerabilityScanCreate(BaseModel):
    scan_id: UUID4
    target_system: str = Field(..., max_length=255)
    scan_type: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    vulnerability_name: Optional[str] = None
    vulnerability_description: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[Decimal] = Field(None, ge=0.0, le=10.0)
    affected_component: Optional[str] = None
    remediation_steps: Optional[str] = None
    status: EventStatus = EventStatus.PENDING
    assigned_to: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class VulnerabilityScanResponse(VulnerabilityScanCreate):
    id: int
    scan_timestamp: datetime
    
    class Config:
        from_attributes = True


# ============ Firewall Log Schemas ============

class FirewallLogCreate(BaseModel):
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = Field(None, ge=0, le=65535)
    destination_port: Optional[int] = Field(None, ge=0, le=65535)
    protocol: Optional[str] = None
    action: Optional[str] = None
    rule_id: Optional[str] = None
    packet_size: Optional[int] = None
    flags: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    threat_indicator: bool = False
    country_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FirewallLogResponse(FirewallLogCreate):
    id: int
    log_timestamp: datetime
    
    class Config:
        from_attributes = True


# ============ AI Analysis Schemas ============

class AIAnalysisRequest(BaseModel):
    analysis_type: str = Field(..., max_length=100)
    input_data: Dict[str, Any]
    data_sources: Optional[List[str]] = None


class AIAnalysisResponse(BaseModel):
    id: int
    analysis_id: UUID4
    analysis_type: str
    ai_response: Optional[str] = None
    confidence_score: Optional[Decimal] = None
    threat_level: Optional[SeverityLevel] = None
    recommendations: Optional[str] = None
    data_sources: Optional[List[str]] = None
    weight_configuration: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    created_at: datetime
    reviewed: bool
    
    class Config:
        from_attributes = True


# ============ AI Weight Config Schemas ============

class AIWeightConfigCreate(BaseModel):
    config_name: str = Field(..., max_length=255)
    weights: Dict[str, Any]
    description: Optional[str] = None
    is_active: bool = False


class AIWeightConfigUpdate(BaseModel):
    weights: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AIWeightConfigResponse(BaseModel):
    id: int
    config_name: str
    config_version: int
    is_active: bool
    weights: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ AI Feedback Schemas ============

class AIFeedbackCreate(BaseModel):
    analysis_id: UUID4
    accuracy_rating: int = Field(..., ge=1, le=5)
    is_accurate: bool
    false_positive: Optional[bool] = None
    false_negative: Optional[bool] = None
    comments: Optional[str] = None


class AIFeedbackResponse(AIFeedbackCreate):
    id: int
    analyst_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Dashboard Schemas ============

class DashboardStats(BaseModel):
    total_threats: int
    critical_vulnerabilities: int
    pending_patches: int
    firewall_blocks_today: int
    ai_analyses_count: int
    average_confidence: Optional[float] = None


class ThreatTrend(BaseModel):
    date: datetime
    count: int
    severity: SeverityLevel


# ============ Pagination Schema ============

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
