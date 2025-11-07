// TypeScript type definitions

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'analyst' | 'observer';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthenticationEvent {
  id: number;
  timestamp: string;
  source_ip?: string;
  username?: string;
  event_type?: string;
  failure_reason?: string;
  geolocation?: string;
  is_suspicious: boolean;
}

export interface NetworkLog {
  id: number;
  timestamp: string;
  source_ip?: string;
  destination_ip?: string;
  port?: number;
  protocol?: string;
  bytes_transferred?: number;
  packet_count?: number;
  is_encrypted?: boolean;
  threat_indicator?: string;
}

export interface PatchStatus {
  id: number;
  timestamp: string;
  hostname?: string;
  os_type?: string;
  missing_patches: string[];
  severity?: string;
  days_unpatched?: number;
  affected_service?: string;
}

export interface VulnerabilityScan {
  id: number;
  timestamp: string;
  asset_id?: string;
  cve_id?: string;
  cvss_score?: number;
  exploit_available?: boolean;
  asset_criticality?: string;
  remediation_status?: string;
}

export interface AIAnalysis {
  id: number;
  timestamp: string;
  analysis_type?: string;
  confidence_score?: number;
  threat_level?: string;
  affected_systems: string[];
  recommendation?: string;
  false_positive_feedback?: boolean;
  analyst_notes?: string;
}

export interface DashboardData {
  threat_level: string;
  confidence_score: number;
  active_threats: number;
  affected_systems: string[];
  threat_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  recent_alerts: Array<{
    id: number;
    timestamp: string;
    threat_level: string;
    analysis_type: string;
    confidence: number;
    recommendation: string;
  }>;
}

export interface EventStats {
  total_auth_events: number;
  suspicious_auth_events: number;
  total_network_logs: number;
  network_threats: number;
  total_patch_records: number;
  critical_patches: number;
  total_vulnerabilities: number;
  critical_vulnerabilities: number;
  exploitable_vulnerabilities: number;
}

export interface ModelWeights {
  [key: string]: {
    [feature: string]: number;
  };
}

export type ThreatLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';
