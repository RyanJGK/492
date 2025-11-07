// Admin configuration page
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export function AdminConfig() {
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState('authentication_weights');

  const { data: weights } = useQuery({
    queryKey: ['model-weights'],
    queryFn: () => apiClient.getModelWeights(),
  });

  const { data: replayStatus } = useQuery({
    queryKey: ['replay-status'],
    queryFn: () => apiClient.getReplayStatus(),
    refetchInterval: 5000,
  });

  const { data: systemInfo } = useQuery({
    queryKey: ['system-info'],
    queryFn: () => apiClient.getSystemInfo(),
  });

  const updateWeightsMutation = useMutation({
    mutationFn: (data: { config_key: string; weights: any }) =>
      apiClient.updateModelWeights(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-weights'] });
    },
  });

  const controlReplayMutation = useMutation({
    mutationFn: (data: { action: 'start' | 'pause' | 'reset'; scenario?: string }) =>
      apiClient.controlReplay(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['replay-status'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const handleWeightChange = (feature: string, value: number) => {
    if (!weights || !weights[selectedCategory]) return;

    const updatedWeights = {
      ...weights[selectedCategory],
      [feature]: value,
    };

    updateWeightsMutation.mutate({
      config_key: selectedCategory,
      weights: updatedWeights,
    });
  };

  const scenarios = [
    { id: 'scada_brute_force', name: 'SCADA Brute Force Attack' },
    { id: 'eternalblue', name: 'EternalBlue Vulnerability' },
    { id: 'dns_tunneling', name: 'DNS Tunneling Exfiltration' },
    { id: 'port_scan', name: 'Port Scan Reconnaissance' },
    { id: 'phishing', name: 'Phishing Campaign' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Admin Configuration</h1>

      {/* Data Replay Control */}
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <h2 className="text-xl font-semibold text-white mb-4">Data Replay Control</h2>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-400">Status:</span>
              <span className="ml-2 text-white">
                {replayStatus?.is_running ? 'Running' : 'Stopped'}
              </span>
            </div>
            <div>
              <span className="text-sm text-gray-400">Speed:</span>
              <span className="ml-2 text-white">{replayStatus?.replay_speed}x</span>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => controlReplayMutation.mutate({ action: 'start' })}
              disabled={controlReplayMutation.isPending}
              className="px-4 py-2 bg-success-600 hover:bg-success-700 text-white rounded-lg transition disabled:opacity-50"
            >
              Load All Scenarios
            </button>
            <button
              onClick={() => controlReplayMutation.mutate({ action: 'reset' })}
              disabled={controlReplayMutation.isPending}
              className="px-4 py-2 bg-danger-600 hover:bg-danger-700 text-white rounded-lg transition disabled:opacity-50"
            >
              Reset Data
            </button>
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-2">Load Individual Scenario:</p>
            <div className="grid grid-cols-2 gap-2">
              {scenarios.map((scenario) => (
                <button
                  key={scenario.id}
                  onClick={() =>
                    controlReplayMutation.mutate({
                      action: 'start',
                      scenario: scenario.id,
                    })
                  }
                  disabled={controlReplayMutation.isPending}
                  className="px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm transition disabled:opacity-50"
                >
                  {scenario.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Model Weights Configuration */}
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <h2 className="text-xl font-semibold text-white mb-4">Model Feature Weights</h2>

        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">Select Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="authentication_weights">Authentication</option>
            <option value="network_weights">Network Traffic</option>
            <option value="vulnerability_weights">Vulnerabilities</option>
          </select>
        </div>

        {weights && weights[selectedCategory] && (
          <div className="space-y-4">
            {Object.entries(weights[selectedCategory]).map(([feature, value]) => (
              <div key={feature}>
                <div className="flex justify-between mb-2">
                  <label className="text-sm text-gray-300 capitalize">
                    {feature.replace(/_/g, ' ')}
                  </label>
                  <span className="text-sm text-gray-400">{Number(value).toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={Number(value)}
                  onChange={(e) => handleWeightChange(feature, parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* System Information */}
      {systemInfo && (
        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <h2 className="text-xl font-semibold text-white mb-4">System Information</h2>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-2">Database Statistics</h3>
              <dl className="space-y-1 text-sm">
                {Object.entries(systemInfo.database || {}).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <dt className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</dt>
                    <dd className="text-white">{String(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-2">Configuration</h3>
              <dl className="space-y-1 text-sm">
                {Object.entries(systemInfo.configuration || {}).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <dt className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</dt>
                    <dd className="text-white">{String(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
