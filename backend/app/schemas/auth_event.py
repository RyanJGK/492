"""Authentication event schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class AuthEventBase(BaseModel):
    """Base authentication event schema."""
    event_type: str = Field(..., pattern="^(login_success|login_failure|logout|token_refresh|password_change|account_lockout)$")
    ip_address: str
    user_agent: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    success: bool
    failure_reason: Optional[str] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class AuthEventCreate(AuthEventBase):
    """Schema for creating authentication event."""
    user_id: Optional[UUID] = None


class AuthEvent(AuthEventBase):
    """Authentication event response schema."""
    id: UUID
    user_id: Optional[UUID]
    timestamp: datetime
    
    model_config = {"from_attributes": True}
