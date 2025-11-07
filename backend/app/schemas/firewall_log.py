"""Firewall log schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class FirewallLogBase(BaseModel):
    """Base firewall log schema."""
    log_id: Optional[str] = None
    timestamp: datetime
    source_ip: str
    source_port: Optional[int] = Field(None, ge=0, le=65535)
    destination_ip: str
    destination_port: Optional[int] = Field(None, ge=0, le=65535)
    protocol: str = Field(..., pattern="^(TCP|UDP|ICMP|ESP|AH|GRE|OTHER)$")
    action: str = Field(..., pattern="^(allow|deny|drop|reject)$")
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    interface: Optional[str] = None
    bytes_sent: int = 0
    bytes_received: int = 0
    session_duration: Optional[int] = None
    threat_detected: bool = False
    threat_type: Optional[str] = None
    threat_severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low|informational)$")
    geolocation: Optional[Dict[str, Any]] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class FirewallLogCreate(FirewallLogBase):
    """Schema for creating firewall log entry."""
    pass


class FirewallLog(FirewallLogBase):
    """Firewall log response schema."""
    id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}
