"""
SQLAlchemy ORM models for Energy Defense database
Maintains 1:1 mapping with database schema
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, JSON, Enum as SQLEnum, DECIMAL, ARRAY, Float
)
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from api.database import Base


# Enum types matching database
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    OBSERVER = "observer"


class SeverityLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventStatus(str, enum.Enum):
    PENDING = "pending"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class User(Base):
    """User model with RBAC"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.OBSERVER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    auth_events = relationship("AuthEvent", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("AIAnalysis", foreign_keys="AIAnalysis.created_by", back_populates="creator")
    feedbacks = relationship("AIFeedback", back_populates="analyst")


class AuthEvent(Base):
    """Authentication event logging"""
    __tablename__ = "auth_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    event_type = Column(String(50), nullable=False)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="auth_events")


class PatchLevel(Base):
    """System patch level tracking"""
    __tablename__ = "patch_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String(255), nullable=False)
    component_name = Column(String(255), nullable=False)
    current_version = Column(String(100))
    latest_version = Column(String(100))
    patch_status = Column(String(50))
    severity = Column(SQLEnum(SeverityLevel), index=True)
    cve_ids = Column(ARRAY(Text))
    last_patched = Column(DateTime(timezone=True))
    next_scheduled_patch = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VulnerabilityScan(Base):
    """Vulnerability scan results"""
    __tablename__ = "vulnerability_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    target_system = Column(String(255), nullable=False)
    scan_type = Column(String(100))
    severity = Column(SQLEnum(SeverityLevel), index=True)
    vulnerability_name = Column(String(255))
    vulnerability_description = Column(Text)
    cve_id = Column(String(50))
    cvss_score = Column(DECIMAL(3, 1))
    affected_component = Column(String(255))
    remediation_steps = Column(Text)
    scan_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLEnum(EventStatus), default=EventStatus.PENDING, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON)


class FirewallLog(Base):
    """Firewall event logging"""
    __tablename__ = "firewall_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    source_ip = Column(INET, nullable=False, index=True)
    destination_ip = Column(INET, nullable=False)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String(20))
    action = Column(String(20))
    rule_id = Column(String(100))
    packet_size = Column(Integer)
    flags = Column(Text)
    severity = Column(SQLEnum(SeverityLevel))
    threat_indicator = Column(Boolean, default=False, index=True)
    country_code = Column(String(5))
    metadata = Column(JSON)


class AIAnalysis(Base):
    """AI agent analysis results with audit trail"""
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    analysis_type = Column(String(100), index=True)
    input_data = Column(JSON, nullable=False)
    ai_response = Column(Text)
    confidence_score = Column(DECIMAL(5, 4))
    threat_level = Column(SQLEnum(SeverityLevel))
    recommendations = Column(Text)
    data_sources = Column(ARRAY(Text))
    weight_configuration = Column(JSON)
    model_version = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    creator = relationship("User", foreign_keys=[created_by], back_populates="analyses")
    feedbacks = relationship("AIFeedback", back_populates="analysis")


class AIWeightConfig(Base):
    """AI weighting configuration (Admin-only access)"""
    __tablename__ = "ai_weight_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_name = Column(String(255), unique=True, nullable=False)
    config_version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=False)
    weights = Column(JSON, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))


class AIFeedback(Base):
    """Analyst feedback on AI accuracy"""
    __tablename__ = "ai_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("ai_analysis.analysis_id"))
    analyst_id = Column(Integer, ForeignKey("users.id"))
    accuracy_rating = Column(Integer)  # 1-5 scale
    is_accurate = Column(Boolean)
    false_positive = Column(Boolean)
    false_negative = Column(Boolean)
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    analysis = relationship("AIAnalysis", back_populates="feedbacks")
    analyst = relationship("User", back_populates="feedbacks")


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(Integer)
    changes = Column(JSON)
    ip_address = Column(INET)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
