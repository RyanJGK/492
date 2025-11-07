"""
AI feedback routes - Analysts can rate AI accuracy
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from api.database import get_db
from api.models import User, AIFeedback, AIAnalysis
from api.schemas import AIFeedbackCreate, AIFeedbackResponse
from api.middleware.auth import require_analyst

router = APIRouter(prefix="/ai-feedback", tags=["ai-feedback"])


@router.post("/", response_model=AIFeedbackResponse)
async def submit_feedback(
    feedback: AIFeedbackCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback on AI analysis accuracy
    Analyst role required
    """
    # Verify analysis exists
    result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.analysis_id == feedback.analysis_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db_feedback = AIFeedback(
        **feedback.dict(),
        analyst_id=current_user.id
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    
    return db_feedback


@router.get("/analysis/{analysis_id}", response_model=List[AIFeedbackResponse])
async def get_analysis_feedback(
    analysis_id: UUID,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get all feedback for a specific analysis"""
    result = await db.execute(
        select(AIFeedback)
        .where(AIFeedback.analysis_id == analysis_id)
        .order_by(AIFeedback.created_at.desc())
    )
    feedbacks = result.scalars().all()
    
    return feedbacks
