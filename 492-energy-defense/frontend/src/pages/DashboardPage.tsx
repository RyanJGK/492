/**
 * Dashboard Page
 * Main overview with statistics and threat trends
 */
import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/services/api';
import { StatCard } from '@/components/StatCard';
import {
  Shield,
  AlertTriangle,
  Package,
  Lock,
  Brain,
  TrendingUp,
} from 'lucide-react';
import type { DashboardStats, ThreatTrend } from '@/types';

export function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<ThreatTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, trendsData] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getThreatTrends(7),
      ]);
      setStats(statsData);
      setTrends(trendsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-danger-50 border border-danger-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-danger-800">Error</h3>
        <p className="text-danger-700 mt-2">{error}</p>
        <button
          onClick={loadDashboardData}
          className="mt-4 px-4 py-2 bg-danger-600 text-white rounded-lg hover:bg-danger-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Security Operations Center
        </h1>
        <p className="text-gray-600 mt-2">
          Welcome back, <span className="font-semibold">{user?.username}</span>
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Total Threats Detected"
          value={stats?.total_threats || 0}
          icon={Shield}
          color="danger"
        />
        <StatCard
          title="Critical Vulnerabilities"
          value={stats?.critical_vulnerabilities || 0}
          icon={AlertTriangle}
          color="danger"
        />
        <StatCard
          title="Pending Patches"
          value={stats?.pending_patches || 0}
          icon={Package}
          color="warning"
        />
        <StatCard
          title="Firewall Blocks Today"
          value={stats?.firewall_blocks_today || 0}
          icon={Lock}
          color="success"
        />
        <StatCard
          title="AI Analyses"
          value={stats?.ai_analyses_count || 0}
          icon={Brain}
          color="primary"
        />
        <StatCard
          title="AI Confidence"
          value={
            stats?.average_confidence
              ? `${(stats.average_confidence * 100).toFixed(1)}%`
              : 'N/A'
          }
          icon={TrendingUp}
          color="primary"
        />
      </div>

      {/* Threat Trends */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Threat Trends (Last 7 Days)
        </h2>

        {trends.length === 0 ? (
          <p className="text-gray-600 text-center py-8">
            No threat data available for the selected period.
          </p>
        ) : (
          <div className="space-y-3">
            {trends.map((trend, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  <div className="text-sm font-medium text-gray-600">
                    {new Date(trend.date).toLocaleDateString()}
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      trend.severity === 'critical'
                        ? 'bg-danger-100 text-danger-700'
                        : trend.severity === 'high'
                        ? 'bg-warning-100 text-warning-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {trend.severity.toUpperCase()}
                  </span>
                </div>
                <div className="text-lg font-bold text-gray-900">
                  {trend.count} threats
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Role-Based Information */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        {user?.role === 'admin' && (
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
            <h3 className="font-semibold text-primary-900 mb-2">
              Admin Controls
            </h3>
            <p className="text-sm text-primary-700">
              You have full access to all system configurations including AI
              weighting parameters.
            </p>
          </div>
        )}

        {(user?.role === 'admin' || user?.role === 'analyst') && (
          <div className="bg-warning-50 border border-warning-200 rounded-lg p-6">
            <h3 className="font-semibold text-warning-900 mb-2">
              Analyst Tools
            </h3>
            <p className="text-sm text-warning-700">
              Submit feedback on AI analysis accuracy to improve threat
              detection.
            </p>
          </div>
        )}

        <div className="bg-success-50 border border-success-200 rounded-lg p-6">
          <h3 className="font-semibold text-success-900 mb-2">
            Live Monitoring
          </h3>
          <p className="text-sm text-success-700">
            Real-time data ingestion simulates an active SOC environment.
          </p>
        </div>
      </div>
    </div>
  );
}
