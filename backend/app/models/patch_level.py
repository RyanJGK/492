"""Patch level model for asset vulnerability tracking."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base


class PatchLevel(Base):
    """Asset patch level tracking for compliance monitoring."""
    
    __tablename__ = "patch_levels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String(255), nullable=False, index=True)
    asset_name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)
    operating_system = Column(String(255))
    current_patch_level = Column(String(100))
    latest_patch_level = Column(String(100))
    missing_critical_patches = Column(Integer, default=0)
    missing_high_patches = Column(Integer, default=0)
    missing_medium_patches = Column(Integer, default=0)
    missing_low_patches = Column(Integer, default=0)
    last_patched = Column(DateTime)
    compliance_status = Column(String(50), index=True)
    criticality_score = Column(Integer, index=True)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PatchLevel(asset_id={self.asset_id}, compliance_status={self.compliance_status})>"
