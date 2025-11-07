"""Firewall log model for network security monitoring."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
import uuid

from app.core.database import Base


class FirewallLog(Base):
    """Firewall log entries for network security analysis."""
    
    __tablename__ = "firewall_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_id = Column(String(255))
    timestamp = Column(DateTime, nullable=False, index=True)
    source_ip = Column(INET, nullable=False, index=True)
    source_port = Column(Integer)
    destination_ip = Column(INET, nullable=False, index=True)
    destination_port = Column(Integer)
    protocol = Column(String(20), nullable=False)
    action = Column(String(50), nullable=False, index=True)
    rule_id = Column(String(255))
    rule_name = Column(String(255))
    interface = Column(String(100))
    bytes_sent = Column(BigInteger, default=0)
    bytes_received = Column(BigInteger, default=0)
    session_duration = Column(Integer)
    threat_detected = Column(Boolean, default=False, index=True)
    threat_type = Column(String(100))
    threat_severity = Column(String(50))
    geolocation = Column(JSONB)
    risk_score = Column(Integer)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<FirewallLog(id={self.id}, action={self.action}, threat_detected={self.threat_detected})>"
