"""
SQLAlchemy ORM models matching the database schema
Provides type-safe database interactions
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime, Date, Numeric,
    Text, ARRAY, CheckConstraint, ForeignKey, Index, func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.session import Base


class User(Base):
    """User accounts with role-based access"""
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'analyst', 'observer')", name="valid_role"),
        Index("idx_users_username", "username"),
        Index("idx_users_role", "role"),
    )


class AuthEvent(Base):
    """Authentication and authorization events"""
    __tablename__ = "auth_events"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    source_ip: Mapped[str] = mapped_column(INET, nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_auth_events_time", "event_time", postgresql_ops={"event_time": "DESC"}),
        Index("idx_auth_events_username", "username"),
        Index("idx_auth_events_severity", "severity"),
    )


class Patch(Base):
    """System patch management"""
    __tablename__ = "patches"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patch_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    system_name: Mapped[str] = mapped_column(String(200), nullable=False)
    system_type: Mapped[str] = mapped_column(String(50), nullable=False)
    patch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patch_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    release_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    installed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cve_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    requires_downtime: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VulnerabilityScan(Base):
    """Vulnerability scan metadata"""
    __tablename__ = "vulnerability_scans"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    scan_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True, default=uuid4)
    scan_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scanner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_system: Mapped[str] = mapped_column(String(200), nullable=False)
    target_ip: Mapped[str] = mapped_column(INET, nullable=False)
    scan_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    total_vulnerabilities: Mapped[int] = mapped_column(Integer, default=0)
    critical_count: Mapped[int] = mapped_column(Integer, default=0)
    high_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_count: Mapped[int] = mapped_column(Integer, default=0)
    low_count: Mapped[int] = mapped_column(Integer, default=0)
    scan_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")


class Vulnerability(Base):
    """Individual vulnerability findings"""
    __tablename__ = "vulnerabilities"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    scan_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("vulnerability_scans.scan_id", ondelete="CASCADE"), nullable=False)
    vuln_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    cvss_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 1), nullable=True)
    cve_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    affected_system: Mapped[str] = mapped_column(String(200), nullable=False)
    affected_component: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    service: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    remediation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    scan = relationship("VulnerabilityScan", back_populates="vulnerabilities")


class FirewallLog(Base):
    """Firewall and network activity logs"""
    __tablename__ = "firewall_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    log_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    firewall_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    source_ip: Mapped[str] = mapped_column(INET, nullable=False)
    source_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dest_ip: Mapped[str] = mapped_column(INET, nullable=False)
    dest_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)
    bytes_sent: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_received: Mapped[int] = mapped_column(BigInteger, default=0)
    rule_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rule_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    threat_level: Mapped[str] = mapped_column(String(20), default="low")
    geo_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_firewall_time", "log_time", postgresql_ops={"log_time": "DESC"}),
        Index("idx_firewall_source_ip", "source_ip"),
        Index("idx_firewall_threat", "threat_level"),
    )


class AIModelConfig(Base):
    """AI model configuration and weights"""
    __tablename__ = "ai_model_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_threshold: Mapped[float] = mapped_column(Numeric(3, 2), default=0.75)
    weights: Mapped[dict] = mapped_column(JSONB, nullable=False)
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AIThreatAnalysis(Base):
    """AI-generated threat analysis results"""
    __tablename__ = "ai_threat_analyses"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    analysis_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True, default=uuid4)
    analysis_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    model_config_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_model_configs.id"), nullable=True)
    model_version: Mapped[str] = mapped_column(String(20), nullable=False)
    threat_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    threat_category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    contributing_events: Mapped[dict] = mapped_column(JSONB, nullable=False)
    weight_application: Mapped[dict] = mapped_column(JSONB, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    feedback = relationship("AIFeedback", back_populates="analysis", cascade="all, delete-orphan")


class AIFeedback(Base):
    """User feedback on AI analysis accuracy"""
    __tablename__ = "ai_feedback"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    analysis_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("ai_threat_analyses.analysis_id", ondelete="CASCADE"), nullable=False)
    submitted_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)
    accuracy_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    analysis = relationship("AIThreatAnalysis", back_populates="feedback")


class AuditLog(Base):
    """Comprehensive audit trail for all system actions"""
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    changes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp", postgresql_ops={"timestamp": "DESC"}),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_action", "action"),
    )
