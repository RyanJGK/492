// Network traffic analysis page
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { EventTable } from '../components/tables/EventTable';
import type { NetworkLog } from '../types';

export function NetworkAnalysis() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['network-logs'],
    queryFn: () => apiClient.getNetworkLogs({ limit: 100 }),
    refetchInterval: 10000,
  });

  const columns = [
    {
      key: 'timestamp',
      label: 'Timestamp',
      render: (value: string) => new Date(value).toLocaleString(),
    },
    { key: 'source_ip', label: 'Source IP' },
    { key: 'destination_ip', label: 'Destination IP' },
    { key: 'port', label: 'Port' },
    { key: 'protocol', label: 'Protocol' },
    {
      key: 'bytes_transferred',
      label: 'Data (MB)',
      render: (value: number) => (value / (1024 * 1024)).toFixed(2),
    },
    {
      key: 'threat_indicator',
      label: 'Threat Indicator',
      render: (value: string) =>
        value ? (
          <span className="px-2 py-1 bg-danger-900/30 text-danger-400 rounded text-xs">
            {value.replace(/_/g, ' ').toUpperCase()}
          </span>
        ) : (
          <span className="text-gray-500">-</span>
        ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Network Traffic Analysis</h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Total Connections</div>
          <div className="text-3xl font-bold text-white">{logs?.length || 0}</div>
        </div>
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Threat Indicators</div>
          <div className="text-3xl font-bold text-danger-500">
            {logs?.filter((l) => l.threat_indicator).length || 0}
          </div>
        </div>
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div className="text-gray-400 text-sm mb-2">Data Transferred</div>
          <div className="text-3xl font-bold text-primary-500">
            {(
              (logs?.reduce((sum, l) => sum + (l.bytes_transferred || 0), 0) || 0) /
              (1024 * 1024 * 1024)
            ).toFixed(2)}{' '}
            GB
          </div>
        </div>
      </div>

      {/* Network Logs Table */}
      <EventTable data={logs || []} columns={columns} loading={isLoading} />
    </div>
  );
}
