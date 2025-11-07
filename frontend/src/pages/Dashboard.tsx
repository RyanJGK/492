// Main dashboard page
import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { ThreatGauge } from '../components/charts/ThreatGauge';
import { ThreatTimeline } from '../components/charts/ThreatTimeline';
import { AttackHeatmap } from '../components/charts/AttackHeatmap';
import type { DashboardData, ThreatLevel } from '../types';

export function Dashboard() {
  const { data: dashboardData, isLoading, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboardData(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: threats } = useQuery({
    queryKey: ['threats'],
    queryFn: () => apiClient.getThreats({ hours: 24, limit: 50 }),
    refetchInterval: 30000,
  });

  if (isLoading || !dashboardData) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">
          Security Operations Dashboard
        </h1>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
        >
          Refresh
        </button>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Active Threats</div>
          <div className="text-3xl font-bold text-white">
            {dashboardData.active_threats}
          </div>
        </div>
        
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Affected Systems</div>
          <div className="text-3xl font-bold text-white">
            {dashboardData.affected_systems.length}
          </div>
        </div>
        
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Critical Alerts</div>
          <div className="text-3xl font-bold text-danger-500">
            {dashboardData.threat_counts.critical}
          </div>
        </div>
        
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">High Priority</div>
          <div className="text-3xl font-bold text-warning-500">
            {dashboardData.threat_counts.high}
          </div>
        </div>
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatGauge
          level={dashboardData.threat_level as ThreatLevel}
          confidence={dashboardData.confidence_score}
        />
        
        <AttackHeatmap threatCounts={dashboardData.threat_counts} />
      </div>

      {threats && threats.length > 0 && (
        <ThreatTimeline
          data={threats.map((t) => ({
            timestamp: t.timestamp,
            threat_level: t.threat_level || 'info',
            confidence: t.confidence_score || 0,
          }))}
        />
      )}

      {/* Recent Alerts */}
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Alerts</h3>
        
        {dashboardData.recent_alerts.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No recent alerts</p>
        ) : (
          <div className="space-y-3">
            {dashboardData.recent_alerts.map((alert) => (
              <div
                key={alert.id}
                className="bg-dark-700 rounded-lg p-4 border border-dark-600"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        alert.threat_level === 'critical'
                          ? 'bg-danger-900/30 text-danger-400'
                          : alert.threat_level === 'high'
                          ? 'bg-warning-900/30 text-warning-400'
                          : 'bg-primary-900/30 text-primary-400'
                      }`}
                    >
                      {alert.threat_level.toUpperCase()}
                    </span>
                    <span className="text-gray-400 text-sm">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <span className="text-gray-400 text-sm">
                    {(alert.confidence * 100).toFixed(1)}% confidence
                  </span>
                </div>
                <p className="text-white mb-2 capitalize">
                  {alert.analysis_type?.replace(/_/g, ' ')}
                </p>
                <p className="text-gray-400 text-sm">{alert.recommendation}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Affected Systems */}
      {dashboardData.affected_systems.length > 0 && (
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <h3 className="text-lg font-semibold text-white mb-4">
            Affected Systems
          </h3>
          <div className="flex flex-wrap gap-2">
            {dashboardData.affected_systems.slice(0, 10).map((system, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-danger-900/20 border border-danger-700 text-danger-400 rounded-lg text-sm"
              >
                {system}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
