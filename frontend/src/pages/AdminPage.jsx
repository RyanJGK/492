/**
 * Admin page for AI weight configuration (Admin only)
 */

import React, { useState, useEffect } from 'react';
import { aiAPI } from '../services/api';
import { CogIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export const AdminPage = () => {
  const [configs, setConfigs] = useState([]);
  const [activeConfig, setActiveConfig] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newConfig, setNewConfig] = useState({
    config_name: '',
    description: '',
    weights: {
      data_sources: {
        auth_events: 0.25,
        patch_levels: 0.20,
        vulnerability_scans: 0.35,
        firewall_logs: 0.20
      },
      threat_indicators: {
        critical_severity: 1.0,
        high_severity: 0.8,
        medium_severity: 0.5,
        low_severity: 0.3,
        exploit_available: 1.2,
        exploited_in_wild: 1.5
      },
      temporal_factors: {
        last_hour: 1.5,
        last_day: 1.2,
        last_week: 1.0,
        older: 0.7
      },
      asset_criticality: {
        critical: 1.5,
        high: 1.2,
        medium: 1.0,
        low: 0.8
      }
    },
    is_active: false
  });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const [configsRes, activeRes] = await Promise.all([
        aiAPI.getWeightConfigs(),
        aiAPI.getActiveWeightConfig().catch(() => null)
      ]);
      
      setConfigs(configsRes.data);
      if (activeRes) {
        setActiveConfig(activeRes.data);
      }
    } catch (error) {
      console.error('Failed to load configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConfig = async (e) => {
    e.preventDefault();
    try {
      await aiAPI.createWeightConfig(newConfig);
      setMessage({ type: 'success', text: 'Configuration created successfully' });
      setShowCreateForm(false);
      loadConfigs();
      
      // Reset form
      setNewConfig({
        ...newConfig,
        config_name: '',
        description: '',
        is_active: false
      });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to create configuration' });
    }
  };

  const handleActivateConfig = async (configId) => {
    try {
      await aiAPI.activateWeightConfig(configId);
      setMessage({ type: 'success', text: 'Configuration activated successfully' });
      loadConfigs();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to activate configuration' });
    }
  };

  const handleWeightChange = (category, key, value) => {
    setNewConfig({
      ...newConfig,
      weights: {
        ...newConfig.weights,
        [category]: {
          ...newConfig.weights[category],
          [key]: parseFloat(value)
        }
      }
    });
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Weight Configuration</h1>
          <p className="mt-1 text-sm text-gray-500">
            Configure AI agent analysis weighting parameters (Admin only)
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Create New Configuration'}
        </button>
      </div>

      {message && (
        <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-danger-50 text-danger-800'}`}>
          {message.text}
        </div>
      )}

      {/* Create Configuration Form */}
      {showCreateForm && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Create New Configuration
          </h2>
          <form onSubmit={handleCreateConfig} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Configuration Name
              </label>
              <input
                type="text"
                required
                className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                value={newConfig.config_name}
                onChange={(e) => setNewConfig({ ...newConfig, config_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                rows={3}
                className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                value={newConfig.description}
                onChange={(e) => setNewConfig({ ...newConfig, description: e.target.value })}
              />
            </div>

            {/* Weight Configuration Sections */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(newConfig.weights).map(([category, weights]) => (
                <div key={category} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3 capitalize">
                    {category.replace(/_/g, ' ')}
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(weights).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between">
                        <label className="text-xs text-gray-600 capitalize">
                          {key.replace(/_/g, ' ')}
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="2"
                          className="w-20 rounded border-gray-300 text-sm"
                          value={value}
                          onChange={(e) => handleWeightChange(category, key, e.target.value)}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                checked={newConfig.is_active}
                onChange={(e) => setNewConfig({ ...newConfig, is_active: e.target.checked })}
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                Set as active configuration
              </label>
            </div>

            <div className="flex justify-end">
              <button type="submit" className="btn-primary">
                Create Configuration
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Existing Configurations */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Existing Configurations
        </h2>
        <div className="space-y-4">
          {configs.map((config) => (
            <div
              key={config.id}
              className={`border rounded-lg p-4 ${config.is_active ? 'border-primary-500 bg-primary-50' : 'border-gray-200'}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  {config.is_active && (
                    <CheckCircleIcon className="h-5 w-5 text-primary-600 mr-2" />
                  )}
                  <h3 className="text-sm font-semibold text-gray-900">
                    {config.config_name}
                  </h3>
                </div>
                {!config.is_active && (
                  <button
                    onClick={() => handleActivateConfig(config.id)}
                    className="text-sm text-primary-600 hover:text-primary-800"
                  >
                    Activate
                  </button>
                )}
              </div>
              {config.description && (
                <p className="text-sm text-gray-600 mb-3">{config.description}</p>
              )}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                {Object.entries(config.weights).map(([category, weights]) => (
                  <div key={category}>
                    <p className="font-medium text-gray-700 capitalize mb-1">
                      {category.replace(/_/g, ' ')}
                    </p>
                    <ul className="space-y-1 text-gray-600">
                      {Object.entries(weights).slice(0, 3).map(([key, value]) => (
                        <li key={key}>
                          {key.replace(/_/g, ' ')}: {value}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
