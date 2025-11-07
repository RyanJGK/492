"""
Threat analysis endpoints
Provides AI-powered threat scoring and classification
"""

from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
import structlog

from app.ml.model_manager import ModelManager

logger = structlog.get_logger()
router = APIRouter()


class ThreatAnalysisRequest(BaseModel):
    """Request for threat analysis"""
    auth_score: float = Field(ge=0, le=1, description="Authentication anomaly score")
    vuln_score: float = Field(ge=0, le=1, description="Vulnerability severity score")
    firewall_score: float = Field(ge=0, le=1, description="Firewall anomaly score")
    patch_score: float = Field(ge=0, le=1, description="Patch criticality score")


class ThreatAnalysisResponse(BaseModel):
    """Threat analysis result with explainability"""
    threat_score: float
    confidence_score: float
    threat_category: str
    severity: str
    explanation: str
    recommended_actions: list[str]
    weight_application: Dict[str, float]
    contributing_events: Dict[str, Any]
    model_version: str
    analysis_time: str


def get_model_manager(request: Request) -> ModelManager:
    """Get model manager from app state"""
    return request.app.state.model_manager


@router.post("/", response_model=ThreatAnalysisResponse)
async def analyze_threat(
    request: ThreatAnalysisRequest,
    model_manager: ModelManager = Depends(get_model_manager),
) -> ThreatAnalysisResponse:
    """
    Perform AI threat analysis
    
    Analyzes security event scores using TensorFlow model with configurable weights
    Returns threat classification with explainability and recommendations
    """
    logger.info(
        "threat_analysis_requested",
        auth_score=request.auth_score,
        vuln_score=request.vuln_score,
        firewall_score=request.firewall_score,
        patch_score=request.patch_score,
    )
    
    result = await model_manager.analyze_threat(
        auth_score=request.auth_score,
        vuln_score=request.vuln_score,
        firewall_score=request.firewall_score,
        patch_score=request.patch_score,
    )
    
    logger.info(
        "threat_analysis_completed",
        threat_score=result["threat_score"],
        severity=result["severity"],
        category=result["threat_category"],
    )
    
    return ThreatAnalysisResponse(**result)


@router.post("/batch")
async def analyze_threats_batch(
    requests: list[ThreatAnalysisRequest],
    model_manager: ModelManager = Depends(get_model_manager),
) -> list[ThreatAnalysisResponse]:
    """
    Batch threat analysis
    Processes multiple threat analyses efficiently
    """
    results = []
    
    for req in requests:
        result = await model_manager.analyze_threat(
            auth_score=req.auth_score,
            vuln_score=req.vuln_score,
            firewall_score=req.firewall_score,
            patch_score=req.patch_score,
        )
        results.append(ThreatAnalysisResponse(**result))
    
    logger.info("batch_analysis_completed", count=len(results))
    
    return results
