"""AI analysis schemas."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class AIAnalysisBase(BaseModel):
    """Base AI analysis schema."""
    analysis_type: str = Field(..., pattern="^(threat_correlation|risk_assessment|anomaly_detection|trend_analysis|incident_prediction)$")
    source_data_types: List[str]
    source_record_ids: Optional[List[UUID]] = None
    query: str
    response: str
    confidence_score: Optional[Decimal] = Field(None, ge=0.0, le=100.0)
    severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low|informational)$")
    recommendations: Optional[str] = None
    weight_config: Dict[str, Any]
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cached: bool = False


class AIAnalysisCreate(AIAnalysisBase):
    """Schema for creating AI analysis record."""
    pass


class AIAnalysis(AIAnalysisBase):
    """AI analysis response schema."""
    id: UUID
    analyst_feedback: Optional[str] = None
    analyst_notes: Optional[str] = None
    analyst_id: Optional[UUID] = None
    feedback_timestamp: Optional[datetime] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AIWeightConfigBase(BaseModel):
    """Base AI weight configuration schema."""
    config_name: str
    description: Optional[str] = None
    weights: Dict[str, Any]
    is_active: bool = False


class AIWeightConfigCreate(AIWeightConfigBase):
    """Schema for creating AI weight configuration."""
    pass


class AIWeightConfig(AIWeightConfigBase):
    """AI weight configuration response schema."""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
