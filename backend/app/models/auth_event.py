"""Authentication event model for security monitoring."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class AuthEvent(Base):
    """Authentication event tracking for security analysis."""
    
    __tablename__ = "auth_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    event_type = Column(String(100), nullable=False)
    ip_address = Column(INET, nullable=False)
    user_agent = Column(Text)
    location = Column(JSONB)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(Text)
    risk_score = Column(Integer)
    metadata = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="auth_events")
    
    def __repr__(self):
        return f"<AuthEvent(id={self.id}, event_type={self.event_type}, success={self.success})>"
