/**
 * Vulnerabilities Page
 * Lists and manages vulnerability scans
 */
import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import { AlertTriangle, Search, Filter } from 'lucide-react';
import clsx from 'clsx';
import type { VulnerabilityScan, SeverityLevel } from '@/types';

export function VulnerabilitiesPage() {
  const [vulnerabilities, setVulnerabilities] = useState<VulnerabilityScan[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadVulnerabilities();
  }, [severityFilter]);

  const loadVulnerabilities = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getVulnerabilities({
        severity: severityFilter || undefined,
        limit: 100,
      });
      setVulnerabilities(data);
    } catch (error) {
      console.error('Failed to load vulnerabilities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: SeverityLevel) => {
    switch (severity) {
      case 'critical':
        return 'bg-danger-100 text-danger-700 border-danger-200';
      case 'high':
        return 'bg-warning-100 text-warning-700 border-warning-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const filteredVulnerabilities = vulnerabilities.filter((vuln) =>
    vuln.vulnerability_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vuln.cve_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vuln.target_system.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Vulnerability Scans
        </h1>
        <p className="text-gray-600 mt-2">
          Monitor and manage security vulnerabilities across systems
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search vulnerabilities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Severity Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Vulnerabilities List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredVulnerabilities.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">
            No vulnerabilities found
          </h3>
          <p className="text-gray-600 mt-2">
            No vulnerabilities match your current filters.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredVulnerabilities.map((vuln) => (
            <div
              key={vuln.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {vuln.vulnerability_name}
                    </h3>
                    <span
                      className={clsx(
                        'px-3 py-1 rounded-full text-xs font-semibold border',
                        getSeverityColor(vuln.severity)
                      )}
                    >
                      {vuln.severity.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
                    <div>
                      <span className="text-gray-600">Target:</span>
                      <div className="font-medium text-gray-900">
                        {vuln.target_system}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">CVE ID:</span>
                      <div className="font-medium text-gray-900">
                        {vuln.cve_id || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">CVSS Score:</span>
                      <div className="font-medium text-gray-900">
                        {vuln.cvss_score || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <div className="font-medium text-gray-900 capitalize">
                        {vuln.status.replace('_', ' ')}
                      </div>
                    </div>
                  </div>

                  {vuln.vulnerability_description && (
                    <p className="text-gray-700 mt-4 text-sm">
                      {vuln.vulnerability_description}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
