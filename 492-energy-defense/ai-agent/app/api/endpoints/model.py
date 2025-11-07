"""
Model configuration endpoints
Handles weight updates and model status
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel, Field
import structlog

from app.ml.model_manager import ModelManager

logger = structlog.get_logger()
router = APIRouter()


class WeightsUpdate(BaseModel):
    """Model weights update request"""
    auth_events: float = Field(ge=0, le=1)
    vulnerability_severity: float = Field(ge=0, le=1)
    firewall_anomalies: float = Field(ge=0, le=1)
    patch_criticality: float = Field(ge=0, le=1)


class ModelStatus(BaseModel):
    """Model status response"""
    ready: bool
    current_weights: Dict[str, float]
    model_version: str


def get_model_manager(request: Request) -> ModelManager:
    """Get model manager from app state"""
    return request.app.state.model_manager


@router.get("/status", response_model=ModelStatus)
async def get_model_status(
    model_manager: ModelManager = Depends(get_model_manager),
) -> ModelStatus:
    """Get current model status and configuration"""
    return ModelStatus(
        ready=model_manager.is_ready(),
        current_weights=model_manager.current_weights,
        model_version="1.0.0",
    )


@router.post("/weights")
async def update_model_weights(
    weights: WeightsUpdate,
    model_manager: ModelManager = Depends(get_model_manager),
) -> Dict[str, Any]:
    """
    Update model feature weights
    
    This endpoint is called by the backend when admin users update weights
    """
    weights_dict = {
        "auth_events": weights.auth_events,
        "vulnerability_severity": weights.vulnerability_severity,
        "firewall_anomalies": weights.firewall_anomalies,
        "patch_criticality": weights.patch_criticality,
    }
    
    try:
        model_manager.update_weights(weights_dict)
        
        logger.info("model_weights_updated", weights=weights_dict)
        
        return {
            "status": "success",
            "message": "Model weights updated successfully",
            "weights": weights_dict,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/weights")
async def get_current_weights(
    model_manager: ModelManager = Depends(get_model_manager),
) -> Dict[str, float]:
    """Get current model weights"""
    return model_manager.current_weights
