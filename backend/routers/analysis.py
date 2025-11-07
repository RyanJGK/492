"""AI analysis endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from middleware.rbac import get_current_user, RoleChecker
from services.ai_model import AIModelService
from models.database import AIAnalysis
from models.schemas import (
    AnomalyDetectionRequest, FeedbackRequest,
    AIAnalysisResponse, TokenData
)

router = APIRouter(prefix="/api/analyze", tags=["analysis"])

# Initialize AI model service
ai_service = AIModelService()


@router.post(
    "/anomaly",
    dependencies=[Depends(RoleChecker(['analyst', 'admin']))]
)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Run anomaly detection analysis on specified event type and time range.
    
    Args:
        request: Anomaly detection request with date range and event type
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Analysis results with threat level and recommendations
    """
    # Validate date range
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    # Run appropriate analysis based on event type
    if request.event_type == 'auth':
        result = ai_service.analyze_authentication_events(
            db, request.start_date, request.end_date
        )
        analysis_type = 'authentication_anomaly'
    
    elif request.event_type == 'network':
        result = ai_service.analyze_network_traffic(
            db, request.start_date, request.end_date
        )
        analysis_type = 'network_anomaly'
    
    elif request.event_type == 'vulnerability':
        result = ai_service.analyze_vulnerabilities(
            db, request.start_date, request.end_date
        )
        analysis_type = 'vulnerability_risk'
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid event_type. Must be 'auth', 'network', or 'vulnerability'"
        )
    
    # Save analysis result to database
    analysis = ai_service.save_analysis_result(
        db, analysis_type, result, datetime.now()
    )
    
    return {
        "analysis_id": analysis.id,
        "timestamp": analysis.timestamp,
        "analysis_type": analysis_type,
        "threat_level": result['threat_level'],
        "confidence": result['confidence'],
        "indicators": result['indicators'],
        "recommendation": result['recommendation'],
        "affected_systems": result['affected_systems']
    }


@router.get(
    "/threats",
    response_model=List[AIAnalysisResponse],
    dependencies=[Depends(RoleChecker(['analyst', 'admin', 'observer']))]
)
async def get_threat_analysis(
    hours: int = 24,
    threat_level: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get recent threat correlation analysis results.
    
    Args:
        hours: Number of hours to look back (default: 24)
        threat_level: Filter by threat level
        limit: Maximum number of results
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of AI analysis results
    """
    start_time = datetime.now() - timedelta(hours=hours)
    
    query = db.query(AIAnalysis).filter(
        AIAnalysis.timestamp >= start_time
    )
    
    if threat_level:
        query = query.filter(AIAnalysis.threat_level == threat_level)
    
    results = query.order_by(AIAnalysis.timestamp.desc()).limit(limit).all()
    return results


@router.post(
    "/feedback",
    dependencies=[Depends(RoleChecker(['analyst', 'admin']))]
)
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Submit false positive feedback on AI analysis.
    
    Args:
        feedback: Feedback request with analysis ID and notes
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated analysis record
    """
    # Find analysis record
    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.id == feedback.analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {feedback.analysis_id} not found"
        )
    
    # Update feedback
    analysis.false_positive_feedback = feedback.is_false_positive
    if feedback.notes:
        analysis.analyst_notes = feedback.notes
    
    db.commit()
    db.refresh(analysis)
    
    return {
        "message": "Feedback submitted successfully",
        "analysis_id": analysis.id,
        "false_positive": analysis.false_positive_feedback
    }


@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get aggregated dashboard data for threat overview.
    
    Returns:
        Dashboard data with current threat level and statistics
    """
    # Get recent analyses (last 24 hours)
    start_time = datetime.now() - timedelta(hours=24)
    
    recent_analyses = db.query(AIAnalysis).filter(
        AIAnalysis.timestamp >= start_time
    ).order_by(AIAnalysis.timestamp.desc()).all()
    
    # Calculate overall threat level
    if not recent_analyses:
        overall_threat = 'info'
        avg_confidence = 0.0
    else:
        # Find highest threat level
        threat_priority = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
        max_threat = max(recent_analyses, key=lambda x: threat_priority.get(x.threat_level, 0))
        overall_threat = max_threat.threat_level
        
        # Calculate average confidence
        confidences = [float(a.confidence_score) for a in recent_analyses if a.confidence_score]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Get affected systems
    affected_systems = set()
    for analysis in recent_analyses:
        if analysis.affected_systems:
            affected_systems.update(analysis.affected_systems)
    
    # Count active threats by level
    threat_counts = {
        'critical': len([a for a in recent_analyses if a.threat_level == 'critical']),
        'high': len([a for a in recent_analyses if a.threat_level == 'high']),
        'medium': len([a for a in recent_analyses if a.threat_level == 'medium']),
        'low': len([a for a in recent_analyses if a.threat_level == 'low'])
    }
    
    return {
        "threat_level": overall_threat,
        "confidence_score": round(avg_confidence, 4),
        "active_threats": sum(threat_counts.values()),
        "affected_systems": list(affected_systems)[:10],
        "threat_counts": threat_counts,
        "recent_alerts": [
            {
                "id": a.id,
                "timestamp": a.timestamp,
                "threat_level": a.threat_level,
                "analysis_type": a.analysis_type,
                "confidence": float(a.confidence_score) if a.confidence_score else 0.0,
                "recommendation": a.recommendation
            }
            for a in recent_analyses[:5]
        ]
    }


@router.post("/run-all-analysis")
async def run_all_analysis(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Run all analysis types on recent data (last 24 hours).
    
    This is a convenience endpoint to run all analyses at once.
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    results = {}
    
    # Authentication analysis
    try:
        auth_result = ai_service.analyze_authentication_events(db, start_time, end_time)
        auth_analysis = ai_service.save_analysis_result(db, 'authentication_anomaly', auth_result)
        results['authentication'] = {
            "analysis_id": auth_analysis.id,
            "threat_level": auth_result['threat_level'],
            "confidence": auth_result['confidence']
        }
    except Exception as e:
        results['authentication'] = {"error": str(e)}
    
    # Network analysis
    try:
        network_result = ai_service.analyze_network_traffic(db, start_time, end_time)
        network_analysis = ai_service.save_analysis_result(db, 'network_anomaly', network_result)
        results['network'] = {
            "analysis_id": network_analysis.id,
            "threat_level": network_result['threat_level'],
            "confidence": network_result['confidence']
        }
    except Exception as e:
        results['network'] = {"error": str(e)}
    
    # Vulnerability analysis
    try:
        vuln_result = ai_service.analyze_vulnerabilities(db, start_time, end_time)
        vuln_analysis = ai_service.save_analysis_result(db, 'vulnerability_risk', vuln_result)
        results['vulnerability'] = {
            "analysis_id": vuln_analysis.id,
            "threat_level": vuln_result['threat_level'],
            "confidence": vuln_result['confidence']
        }
    except Exception as e:
        results['vulnerability'] = {"error": str(e)}
    
    return {
        "message": "Analysis complete",
        "time_range": {
            "start": start_time,
            "end": end_time
        },
        "results": results
    }
