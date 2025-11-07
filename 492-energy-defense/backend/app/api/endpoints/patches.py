"""
Patch management endpoints
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Patch

router = APIRouter()


class PatchResponse(BaseModel):
    """Patch details"""
    id: int
    patch_id: str
    system_name: str
    system_type: str
    patch_name: str
    severity: str
    status: str
    release_date: datetime
    scheduled_date: Optional[datetime]
    requires_downtime: bool
    
    model_config = {"from_attributes": True}


@router.get("/", response_model=List[PatchResponse])
async def get_patches(
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[PatchResponse]:
    """Get patches with filtering"""
    query = select(Patch)
    
    if status:
        query = query.where(Patch.status == status)
    if severity:
        query = query.where(Patch.severity == severity)
    
    query = query.order_by(desc(Patch.created_at)).limit(limit)
    
    result = await db.execute(query)
    patches = result.scalars().all()
    
    return [PatchResponse.model_validate(p) for p in patches]
