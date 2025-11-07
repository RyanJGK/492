// Vulnerabilities management page
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { EventTable } from '../components/tables/EventTable';
import type { VulnerabilityScan } from '../types';

export function Vulnerabilities() {
  const { data: vulnerabilities, isLoading } = useQuery({
    queryKey: ['vulnerabilities'],
    queryFn: () => apiClient.getVulnerabilities({ limit: 100 }),
    refetchInterval: 10000,
  });

  const columns = [
    {
      key: 'asset_id',
      label: 'Asset',
    },
    {
      key: 'cve_id',
      label: 'CVE ID',
    },
    {
      key: 'cvss_score',
      label: 'CVSS Score',
      render: (value: number) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            value >= 9
              ? 'bg-danger-900/30 text-danger-400'
              : value >= 7
              ? 'bg-warning-900/30 text-warning-400'
              : 'bg-primary-900/30 text-primary-400'
          }`}
        >
          {value?.toFixed(1) || '-'}
        </span>
      ),
    },
    {
      key: 'exploit_available',
      label: 'Exploit',
      render: (value: boolean) =>
        value ? (
          <span className="px-2 py-1 bg-danger-900/30 text-danger-400 rounded text-xs">
            Available
          </span>
        ) : (
          <span className="text-gray-500">None</span>
        ),
    },
    {
      key: 'asset_criticality',
      label: 'Criticality',
      render: (value: string) => (
        <span className="capitalize">{value?.replace(/_/g, ' ') || '-'}</span>
      ),
    },
    {
      key: 'remediation_status',
      label: 'Status',
      render: (value: string) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            value === 'open'
              ? 'bg-danger-900/30 text-danger-400'
              : value === 'in_progress'
              ? 'bg-warning-900/30 text-warning-400'
              : 'bg-success-900/30 text-success-400'
          }`}
        >
          {value?.replace(/_/g, ' ').toUpperCase() || 'UNKNOWN'}
        </span>
      ),
    },
  ];

  const criticalVulns = vulnerabilities?.filter((v) => v.cvss_score && v.cvss_score >= 9.0) || [];
  const exploitableVulns = vulnerabilities?.filter((v) => v.exploit_available) || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Vulnerability Management</h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Total Vulnerabilities</div>
          <div className="text-3xl font-bold text-white">{vulnerabilities?.length || 0}</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Critical (CVSS ≥ 9)</div>
          <div className="text-3xl font-bold text-danger-500">{criticalVulns.length}</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Exploit Available</div>
          <div className="text-3xl font-bold text-warning-500">{exploitableVulns.length}</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">OT Systems Affected</div>
          <div className="text-3xl font-bold text-primary-500">
            {vulnerabilities?.filter((v) => v.asset_criticality === 'operational_technology')
              .length || 0}
          </div>
        </div>
      </div>

      {/* Vulnerabilities Table */}
      <EventTable data={vulnerabilities || []} columns={columns} loading={isLoading} />
    </div>
  );
}
