"""Admin configuration endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import json
from datetime import datetime

from database import get_db
from middleware.rbac import RoleChecker, get_current_user
from services.ai_model import AIModelService
from services.data_replay import DataReplayService
from models.database import ModelConfig
from models.schemas import ModelWeightsUpdate, ReplayControlRequest, TokenData
from config import settings

router = APIRouter(prefix="/api/config", tags=["admin"])

# Initialize services
ai_service = AIModelService()
replay_service = DataReplayService(replay_speed=settings.REPLAY_SPEED)


@router.get(
    "/model-weights",
    dependencies=[Depends(RoleChecker(['admin']))]
)
async def get_model_weights(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current model feature weights.
    
    Returns:
        Dictionary of all model weights
    """
    weights = {}
    
    # Query all weight configurations
    configs = db.query(ModelConfig).filter(
        ModelConfig.config_key.in_([
            'authentication_weights',
            'network_weights',
            'vulnerability_weights'
        ])
    ).all()
    
    for config in configs:
        try:
            weights[config.config_key] = json.loads(config.config_value)
        except json.JSONDecodeError:
            weights[config.config_key] = {}
    
    return weights


@router.put(
    "/model-weights",
    dependencies=[Depends(RoleChecker(['admin']))]
)
async def update_model_weights(
    update: ModelWeightsUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update model feature weights.
    
    Args:
        update: Model weights update request
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated weights configuration
    """
    # Validate config_key
    valid_keys = ['authentication_weights', 'network_weights', 'vulnerability_weights']
    if update.config_key not in valid_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid config_key. Must be one of: {', '.join(valid_keys)}"
        )
    
    # Validate weights sum to 1.0 (or close to it)
    weights_sum = sum(update.weights.values())
    if not (0.95 <= weights_sum <= 1.05):
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to approximately 1.0 (got {weights_sum})"
        )
    
    # Find or create configuration
    config = db.query(ModelConfig).filter(
        ModelConfig.config_key == update.config_key
    ).first()
    
    if config:
        config.config_value = json.dumps(update.weights)
        config.updated_at = datetime.now()
        config.updated_by = current_user.username
    else:
        config = ModelConfig(
            config_key=update.config_key,
            config_value=json.dumps(update.weights),
            updated_by=current_user.username
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    
    # Update AI service weights
    category = update.config_key.replace('_weights', '')
    ai_service.update_weights(category, update.weights)
    
    return {
        "message": "Model weights updated successfully",
        "config_key": config.config_key,
        "weights": json.loads(config.config_value),
        "updated_by": config.updated_by,
        "updated_at": config.updated_at
    }


@router.get("/replay-status")
async def get_replay_status(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current data replay status.
    
    Returns:
        Replay status information
    """
    return {
        "is_running": replay_service.replay_status["is_running"],
        "current_scenario": replay_service.replay_status["current_scenario"],
        "progress": replay_service.replay_status["progress"],
        "replay_speed": replay_service.replay_speed
    }


@router.post(
    "/replay-control",
    dependencies=[Depends(RoleChecker(['admin']))]
)
async def control_replay(
    request: ReplayControlRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Control data replay (start, pause, reset scenarios).
    
    Args:
        request: Replay control request
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Status message and results
    """
    if request.action not in ['start', 'pause', 'reset']:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be 'start', 'pause', or 'reset'"
        )
    
    if request.action == 'start':
        if not request.scenario:
            # Load all scenarios
            results = replay_service.load_all_scenarios(db, adjust_time=True)
            
            return {
                "message": "All scenarios loaded successfully",
                "results": results
            }
        else:
            # Load specific scenario
            scenario_methods = {
                'scada_brute_force': replay_service.load_scenario1_scada_brute_force,
                'eternalblue': replay_service.load_scenario2_eternalblue,
                'dns_tunneling': replay_service.load_scenario3_dns_tunneling,
                'port_scan': replay_service.load_scenario4_port_scan,
                'phishing': replay_service.load_scenario5_phishing
            }
            
            if request.scenario not in scenario_methods:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid scenario. Must be one of: {', '.join(scenario_methods.keys())}"
                )
            
            method = scenario_methods[request.scenario]
            result = method(db, adjust_time=True)
            
            return {
                "message": f"Scenario '{request.scenario}' loaded successfully",
                "result": result
            }
    
    elif request.action == 'pause':
        replay_service.replay_status["is_running"] = False
        return {"message": "Replay paused"}
    
    elif request.action == 'reset':
        # Clear all event tables
        from models.database import (
            AuthenticationEvent, NetworkLog, PatchStatus,
            VulnerabilityScan, AIAnalysis
        )
        
        db.query(AIAnalysis).delete()
        db.query(AuthenticationEvent).delete()
        db.query(NetworkLog).delete()
        db.query(PatchStatus).delete()
        db.query(VulnerabilityScan).delete()
        db.commit()
        
        replay_service.replay_status = {
            "is_running": False,
            "current_scenario": None,
            "progress": 0.0
        }
        
        return {"message": "All scenarios reset, event data cleared"}


@router.get(
    "/audit-log",
    dependencies=[Depends(RoleChecker(['admin']))]
)
async def get_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get configuration change audit log.
    
    Args:
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of configuration changes
    """
    configs = db.query(ModelConfig).order_by(
        ModelConfig.updated_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "config_key": c.config_key,
            "updated_at": c.updated_at,
            "updated_by": c.updated_by,
            "config_value": json.loads(c.config_value) if c.config_value else {}
        }
        for c in configs
    ]


@router.get(
    "/system-info",
    dependencies=[Depends(RoleChecker(['admin']))]
)
async def get_system_info(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get system information and statistics.
    
    Returns:
        System configuration and database statistics
    """
    from models.database import (
        AuthenticationEvent, NetworkLog, PatchStatus,
        VulnerabilityScan, AIAnalysis, User
    )
    
    # Count records in each table
    stats = {
        "database": {
            "authentication_events": db.query(AuthenticationEvent).count(),
            "network_logs": db.query(NetworkLog).count(),
            "patch_status": db.query(PatchStatus).count(),
            "vulnerability_scans": db.query(VulnerabilityScan).count(),
            "ai_analyses": db.query(AIAnalysis).count(),
            "users": db.query(User).count()
        },
        "configuration": {
            "replay_speed": settings.REPLAY_SPEED,
            "model_path": settings.MODEL_PATH,
            "jwt_expiration_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        },
        "models": {
            "loaded": len(ai_service.models),
            "available": list(ai_service.models.keys())
        }
    }
    
    return stats
