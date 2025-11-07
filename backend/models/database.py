"""SQLAlchemy database models for Energy Defense system."""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, DECIMAL, ARRAY, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class AuthenticationEvent(Base):
    """Authentication events table."""
    __tablename__ = "authentication_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    source_ip = Column(String(45), index=True)
    username = Column(String(100), index=True)
    event_type = Column(String(50))
    failure_reason = Column(String(200))
    geolocation = Column(String(100))
    is_suspicious = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=func.now())


class PatchStatus(Base):
    """Patch status table."""
    __tablename__ = "patch_status"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    hostname = Column(String(100))
    os_type = Column(String(50))
    missing_patches = Column(ARRAY(Text))
    severity = Column(String(20), index=True)
    days_unpatched = Column(Integer)
    affected_service = Column(String(100))
    created_at = Column(TIMESTAMP, default=func.now())


class NetworkLog(Base):
    """Network logs table."""
    __tablename__ = "network_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    source_ip = Column(String(45), index=True)
    destination_ip = Column(String(45))
    port = Column(Integer)
    protocol = Column(String(20))
    bytes_transferred = Column(BIGINT)
    packet_count = Column(Integer)
    is_encrypted = Column(Boolean)
    threat_indicator = Column(String(100), index=True)
    created_at = Column(TIMESTAMP, default=func.now())


class VulnerabilityScan(Base):
    """Vulnerability scans table."""
    __tablename__ = "vulnerability_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    asset_id = Column(String(100))
    cve_id = Column(String(50), index=True)
    cvss_score = Column(DECIMAL(3, 1))
    exploit_available = Column(Boolean)
    asset_criticality = Column(String(20))
    remediation_status = Column(String(50))
    created_at = Column(TIMESTAMP, default=func.now())


class AIAnalysis(Base):
    """AI analysis results table."""
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    analysis_type = Column(String(50))
    confidence_score = Column(DECIMAL(5, 4))
    threat_level = Column(String(20), index=True)
    affected_systems = Column(ARRAY(Text))
    recommendation = Column(Text)
    false_positive_feedback = Column(Boolean, nullable=True)
    analyst_notes = Column(Text)
    created_at = Column(TIMESTAMP, default=func.now())


class ModelConfig(Base):
    """Model configuration table."""
    __tablename__ = "model_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)  # JSONB stored as text
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    updated_by = Column(String(100))


class User(Base):
    """Users table."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
