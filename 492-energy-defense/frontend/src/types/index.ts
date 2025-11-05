/**
 * TypeScript type definitions for Energy Defense frontend
 */

export type UserRole = 'admin' | 'analyst' | 'observer';

export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type EventStatus = 'pending' | 'investigating' | 'resolved' | 'false_positive';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface VulnerabilityScan {
  id: number;
  scan_id: string;
  target_system: string;
  scan_type: string;
  severity: SeverityLevel;
  vulnerability_name: string;
  vulnerability_description: string;
  cve_id: string;
  cvss_score: number;
  affected_component: string;
  remediation_steps: string;
  scan_timestamp: string;
  status: EventStatus;
  assigned_to: number | null;
}

export interface PatchLevel {
  id: number;
  system_name: string;
  component_name: string;
  current_version: string;
  latest_version: string;
  patch_status: string;
  severity: SeverityLevel;
  cve_ids: string[];
  last_patched: string;
  next_scheduled_patch: string;
}

export interface FirewallLog {
  id: number;
  log_timestamp: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  action: string;
  rule_id: string;
  severity: SeverityLevel;
  threat_indicator: boolean;
  country_code: string;
}

export interface AIAnalysis {
  id: number;
  analysis_id: string;
  analysis_type: string;
  ai_response: string;
  confidence_score: number;
  threat_level: SeverityLevel;
  recommendations: string;
  data_sources: string[];
  weight_configuration: Record<string, any>;
  model_version: string;
  created_at: string;
  reviewed: boolean;
}

export interface AIWeightConfig {
  id: number;
  config_name: string;
  config_version: number;
  is_active: boolean;
  weights: Record<string, any>;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface AIFeedback {
  analysis_id: string;
  accuracy_rating: number;
  is_accurate: boolean;
  false_positive: boolean;
  false_negative: boolean;
  comments: string;
}

export interface DashboardStats {
  total_threats: number;
  critical_vulnerabilities: number;
  pending_patches: number;
  firewall_blocks_today: number;
  ai_analyses_count: number;
  average_confidence: number | null;
}

export interface ThreatTrend {
  date: string;
  count: number;
  severity: SeverityLevel;
}
