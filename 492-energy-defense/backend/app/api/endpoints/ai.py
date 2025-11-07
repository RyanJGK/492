"""
AI agent configuration and threat analysis endpoints
Handles model weight configuration (admin only) and feedback submission
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.session import get_db
from app.db.models import (
    AIModelConfig, AIThreatAnalysis, AIFeedback, User
)
from app.api.dependencies import log_audit_action, check_role_permission

logger = structlog.get_logger()
router = APIRouter()


class WeightsUpdate(BaseModel):
    """Request to update AI model weights (admin only)"""
    auth_events: float = Field(ge=0, le=1)
    vulnerability_severity: float = Field(ge=0, le=1)
    firewall_anomalies: float = Field(ge=0, le=1)
    patch_criticality: float = Field(ge=0, le=1)


class ModelConfigResponse(BaseModel):
    """AI model configuration"""
    id: int
    config_name: str
    version: str
    is_active: bool
    confidence_threshold: float
    weights: Dict[str, float]
    
    model_config = {"from_attributes": True}


class ThreatAnalysisResponse(BaseModel):
    """AI threat analysis result"""
    id: int
    analysis_id: UUID
    analysis_time: datetime
    threat_score: float
    confidence_score: float
    threat_category: str
    severity: str
    explanation: Optional[str]
    recommended_actions: Optional[List[str]]
    acknowledged: bool
    
    model_config = {"from_attributes": True}


class FeedbackSubmission(BaseModel):
    """User feedback on AI analysis"""
    analysis_id: UUID
    feedback_type: str
    accuracy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    comments: Optional[str] = None
    suggested_severity: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback submission response"""
    id: int
    analysis_id: UUID
    submitted_by: UUID
    feedback_type: str
    accuracy_rating: Optional[int]
    created_at: datetime
    
    model_config = {"from_attributes": True}


@router.get("/config/active", response_model=ModelConfigResponse)
async def get_active_config(
    db: AsyncSession = Depends(get_db),
) -> ModelConfigResponse:
    """Get currently active AI model configuration"""
    result = await db.execute(
        select(AIModelConfig).where(AIModelConfig.is_active == True)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active configuration found",
        )
    
    return ModelConfigResponse.model_validate(config)


@router.post("/config/weights")
async def update_weights(
    weights: WeightsUpdate,
    username: str = Query(..., description="Current user"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Update AI model weights (Admin only)
    Creates new configuration version with updated weights
    """
    # Get user and verify role
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update AI weights",
        )
    
    # Validate weights sum
    total_weight = (
        weights.auth_events +
        weights.vulnerability_severity +
        weights.firewall_anomalies +
        weights.patch_criticality
    )
    
    if not (0.99 <= total_weight <= 1.01):  # Allow small floating point variance
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weights must sum to 1.0, current sum: {total_weight}",
        )
    
    # Deactivate current config
    await db.execute(
        update(AIModelConfig)
        .where(AIModelConfig.is_active == True)
        .values(is_active=False)
    )
    
    # Create new configuration
    new_config = AIModelConfig(
        config_name=f"config_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        version="1.0.0",
        is_active=True,
        model_type="threat_classifier",
        weights={
            "auth_events": float(weights.auth_events),
            "vulnerability_severity": float(weights.vulnerability_severity),
            "firewall_anomalies": float(weights.firewall_anomalies),
            "patch_criticality": float(weights.patch_criticality),
        },
        created_by=user.id,
        activated_at=datetime.utcnow(),
    )
    
    db.add(new_config)
    await db.flush()
    
    # Audit log
    await log_audit_action(
        db=db,
        user_id=user.id,
        username=user.username,
        action="update_ai_weights",
        resource_type="ai_config",
        resource_id=str(new_config.id),
        changes={"weights": new_config.weights},
        metadata={"previous_config_deactivated": True},
    )
    
    await db.commit()
    
    logger.info(
        "ai_weights_updated",
        user=username,
        config_id=new_config.id,
        weights=new_config.weights,
    )
    
    return {
        "status": "success",
        "message": "AI weights updated successfully",
        "config_id": new_config.id,
        "weights": new_config.weights,
    }


@router.get("/analyses", response_model=List[ThreatAnalysisResponse])
async def get_threat_analyses(
    severity: Optional[str] = Query(default=None),
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[ThreatAnalysisResponse]:
    """Get AI threat analyses with filtering"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(AIThreatAnalysis).where(
        AIThreatAnalysis.analysis_time >= start_time
    )
    
    if severity:
        query = query.where(AIThreatAnalysis.severity == severity)
    
    query = query.order_by(desc(AIThreatAnalysis.analysis_time)).limit(limit)
    
    result = await db.execute(query)
    analyses = result.scalars().all()
    
    return [ThreatAnalysisResponse.model_validate(a) for a in analyses]


@router.get("/analyses/{analysis_id}", response_model=ThreatAnalysisResponse)
async def get_threat_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ThreatAnalysisResponse:
    """Get specific threat analysis by ID"""
    result = await db.execute(
        select(AIThreatAnalysis).where(
            AIThreatAnalysis.analysis_id == analysis_id
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    
    return ThreatAnalysisResponse.model_validate(analysis)


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackSubmission,
    username: str = Query(..., description="Current user"),
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """
    Submit evaluation feedback on AI analysis (Analyst and Admin)
    """
    # Get user
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check role permission (analyst or admin can submit feedback)
    if user.role not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and analyst users can submit feedback",
        )
    
    # Verify analysis exists
    analysis_result = await db.execute(
        select(AIThreatAnalysis).where(
            AIThreatAnalysis.analysis_id == feedback.analysis_id
        )
    )
    analysis = analysis_result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    
    # Create feedback entry
    feedback_entry = AIFeedback(
        analysis_id=feedback.analysis_id,
        submitted_by=user.id,
        feedback_type=feedback.feedback_type,
        accuracy_rating=feedback.accuracy_rating,
        comments=feedback.comments,
        suggested_severity=feedback.suggested_severity,
    )
    
    db.add(feedback_entry)
    await db.flush()
    
    # Audit log
    await log_audit_action(
        db=db,
        user_id=user.id,
        username=user.username,
        action="submit_ai_feedback",
        resource_type="ai_feedback",
        resource_id=str(feedback_entry.id),
        metadata={
            "analysis_id": str(feedback.analysis_id),
            "feedback_type": feedback.feedback_type,
        },
    )
    
    await db.commit()
    
    logger.info(
        "ai_feedback_submitted",
        user=username,
        analysis_id=str(feedback.analysis_id),
        feedback_type=feedback.feedback_type,
    )
    
    return FeedbackResponse.model_validate(feedback_entry)


@router.post("/analyses/{analysis_id}/acknowledge")
async def acknowledge_threat(
    analysis_id: UUID,
    username: str = Query(..., description="Current user"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Acknowledge a threat analysis"""
    # Get user
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update analysis
    result = await db.execute(
        update(AIThreatAnalysis)
        .where(AIThreatAnalysis.analysis_id == analysis_id)
        .values(
            acknowledged=True,
            acknowledged_by=user.id,
            acknowledged_at=datetime.utcnow(),
        )
        .returning(AIThreatAnalysis.id)
    )
    
    updated = result.scalar_one_or_none()
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    
    await db.commit()
    
    return {
        "status": "success",
        "message": "Threat analysis acknowledged",
        "analysis_id": str(analysis_id),
    }
