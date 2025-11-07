-- 492-Energy-Defense Database Schema
-- PostgreSQL initialization script

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table with role-based access control
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'analyst', 'observer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Authentication events table
CREATE TABLE auth_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL CHECK (event_type IN ('login_success', 'login_failure', 'logout', 'token_refresh', 'password_change', 'account_lockout')),
    ip_address INET NOT NULL,
    user_agent TEXT,
    location JSONB,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Patch levels table
CREATE TABLE patch_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id VARCHAR(255) NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL CHECK (asset_type IN ('server', 'workstation', 'network_device', 'ics_component', 'scada_system')),
    operating_system VARCHAR(255),
    current_patch_level VARCHAR(100),
    latest_patch_level VARCHAR(100),
    missing_critical_patches INTEGER DEFAULT 0,
    missing_high_patches INTEGER DEFAULT 0,
    missing_medium_patches INTEGER DEFAULT 0,
    missing_low_patches INTEGER DEFAULT 0,
    last_patched TIMESTAMP WITH TIME ZONE,
    compliance_status VARCHAR(50) CHECK (compliance_status IN ('compliant', 'non_compliant', 'at_risk', 'critical')),
    criticality_score INTEGER CHECK (criticality_score BETWEEN 0 AND 100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vulnerability scans table
CREATE TABLE vulnerability_scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    asset_id VARCHAR(255) NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    vulnerability_id VARCHAR(255) NOT NULL,
    cve_id VARCHAR(50),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'informational')),
    cvss_score DECIMAL(3, 1) CHECK (cvss_score BETWEEN 0.0 AND 10.0),
    cvss_vector TEXT,
    title TEXT NOT NULL,
    description TEXT,
    solution TEXT,
    exploit_available BOOLEAN DEFAULT FALSE,
    exploited_in_wild BOOLEAN DEFAULT FALSE,
    patch_available BOOLEAN DEFAULT FALSE,
    affected_software TEXT,
    first_detected TIMESTAMP WITH TIME ZONE NOT NULL,
    last_detected TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'mitigated', 'remediated', 'accepted_risk', 'false_positive')),
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Firewall logs table
CREATE TABLE firewall_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source_ip INET NOT NULL,
    source_port INTEGER CHECK (source_port BETWEEN 0 AND 65535),
    destination_ip INET NOT NULL,
    destination_port INTEGER CHECK (destination_port BETWEEN 0 AND 65535),
    protocol VARCHAR(20) NOT NULL CHECK (protocol IN ('TCP', 'UDP', 'ICMP', 'ESP', 'AH', 'GRE', 'OTHER')),
    action VARCHAR(50) NOT NULL CHECK (action IN ('allow', 'deny', 'drop', 'reject')),
    rule_id VARCHAR(255),
    rule_name VARCHAR(255),
    interface VARCHAR(100),
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    session_duration INTEGER,
    threat_detected BOOLEAN DEFAULT FALSE,
    threat_type VARCHAR(100),
    threat_severity VARCHAR(50) CHECK (threat_severity IN ('critical', 'high', 'medium', 'low', 'informational')),
    geolocation JSONB,
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI agent analysis results table
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_type VARCHAR(100) NOT NULL CHECK (analysis_type IN ('threat_correlation', 'risk_assessment', 'anomaly_detection', 'trend_analysis', 'incident_prediction')),
    source_data_types TEXT[] NOT NULL,
    source_record_ids UUID[],
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    confidence_score DECIMAL(5, 2) CHECK (confidence_score BETWEEN 0.00 AND 100.00),
    severity VARCHAR(50) CHECK (severity IN ('critical', 'high', 'medium', 'low', 'informational')),
    recommendations TEXT,
    weight_config JSONB NOT NULL,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    cached BOOLEAN DEFAULT FALSE,
    analyst_feedback VARCHAR(50) CHECK (analyst_feedback IN ('accurate', 'mostly_accurate', 'needs_improvement', 'inaccurate', 'false_positive')),
    analyst_notes TEXT,
    analyst_id UUID REFERENCES users(id),
    feedback_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI weight configurations table
CREATE TABLE ai_weight_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    weights JSONB NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for all system changes
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_auth_events_user_id ON auth_events(user_id);
CREATE INDEX idx_auth_events_timestamp ON auth_events(timestamp DESC);
CREATE INDEX idx_auth_events_risk_score ON auth_events(risk_score DESC);

CREATE INDEX idx_patch_levels_asset_id ON patch_levels(asset_id);
CREATE INDEX idx_patch_levels_compliance_status ON patch_levels(compliance_status);
CREATE INDEX idx_patch_levels_criticality_score ON patch_levels(criticality_score DESC);

CREATE INDEX idx_vulnerability_scans_asset_id ON vulnerability_scans(asset_id);
CREATE INDEX idx_vulnerability_scans_severity ON vulnerability_scans(severity);
CREATE INDEX idx_vulnerability_scans_status ON vulnerability_scans(status);
CREATE INDEX idx_vulnerability_scans_cvss_score ON vulnerability_scans(cvss_score DESC);
CREATE INDEX idx_vulnerability_scans_cve_id ON vulnerability_scans(cve_id);

CREATE INDEX idx_firewall_logs_timestamp ON firewall_logs(timestamp DESC);
CREATE INDEX idx_firewall_logs_source_ip ON firewall_logs(source_ip);
CREATE INDEX idx_firewall_logs_destination_ip ON firewall_logs(destination_ip);
CREATE INDEX idx_firewall_logs_action ON firewall_logs(action);
CREATE INDEX idx_firewall_logs_threat_detected ON firewall_logs(threat_detected);

CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);
CREATE INDEX idx_ai_analysis_created_at ON ai_analysis(created_at DESC);
CREATE INDEX idx_ai_analysis_severity ON ai_analysis(severity);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Create trigger function for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patch_levels_updated_at BEFORE UPDATE ON patch_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_weight_configs_updated_at BEFORE UPDATE ON ai_weight_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
