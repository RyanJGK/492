"""
AI Agent endpoints for threat analysis and weight configuration.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import logging

from app.core.database import get_db
from app.core.dependencies import require_analyst, require_admin, get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.ai_analysis import AIAnalysis, AIWeightConfig
from app.schemas.ai_analysis import (
    AIAnalysis as AIAnalysisSchema,
    AIAnalysisCreate,
    AIWeightConfig as AIWeightConfigSchema,
    AIWeightConfigCreate
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AIAnalysisSchema, status_code=status.HTTP_201_CREATED)
async def request_ai_analysis(
    analysis_request: AIAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Request AI analysis on security data.
    
    Args:
        analysis_request: Analysis request data
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        AIAnalysisSchema: AI analysis results
    """
    try:
        # Forward request to AI Agent service
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.AI_AGENT_URL}/api/v1/analyze",
                json=analysis_request.model_dump()
            )
            response.raise_for_status()
            ai_response = response.json()
        
        # Store analysis in database
        analysis = AIAnalysis(**analysis_request.model_dump())
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        logger.info(f"AI analysis created: {analysis.id} by user {current_user.username}")
        return analysis
        
    except httpx.HTTPError as e:
        logger.error(f"AI Agent communication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Agent service unavailable"
        )


@router.post("/analyze/feedback/{analysis_id}")
async def submit_analysis_feedback(
    analysis_id: str,
    feedback: str,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Submit feedback on AI analysis results.
    
    Args:
        analysis_id: ID of the analysis
        feedback: Feedback classification
        notes: Optional feedback notes
        db: Database session
        current_user: Current authenticated user with analyst+ role
        
    Returns:
        dict: Success message
    """
    result = await db.execute(select(AIAnalysis).where(AIAnalysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Update feedback
    analysis.analyst_feedback = feedback
    analysis.analyst_notes = notes
    analysis.analyst_id = current_user.id
    analysis.feedback_timestamp = datetime.utcnow()
    
    await db.commit()
    
    logger.info(f"Feedback submitted for analysis {analysis_id} by {current_user.username}: {feedback}")
    
    return {"message": "Feedback submitted successfully"}


@router.get("/weights", response_model=List[AIWeightConfigSchema])
async def get_weight_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all AI weight configurations.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[AIWeightConfigSchema]: List of weight configurations
    """
    result = await db.execute(select(AIWeightConfig))
    configs = result.scalars().all()
    
    return configs


@router.get("/weights/active", response_model=AIWeightConfigSchema)
async def get_active_weight_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the currently active AI weight configuration.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        AIWeightConfigSchema: Active weight configuration
    """
    result = await db.execute(select(AIWeightConfig).where(AIWeightConfig.is_active == True))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active weight configuration found"
        )
    
    return config


@router.post("/weights", response_model=AIWeightConfigSchema, status_code=status.HTTP_201_CREATED)
async def create_weight_config(
    config: AIWeightConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new AI weight configuration (Admin only).
    
    Args:
        config: Weight configuration data
        db: Database session
        current_user: Current authenticated user with admin role
        
    Returns:
        AIWeightConfigSchema: Created weight configuration
    """
    # Check if name already exists
    result = await db.execute(select(AIWeightConfig).where(AIWeightConfig.config_name == config.config_name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuration name already exists"
        )
    
    # If setting as active, deactivate others
    if config.is_active:
        await db.execute(
            select(AIWeightConfig)
            .where(AIWeightConfig.is_active == True)
        )
        active_configs = (await db.execute(select(AIWeightConfig).where(AIWeightConfig.is_active == True))).scalars().all()
        for active in active_configs:
            active.is_active = False
    
    weight_config = AIWeightConfig(
        **config.model_dump(),
        created_by=current_user.id
    )
    
    db.add(weight_config)
    await db.commit()
    await db.refresh(weight_config)
    
    logger.info(f"Weight configuration created: {weight_config.config_name} by {current_user.username}")
    
    return weight_config


@router.put("/weights/{config_id}/activate")
async def activate_weight_config(
    config_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activate a specific weight configuration (Admin only).
    
    Args:
        config_id: Configuration ID
        db: Database session
        current_user: Current authenticated user with admin role
        
    Returns:
        dict: Success message
    """
    result = await db.execute(select(AIWeightConfig).where(AIWeightConfig.id == config_id))
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Deactivate all other configs
    active_configs = (await db.execute(select(AIWeightConfig).where(AIWeightConfig.is_active == True))).scalars().all()
    for active in active_configs:
        active.is_active = False
    
    # Activate this config
    config.is_active = True
    
    await db.commit()
    
    logger.info(f"Weight configuration activated: {config.config_name} by {current_user.username}")
    
    return {"message": f"Configuration '{config.config_name}' activated successfully"}


from datetime import datetime
