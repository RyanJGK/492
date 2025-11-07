"""Patch level schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class PatchLevelBase(BaseModel):
    """Base patch level schema."""
    asset_id: str
    asset_name: str
    asset_type: str = Field(..., pattern="^(server|workstation|network_device|ics_component|scada_system)$")
    operating_system: Optional[str] = None
    current_patch_level: Optional[str] = None
    latest_patch_level: Optional[str] = None
    missing_critical_patches: int = 0
    missing_high_patches: int = 0
    missing_medium_patches: int = 0
    missing_low_patches: int = 0
    last_patched: Optional[datetime] = None
    compliance_status: str = Field(..., pattern="^(compliant|non_compliant|at_risk|critical)$")
    criticality_score: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class PatchLevelCreate(PatchLevelBase):
    """Schema for creating patch level record."""
    pass


class PatchLevel(PatchLevelBase):
    """Patch level response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
