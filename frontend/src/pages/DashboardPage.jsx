/**
 * Main dashboard page with security metrics and data views
 */

import React, { useState, useEffect } from 'react';
import {
  ShieldExclamationIcon,
  ExclamationTriangleIcon,
  FireIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { dashboardAPI } from '../services/api';

const StatCard = ({ title, value, icon: Icon, trend, color }) => (
  <div className="card">
    <div className="flex items-center">
      <div className={`flex-shrink-0 p-3 rounded-lg ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div className="ml-5 w-0 flex-1">
        <dl>
          <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
          <dd className="flex items-baseline">
            <div className="text-2xl font-semibold text-gray-900">{value}</div>
            {trend && (
              <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                {trend}
              </div>
            )}
          </dd>
        </dl>
      </div>
    </div>
  </div>
);

export const DashboardPage = () => {
  const [summary, setSummary] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [firewallLogs, setFirewallLogs] = useState([]);
  const [patchLevels, setPatchLevels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [summaryRes, vulnRes, fwRes, patchRes] = await Promise.all([
        dashboardAPI.getSummary(),
        dashboardAPI.getVulnerabilities({ limit: 10, status: 'open' }),
        dashboardAPI.getFirewallLogs({ limit: 10, threat_detected: true }),
        dashboardAPI.getPatchLevels({ limit: 10, compliance_status: 'critical' }),
      ]);

      setSummary(summaryRes.data);
      setVulnerabilities(vulnRes.data);
      setFirewallLogs(fwRes.data);
      setPatchLevels(patchRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Security Overview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Real-time monitoring of energy sector cybersecurity defense
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Critical Vulnerabilities"
          value={summary?.vulnerabilities.critical_open || 0}
          icon={ShieldExclamationIcon}
          color="bg-danger-600"
        />
        <StatCard
          title="Failed Auth (24h)"
          value={summary?.auth_events.failed_24h || 0}
          icon={ExclamationTriangleIcon}
          color="bg-orange-600"
        />
        <StatCard
          title="Threats Detected (24h)"
          value={summary?.firewall.threats_24h || 0}
          icon={FireIcon}
          color="bg-danger-600"
        />
        <StatCard
          title="Critical Assets"
          value={summary?.patch_compliance.critical_assets || 0}
          icon={ChartBarIcon}
          color="bg-yellow-600"
        />
      </div>

      {/* Critical Vulnerabilities */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Critical Vulnerabilities (Open)
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Asset
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Vulnerability
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Severity
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  CVSS
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  CVE
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {vulnerabilities.map((vuln) => (
                <tr key={vuln.id}>
                  <td className="px-4 py-3 text-sm text-gray-900">{vuln.asset_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{vuln.title}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`badge badge-${vuln.severity}`}>
                      {vuln.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">{vuln.cvss_score}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{vuln.cve_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Threat Detection */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Threats Detected
          </h2>
          <div className="space-y-3">
            {firewallLogs.slice(0, 5).map((log) => (
              <div key={log.id} className="flex items-center justify-between p-3 bg-danger-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {log.threat_type?.replace('_', ' ').toUpperCase()}
                  </p>
                  <p className="text-xs text-gray-600">
                    From {log.source_ip} to {log.destination_ip}:{log.destination_port}
                  </p>
                </div>
                <span className={`badge badge-${log.threat_severity}`}>
                  {log.threat_severity}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Critical Patch Status
          </h2>
          <div className="space-y-3">
            {patchLevels.slice(0, 5).map((patch) => (
              <div key={patch.id} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">{patch.asset_name}</p>
                  <p className="text-xs text-gray-600">
                    {patch.missing_critical_patches} critical patches missing
                  </p>
                </div>
                <span className={`badge badge-${patch.compliance_status}`}>
                  {patch.compliance_status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
