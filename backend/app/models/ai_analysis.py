"""AI analysis models for threat intelligence and recommendations."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class AIAnalysis(Base):
    """AI-generated analysis and recommendations."""
    
    __tablename__ = "ai_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_type = Column(String(100), nullable=False, index=True)
    source_data_types = Column(ARRAY(Text), nullable=False)
    source_record_ids = Column(ARRAY(UUID(as_uuid=True)))
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    confidence_score = Column(Numeric(5, 2))
    severity = Column(String(50), index=True)
    recommendations = Column(Text)
    weight_config = Column(JSONB, nullable=False)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    cached = Column(Boolean, default=False)
    analyst_feedback = Column(String(50))
    analyst_notes = Column(Text)
    analyst_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    feedback_timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    analyst = relationship("User", back_populates="ai_analyses", foreign_keys=[analyst_id])
    
    def __repr__(self):
        return f"<AIAnalysis(id={self.id}, analysis_type={self.analysis_type}, severity={self.severity})>"


class AIWeightConfig(Base):
    """AI weight configuration for customizable analysis parameters."""
    
    __tablename__ = "ai_weight_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    weights = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="weight_configs")
    
    def __repr__(self):
        return f"<AIWeightConfig(config_name={self.config_name}, is_active={self.is_active})>"
