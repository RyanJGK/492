/**
 * API service for backend communication
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const authAPI = {
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  register: (userData) => api.post('/api/v1/auth/register', userData),
  getCurrentUser: () => api.get('/api/v1/auth/me'),
};

// Dashboard
export const dashboardAPI = {
  getSummary: () => api.get('/api/v1/dashboard/summary'),
  getAuthEvents: (params) => api.get('/api/v1/dashboard/auth-events', { params }),
  getPatchLevels: (params) => api.get('/api/v1/dashboard/patch-levels', { params }),
  getVulnerabilities: (params) => api.get('/api/v1/dashboard/vulnerabilities', { params }),
  getFirewallLogs: (params) => api.get('/api/v1/dashboard/firewall-logs', { params }),
  getAIAnalyses: (params) => api.get('/api/v1/dashboard/ai-analyses', { params }),
};

// AI Agent
export const aiAPI = {
  requestAnalysis: (analysisRequest) => api.post('/api/v1/ai/analyze', analysisRequest),
  submitFeedback: (analysisId, feedback) => api.post(`/api/v1/ai/analyze/feedback/${analysisId}`, feedback),
  getWeightConfigs: () => api.get('/api/v1/ai/weights'),
  getActiveWeightConfig: () => api.get('/api/v1/ai/weights/active'),
  createWeightConfig: (config) => api.post('/api/v1/ai/weights', config),
  activateWeightConfig: (configId) => api.put(`/api/v1/ai/weights/${configId}/activate`),
};

export default api;
