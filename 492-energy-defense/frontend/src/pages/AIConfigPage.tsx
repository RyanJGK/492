/**
 * AI Configuration Page (Admin Only)
 * Manage AI weight configurations
 */
import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import { RequireRole } from '@/context/AuthContext';
import { Settings, Plus, Edit, Trash2, Check } from 'lucide-react';
import clsx from 'clsx';
import type { AIWeightConfig } from '@/types';

export function AIConfigPage() {
  const [configs, setConfigs] = useState<AIWeightConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingConfig, setEditingConfig] = useState<AIWeightConfig | null>(
    null
  );

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getAIConfigs();
      setConfigs(data);
    } catch (error) {
      console.error('Failed to load configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivateConfig = async (configId: number) => {
    try {
      await apiClient.updateAIConfig(configId, { is_active: true });
      await loadConfigs();
    } catch (error) {
      console.error('Failed to activate config:', error);
    }
  };

  const handleDeleteConfig = async (configId: number) => {
    if (!confirm('Are you sure you want to delete this configuration?')) {
      return;
    }

    try {
      await apiClient.deleteAIConfig(configId);
      await loadConfigs();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete configuration');
    }
  };

  return (
    <RequireRole roles={['admin']}>
      <div>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Agent Configuration
          </h1>
          <p className="text-gray-600 mt-2">
            Manage AI weighting parameters for threat analysis (Admin Only)
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-primary-900 mb-2">
            About AI Weighting
          </h3>
          <p className="text-sm text-primary-700">
            Weight configurations control how the AI agent prioritizes different
            data sources when analyzing threats. Higher weights indicate greater
            influence on the final risk assessment. All changes are version-
            controlled and logged for audit purposes.
          </p>
        </div>

        {/* Configurations List */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {configs.map((config) => (
              <div
                key={config.id}
                className={clsx(
                  'bg-white rounded-lg shadow-sm border p-6',
                  config.is_active
                    ? 'border-success-300 ring-2 ring-success-200'
                    : 'border-gray-200'
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {config.config_name}
                      </h3>
                      <span className="text-sm text-gray-500">
                        v{config.config_version}
                      </span>
                      {config.is_active && (
                        <span className="px-3 py-1 bg-success-100 text-success-700 rounded-full text-xs font-semibold flex items-center">
                          <Check className="w-3 h-3 mr-1" />
                          ACTIVE
                        </span>
                      )}
                    </div>

                    {config.description && (
                      <p className="text-gray-600 text-sm mb-4">
                        {config.description}
                      </p>
                    )}

                    {/* Weight Parameters */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-3">
                        Weight Parameters
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {Object.entries(config.weights).map(([key, value]) => (
                          <div key={key}>
                            <div className="text-xs text-gray-600 mb-1">
                              {key.replace(/_/g, ' ').toUpperCase()}
                            </div>
                            <div className="font-mono text-sm font-semibold text-gray-900">
                              {typeof value === 'object'
                                ? JSON.stringify(value)
                                : value}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="mt-4 text-sm text-gray-500">
                      Created: {new Date(config.created_at).toLocaleString()}
                      {' | '}
                      Updated: {new Date(config.updated_at).toLocaleString()}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col space-y-2 ml-4">
                    {!config.is_active && (
                      <button
                        onClick={() => handleActivateConfig(config.id)}
                        className="px-4 py-2 bg-success-600 text-white rounded-lg hover:bg-success-700 text-sm font-medium transition"
                      >
                        Activate
                      </button>
                    )}
                    {!config.is_active && (
                      <button
                        onClick={() => handleDeleteConfig(config.id)}
                        className="px-4 py-2 bg-danger-600 text-white rounded-lg hover:bg-danger-700 text-sm font-medium transition flex items-center"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Warning */}
        <div className="mt-8 bg-warning-50 border border-warning-200 rounded-lg p-6">
          <h3 className="font-semibold text-warning-900 mb-2">
            ⚠️ Configuration Changes
          </h3>
          <p className="text-sm text-warning-700">
            Modifying AI weight configurations will affect how threats are
            analyzed and prioritized. All changes are audited and can impact the
            AI agent's recommendations. Test new configurations thoroughly before
            activating in production environments.
          </p>
        </div>
      </div>
    </RequireRole>
  );
}
