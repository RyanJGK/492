/**
 * API Client Service
 * Centralized HTTP client with authentication and error handling
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  User,
  AuthResponse,
  LoginCredentials,
  DashboardStats,
  ThreatTrend,
  VulnerabilityScan,
  AIWeightConfig,
  AIFeedback,
} from '@/types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for adding auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for handling errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== Authentication ==========

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const { data } = await this.client.post<AuthResponse>(
      '/api/v1/auth/login',
      credentials
    );
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/v1/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  async getCurrentUser(): Promise<User> {
    const { data } = await this.client.get<User>('/api/v1/auth/me');
    return data;
  }

  // ========== Dashboard ==========

  async getDashboardStats(): Promise<DashboardStats> {
    const { data } = await this.client.get<DashboardStats>(
      '/api/v1/dashboard/stats'
    );
    return data;
  }

  async getThreatTrends(days: number = 7): Promise<ThreatTrend[]> {
    const { data } = await this.client.get<ThreatTrend[]>(
      `/api/v1/dashboard/trends/threats?days=${days}`
    );
    return data;
  }

  // ========== Vulnerabilities ==========

  async getVulnerabilities(params?: {
    skip?: number;
    limit?: number;
    severity?: string;
    status?: string;
  }): Promise<VulnerabilityScan[]> {
    const { data } = await this.client.get<VulnerabilityScan[]>(
      '/api/v1/vulnerabilities/',
      { params }
    );
    return data;
  }

  async getVulnerability(scanId: string): Promise<VulnerabilityScan> {
    const { data } = await this.client.get<VulnerabilityScan>(
      `/api/v1/vulnerabilities/${scanId}`
    );
    return data;
  }

  async getVulnerabilityStats(): Promise<any> {
    const { data } = await this.client.get(
      '/api/v1/vulnerabilities/stats/summary'
    );
    return data;
  }

  // ========== AI Configuration (Admin Only) ==========

  async getAIConfigs(): Promise<AIWeightConfig[]> {
    const { data } = await this.client.get<AIWeightConfig[]>(
      '/api/v1/ai-config/'
    );
    return data;
  }

  async getActiveAIConfig(): Promise<AIWeightConfig> {
    const { data } = await this.client.get<AIWeightConfig>(
      '/api/v1/ai-config/active'
    );
    return data;
  }

  async createAIConfig(
    config: Partial<AIWeightConfig>
  ): Promise<AIWeightConfig> {
    const { data } = await this.client.post<AIWeightConfig>(
      '/api/v1/ai-config/',
      config
    );
    return data;
  }

  async updateAIConfig(
    configId: number,
    updates: Partial<AIWeightConfig>
  ): Promise<AIWeightConfig> {
    const { data } = await this.client.patch<AIWeightConfig>(
      `/api/v1/ai-config/${configId}`,
      updates
    );
    return data;
  }

  async deleteAIConfig(configId: number): Promise<void> {
    await this.client.delete(`/api/v1/ai-config/${configId}`);
  }

  // ========== AI Feedback (Analyst) ==========

  async submitAIFeedback(feedback: AIFeedback): Promise<any> {
    const { data } = await this.client.post(
      '/api/v1/ai-feedback/',
      feedback
    );
    return data;
  }

  async getAnalysisFeedback(analysisId: string): Promise<any[]> {
    const { data } = await this.client.get(
      `/api/v1/ai-feedback/analysis/${analysisId}`
    );
    return data;
  }
}

export const apiClient = new ApiClient();
