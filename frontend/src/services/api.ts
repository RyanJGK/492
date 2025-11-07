// API client service
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  AuthToken,
  User,
  AuthenticationEvent,
  NetworkLog,
  PatchStatus,
  VulnerabilityScan,
  AIAnalysis,
  DashboardData,
  EventStats,
  ModelWeights,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear auth and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(username: string, password: string): Promise<AuthToken> {
    const response = await this.client.post<AuthToken>('/api/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<AuthToken> {
    const response = await this.client.post<AuthToken>('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  // Events
  async getAuthenticationEvents(params?: {
    start_date?: string;
    end_date?: string;
    source_ip?: string;
    username?: string;
    is_suspicious?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<AuthenticationEvent[]> {
    const response = await this.client.get<AuthenticationEvent[]>(
      '/api/events/auth',
      { params }
    );
    return response.data;
  }

  async getNetworkLogs(params?: {
    start_date?: string;
    end_date?: string;
    source_ip?: string;
    destination_ip?: string;
    threat_indicator?: string;
    limit?: number;
    offset?: number;
  }): Promise<NetworkLog[]> {
    const response = await this.client.get<NetworkLog[]>(
      '/api/events/network',
      { params }
    );
    return response.data;
  }

  async getPatchStatus(params?: {
    start_date?: string;
    end_date?: string;
    hostname?: string;
    severity?: string;
    affected_service?: string;
    limit?: number;
    offset?: number;
  }): Promise<PatchStatus[]> {
    const response = await this.client.get<PatchStatus[]>(
      '/api/events/patches',
      { params }
    );
    return response.data;
  }

  async getVulnerabilities(params?: {
    start_date?: string;
    end_date?: string;
    asset_id?: string;
    cve_id?: string;
    min_cvss?: number;
    exploit_available?: boolean;
    asset_criticality?: string;
    limit?: number;
    offset?: number;
  }): Promise<VulnerabilityScan[]> {
    const response = await this.client.get<VulnerabilityScan[]>(
      '/api/events/vulnerabilities',
      { params }
    );
    return response.data;
  }

  async getEventStats(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<EventStats> {
    const response = await this.client.get<EventStats>('/api/events/stats', {
      params,
    });
    return response.data;
  }

  // Analysis
  async detectAnomalies(data: {
    start_date: string;
    end_date: string;
    event_type: 'auth' | 'network' | 'vulnerability';
  }) {
    const response = await this.client.post('/api/analyze/anomaly', data);
    return response.data;
  }

  async getThreats(params?: {
    hours?: number;
    threat_level?: string;
    limit?: number;
  }): Promise<AIAnalysis[]> {
    const response = await this.client.get<AIAnalysis[]>(
      '/api/analyze/threats',
      { params }
    );
    return response.data;
  }

  async submitFeedback(data: {
    analysis_id: number;
    is_false_positive: boolean;
    notes?: string;
  }) {
    const response = await this.client.post('/api/analyze/feedback', data);
    return response.data;
  }

  async getDashboardData(): Promise<DashboardData> {
    const response = await this.client.get<DashboardData>(
      '/api/analyze/dashboard'
    );
    return response.data;
  }

  async runAllAnalysis() {
    const response = await this.client.post('/api/analyze/run-all-analysis');
    return response.data;
  }

  // Admin Configuration
  async getModelWeights(): Promise<ModelWeights> {
    const response = await this.client.get<ModelWeights>(
      '/api/config/model-weights'
    );
    return response.data;
  }

  async updateModelWeights(data: {
    config_key: string;
    weights: { [key: string]: number };
  }) {
    const response = await this.client.put('/api/config/model-weights', data);
    return response.data;
  }

  async getReplayStatus() {
    const response = await this.client.get('/api/config/replay-status');
    return response.data;
  }

  async controlReplay(data: {
    action: 'start' | 'pause' | 'reset';
    scenario?: string;
  }) {
    const response = await this.client.post('/api/config/replay-control', data);
    return response.data;
  }

  async getAuditLog(params?: { limit?: number }) {
    const response = await this.client.get('/api/config/audit-log', { params });
    return response.data;
  }

  async getSystemInfo() {
    const response = await this.client.get('/api/config/system-info');
    return response.data;
  }
}

export const apiClient = new APIClient();
