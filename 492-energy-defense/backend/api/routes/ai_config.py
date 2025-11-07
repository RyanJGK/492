"""
AI configuration routes - Admin only access to weighting parameters
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from api.database import get_db
from api.models import User, AIWeightConfig
from api.schemas import (
    AIWeightConfigCreate,
    AIWeightConfigUpdate,
    AIWeightConfigResponse
)
from api.middleware.auth import require_admin

router = APIRouter(prefix="/ai-config", tags=["ai-configuration"])


@router.get("/", response_model=List[AIWeightConfigResponse])
async def list_ai_configs(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all AI weight configurations
    Admin only
    """
    result = await db.execute(
        select(AIWeightConfig).order_by(AIWeightConfig.created_at.desc())
    )
    configs = result.scalars().all()
    return configs


@router.get("/active", response_model=AIWeightConfigResponse)
async def get_active_config(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get currently active AI weight configuration"""
    result = await db.execute(
        select(AIWeightConfig).where(AIWeightConfig.is_active == True)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="No active configuration found")
    
    return config


@router.post("/", response_model=AIWeightConfigResponse)
async def create_ai_config(
    config: AIWeightConfigCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new AI weight configuration
    Admin only - controls how AI agent weighs different data sources
    """
    # If setting as active, deactivate others
    if config.is_active:
        await db.execute(
            update(AIWeightConfig)
            .where(AIWeightConfig.is_active == True)
            .values(is_active=False)
        )
    
    db_config = AIWeightConfig(
        **config.dict(),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    
    return db_config


@router.patch("/{config_id}", response_model=AIWeightConfigResponse)
async def update_ai_config(
    config_id: int,
    config_update: AIWeightConfigUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update AI weight configuration
    Admin only - version control for traceability
    """
    result = await db.execute(
        select(AIWeightConfig).where(AIWeightConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # If activating this config, deactivate others
    if config_update.is_active:
        await db.execute(
            update(AIWeightConfig)
            .where(AIWeightConfig.is_active == True)
            .values(is_active=False)
        )
    
    # Increment version if weights changed
    if config_update.weights and config_update.weights != config.weights:
        config.config_version += 1
    
    # Update fields
    for field, value in config_update.dict(exclude_unset=True).items():
        setattr(config, field, value)
    
    config.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(config)
    
    return config


@router.delete("/{config_id}")
async def delete_ai_config(
    config_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete AI weight configuration (Admin only)"""
    result = await db.execute(
        select(AIWeightConfig).where(AIWeightConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if config.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete active configuration"
        )
    
    await db.delete(config)
    await db.commit()
    
    return {"message": "Configuration deleted successfully"}
