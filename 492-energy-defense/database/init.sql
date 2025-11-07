-- 492-Energy-Defense Database Schema
-- PostgreSQL 15+ compatible

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create audit log function for tracking changes
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- AUTHENTICATION AND USER MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'analyst', 'observer')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- AUTHENTICATION EVENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS auth_events (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'login_success', 'login_failure', 'logout', 'token_refresh',
        'password_change', 'permission_denied', 'session_timeout'
    )),
    username VARCHAR(100) NOT NULL,
    source_ip INET NOT NULL,
    user_agent TEXT,
    session_id UUID,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_auth_events_time ON auth_events(event_time DESC);
CREATE INDEX idx_auth_events_username ON auth_events(username);
CREATE INDEX idx_auth_events_type ON auth_events(event_type);
CREATE INDEX idx_auth_events_severity ON auth_events(severity);
CREATE INDEX idx_auth_events_source_ip ON auth_events(source_ip);
CREATE INDEX idx_auth_events_metadata ON auth_events USING gin(metadata);

-- ============================================================================
-- PATCH MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS patches (
    id BIGSERIAL PRIMARY KEY,
    patch_id VARCHAR(100) UNIQUE NOT NULL,
    system_name VARCHAR(200) NOT NULL,
    system_type VARCHAR(50) NOT NULL CHECK (system_type IN (
        'scada', 'hmi', 'plc', 'rtu', 'server', 'workstation', 'network_device'
    )),
    patch_name VARCHAR(255) NOT NULL,
    patch_version VARCHAR(50),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    status VARCHAR(30) NOT NULL CHECK (status IN (
        'pending', 'scheduled', 'in_progress', 'installed', 'failed', 'rolled_back'
    )),
    release_date DATE NOT NULL,
    scheduled_date TIMESTAMP WITH TIME ZONE,
    installed_date TIMESTAMP WITH TIME ZONE,
    description TEXT,
    cve_ids TEXT[],
    requires_downtime BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patches_system ON patches(system_name);
CREATE INDEX idx_patches_status ON patches(status);
CREATE INDEX idx_patches_severity ON patches(severity);
CREATE INDEX idx_patches_scheduled ON patches(scheduled_date);
CREATE INDEX idx_patches_cve ON patches USING gin(cve_ids);

CREATE TRIGGER patches_updated_at
    BEFORE UPDATE ON patches
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

-- ============================================================================
-- VULNERABILITY SCANNING
-- ============================================================================

CREATE TABLE IF NOT EXISTS vulnerability_scans (
    id BIGSERIAL PRIMARY KEY,
    scan_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    scan_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scanner_name VARCHAR(100) NOT NULL,
    target_system VARCHAR(200) NOT NULL,
    target_ip INET NOT NULL,
    scan_type VARCHAR(50) NOT NULL CHECK (scan_type IN (
        'network', 'application', 'configuration', 'compliance'
    )),
    status VARCHAR(30) NOT NULL CHECK (status IN (
        'running', 'completed', 'failed', 'cancelled'
    )),
    total_vulnerabilities INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    high_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    scan_duration_seconds INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id BIGSERIAL PRIMARY KEY,
    scan_id UUID NOT NULL REFERENCES vulnerability_scans(scan_id) ON DELETE CASCADE,
    vuln_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    cvss_score NUMERIC(3,1) CHECK (cvss_score >= 0 AND cvss_score <= 10),
    cve_id VARCHAR(50),
    affected_system VARCHAR(200) NOT NULL,
    affected_component VARCHAR(200),
    port INTEGER CHECK (port >= 0 AND port <= 65535),
    service VARCHAR(100),
    remediation TEXT,
    status VARCHAR(30) DEFAULT 'open' CHECK (status IN (
        'open', 'acknowledged', 'in_remediation', 'false_positive', 'resolved', 'risk_accepted'
    )),
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vuln_scans_time ON vulnerability_scans(scan_time DESC);
CREATE INDEX idx_vuln_scans_target ON vulnerability_scans(target_system);
CREATE INDEX idx_vuln_scans_status ON vulnerability_scans(status);
CREATE INDEX idx_vulns_scan_id ON vulnerabilities(scan_id);
CREATE INDEX idx_vulns_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulns_status ON vulnerabilities(status);
CREATE INDEX idx_vulns_cve ON vulnerabilities(cve_id) WHERE cve_id IS NOT NULL;

-- ============================================================================
-- FIREWALL AND NETWORK LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS firewall_logs (
    id BIGSERIAL PRIMARY KEY,
    log_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    firewall_name VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('allow', 'deny', 'drop', 'reject')),
    source_ip INET NOT NULL,
    source_port INTEGER CHECK (source_port >= 0 AND source_port <= 65535),
    dest_ip INET NOT NULL,
    dest_port INTEGER CHECK (dest_port >= 0 AND dest_port <= 65535),
    protocol VARCHAR(10) NOT NULL CHECK (protocol IN ('TCP', 'UDP', 'ICMP', 'GRE', 'ESP', 'AH', 'OTHER')),
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    rule_id VARCHAR(100),
    rule_name VARCHAR(200),
    threat_level VARCHAR(20) DEFAULT 'low' CHECK (threat_level IN ('critical', 'high', 'medium', 'low', 'info')),
    geo_location VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_firewall_time ON firewall_logs(log_time DESC);
CREATE INDEX idx_firewall_action ON firewall_logs(action);
CREATE INDEX idx_firewall_source_ip ON firewall_logs(source_ip);
CREATE INDEX idx_firewall_dest_ip ON firewall_logs(dest_ip);
CREATE INDEX idx_firewall_threat ON firewall_logs(threat_level);
CREATE INDEX idx_firewall_protocol ON firewall_logs(protocol);

-- ============================================================================
-- AI AGENT CONFIGURATION AND WEIGHTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_model_configs (
    id SERIAL PRIMARY KEY,
    config_name VARCHAR(100) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    model_type VARCHAR(50) NOT NULL,
    confidence_threshold NUMERIC(3,2) DEFAULT 0.75 CHECK (confidence_threshold >= 0 AND confidence_threshold <= 1),
    weights JSONB NOT NULL,
    feature_importance JSONB,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_ai_configs_active ON ai_model_configs(is_active);
CREATE INDEX idx_ai_configs_version ON ai_model_configs(version);

-- Default AI weights configuration
INSERT INTO ai_model_configs (config_name, version, is_active, model_type, weights, description)
VALUES (
    'default_v1',
    '1.0.0',
    TRUE,
    'threat_classifier',
    '{
        "auth_events": 0.30,
        "vulnerability_severity": 0.35,
        "firewall_anomalies": 0.25,
        "patch_criticality": 0.10
    }'::jsonb,
    'Initial production weights for threat classification'
);

-- ============================================================================
-- AI THREAT ANALYSIS AND SCORES
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_threat_analyses (
    id BIGSERIAL PRIMARY KEY,
    analysis_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    analysis_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_config_id INTEGER REFERENCES ai_model_configs(id),
    model_version VARCHAR(20) NOT NULL,
    threat_score NUMERIC(5,4) NOT NULL CHECK (threat_score >= 0 AND threat_score <= 1),
    confidence_score NUMERIC(5,4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    threat_category VARCHAR(50) NOT NULL CHECK (threat_category IN (
        'authentication_anomaly', 'vulnerability_exploitation', 'network_intrusion',
        'lateral_movement', 'data_exfiltration', 'dos_attack', 'misconfiguration', 'unknown'
    )),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    contributing_events JSONB NOT NULL,
    weight_application JSONB NOT NULL,
    explanation TEXT,
    recommended_actions TEXT[],
    false_positive BOOLEAN DEFAULT FALSE,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_analyses_time ON ai_threat_analyses(analysis_time DESC);
CREATE INDEX idx_ai_analyses_score ON ai_threat_analyses(threat_score DESC);
CREATE INDEX idx_ai_analyses_category ON ai_threat_analyses(threat_category);
CREATE INDEX idx_ai_analyses_severity ON ai_threat_analyses(severity);
CREATE INDEX idx_ai_analyses_false_positive ON ai_threat_analyses(false_positive);

-- ============================================================================
-- AI EVALUATION FEEDBACK
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_feedback (
    id BIGSERIAL PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES ai_threat_analyses(analysis_id) ON DELETE CASCADE,
    submitted_by UUID NOT NULL REFERENCES users(id),
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN (
        'true_positive', 'false_positive', 'true_negative', 'false_negative', 'accuracy_comment'
    )),
    accuracy_rating INTEGER CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),
    comments TEXT,
    suggested_severity VARCHAR(20) CHECK (suggested_severity IN ('critical', 'high', 'medium', 'low', 'info')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_feedback_analysis ON ai_feedback(analysis_id);
CREATE INDEX idx_ai_feedback_user ON ai_feedback(submitted_by);
CREATE INDEX idx_ai_feedback_type ON ai_feedback(feedback_type);

-- ============================================================================
-- AUDIT LOGS (Comprehensive System Traceability)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id),
    username VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- ============================================================================
-- SYSTEM METRICS AND HEALTH
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN (
        'cpu_usage', 'memory_usage', 'disk_usage', 'network_throughput',
        'db_connections', 'api_response_time', 'ai_inference_time'
    )),
    metric_value NUMERIC(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    source_service VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_metrics_time ON system_metrics(metric_time DESC);
CREATE INDEX idx_metrics_type ON system_metrics(metric_type);
CREATE INDEX idx_metrics_service ON system_metrics(source_service);

-- Partition system_metrics by month for performance
-- Note: This requires manual maintenance in production
-- CREATE TABLE system_metrics_y2024m11 PARTITION OF system_metrics
-- FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

-- ============================================================================
-- SEED DEFAULT USER ACCOUNTS (For Demo Purposes)
-- ============================================================================

INSERT INTO users (username, role, is_active) VALUES
    ('admin_user', 'admin', TRUE),
    ('analyst_user', 'analyst', TRUE),
    ('observer_user', 'observer', TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_summary AS
SELECT
    'auth_events' AS category,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE severity = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE severity = 'warning') AS warning_count,
    MAX(event_time) AS last_event_time
FROM auth_events
WHERE event_time > CURRENT_TIMESTAMP - INTERVAL '24 hours'
UNION ALL
SELECT
    'vulnerabilities' AS category,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE severity = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE severity = 'high') AS warning_count,
    MAX(detected_at) AS last_event_time
FROM vulnerabilities
WHERE status IN ('open', 'acknowledged', 'in_remediation')
UNION ALL
SELECT
    'firewall_logs' AS category,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE threat_level = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE threat_level = 'high') AS warning_count,
    MAX(log_time) AS last_event_time
FROM firewall_logs
WHERE log_time > CURRENT_TIMESTAMP - INTERVAL '24 hours'
UNION ALL
SELECT
    'ai_threats' AS category,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE severity = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE severity = 'high') AS warning_count,
    MAX(analysis_time) AS last_event_time
FROM ai_threat_analyses
WHERE analysis_time > CURRENT_TIMESTAMP - INTERVAL '24 hours';

CREATE UNIQUE INDEX idx_dashboard_summary_category ON dashboard_summary(category);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_dashboard_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_summary;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANT PERMISSIONS (For Application User)
-- ============================================================================

-- In production, create a separate application user with limited permissions
-- GRANT CONNECT ON DATABASE energy_defense TO app_user;
-- GRANT USAGE ON SCHEMA public TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
