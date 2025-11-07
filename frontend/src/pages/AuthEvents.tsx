// Authentication events page
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { EventTable } from '../components/tables/EventTable';
import type { AuthenticationEvent } from '../types';

export function AuthEvents() {
  const [filters, setFilters] = useState({
    is_suspicious: undefined as boolean | undefined,
    limit: 100,
  });

  const { data: events, isLoading } = useQuery({
    queryKey: ['auth-events', filters],
    queryFn: () => apiClient.getAuthenticationEvents(filters),
    refetchInterval: 10000,
  });

  const columns = [
    {
      key: 'timestamp',
      label: 'Timestamp',
      render: (value: string) => new Date(value).toLocaleString(),
    },
    { key: 'source_ip', label: 'Source IP' },
    { key: 'username', label: 'Username' },
    { key: 'event_type', label: 'Event Type' },
    { key: 'geolocation', label: 'Location' },
    {
      key: 'is_suspicious',
      label: 'Status',
      render: (value: boolean) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            value
              ? 'bg-danger-900/30 text-danger-400'
              : 'bg-success-900/30 text-success-400'
          }`}
        >
          {value ? 'Suspicious' : 'Normal'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Authentication Events</h1>
      </div>

      {/* Filters */}
      <div className="bg-dark-800 rounded-lg p-4 border border-dark-700">
        <div className="flex gap-4">
          <button
            onClick={() => setFilters({ ...filters, is_suspicious: undefined })}
            className={`px-4 py-2 rounded-lg transition ${
              filters.is_suspicious === undefined
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
            }`}
          >
            All Events
          </button>
          <button
            onClick={() => setFilters({ ...filters, is_suspicious: true })}
            className={`px-4 py-2 rounded-lg transition ${
              filters.is_suspicious === true
                ? 'bg-danger-600 text-white'
                : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
            }`}
          >
            Suspicious Only
          </button>
          <button
            onClick={() => setFilters({ ...filters, is_suspicious: false })}
            className={`px-4 py-2 rounded-lg transition ${
              filters.is_suspicious === false
                ? 'bg-success-600 text-white'
                : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
            }`}
          >
            Normal Only
          </button>
        </div>
      </div>

      {/* Events Table */}
      <EventTable data={events || []} columns={columns} loading={isLoading} />
    </div>
  );
}
