-- Initialize database schema for Energy Defense system
-- This script runs automatically when the PostgreSQL container starts

CREATE TABLE IF NOT EXISTS authentication_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    source_ip VARCHAR(45),
    username VARCHAR(100),
    event_type VARCHAR(50),
    failure_reason VARCHAR(200),
    geolocation VARCHAR(100),
    is_suspicious BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_auth_events_timestamp ON authentication_events(timestamp);
CREATE INDEX idx_auth_events_source_ip ON authentication_events(source_ip);
CREATE INDEX idx_auth_events_username ON authentication_events(username);

CREATE TABLE IF NOT EXISTS patch_status (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    hostname VARCHAR(100),
    os_type VARCHAR(50),
    missing_patches TEXT[],
    severity VARCHAR(20),
    days_unpatched INTEGER,
    affected_service VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patch_status_timestamp ON patch_status(timestamp);
CREATE INDEX idx_patch_status_severity ON patch_status(severity);

CREATE TABLE IF NOT EXISTS network_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    port INTEGER,
    protocol VARCHAR(20),
    bytes_transferred BIGINT,
    packet_count INTEGER,
    is_encrypted BOOLEAN,
    threat_indicator VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_network_logs_timestamp ON network_logs(timestamp);
CREATE INDEX idx_network_logs_source_ip ON network_logs(source_ip);
CREATE INDEX idx_network_logs_threat_indicator ON network_logs(threat_indicator);

CREATE TABLE IF NOT EXISTS vulnerability_scans (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    asset_id VARCHAR(100),
    cve_id VARCHAR(50),
    cvss_score DECIMAL(3,1),
    exploit_available BOOLEAN,
    asset_criticality VARCHAR(20),
    remediation_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vulnerability_scans_timestamp ON vulnerability_scans(timestamp);
CREATE INDEX idx_vulnerability_scans_cve_id ON vulnerability_scans(cve_id);

CREATE TABLE IF NOT EXISTS ai_analysis (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    analysis_type VARCHAR(50),
    confidence_score DECIMAL(5,4),
    threat_level VARCHAR(20),
    affected_systems TEXT[],
    recommendation TEXT,
    false_positive_feedback BOOLEAN NULL,
    analyst_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_analysis_timestamp ON ai_analysis(timestamp);
CREATE INDEX idx_ai_analysis_threat_level ON ai_analysis(threat_level);

-- Configuration table for AI model weights
CREATE TABLE IF NOT EXISTS model_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Insert default users (passwords: admin123, analyst123, observer123)
-- Password hash generated using bcrypt
INSERT INTO users (username, email, hashed_password, role) VALUES
    ('admin', 'admin@energydefense.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5QI3l3pXhJ9FS', 'admin'),
    ('analyst', 'analyst@energydefense.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5QI3l3pXhJ9FS', 'analyst'),
    ('observer', 'observer@energydefense.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5QI3l3pXhJ9FS', 'observer')
ON CONFLICT (username) DO NOTHING;

-- Insert default model configuration
INSERT INTO model_config (config_key, config_value) VALUES
    ('authentication_weights', '{
        "failed_login_rate": 0.35,
        "geo_velocity": 0.25,
        "time_anomaly": 0.20,
        "enumeration_score": 0.20
    }'::jsonb),
    ('network_weights', '{
        "data_volume": 0.30,
        "connection_pattern": 0.25,
        "port_entropy": 0.25,
        "protocol_anomaly": 0.20
    }'::jsonb),
    ('vulnerability_weights', '{
        "cvss_score": 0.40,
        "days_unpatched": 0.30,
        "exploit_available": 0.20,
        "asset_criticality": 0.10
    }'::jsonb)
ON CONFLICT (config_key) DO NOTHING;
