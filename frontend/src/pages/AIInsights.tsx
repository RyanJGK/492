// AI insights and analysis page
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import type { AIAnalysis } from '../types';

export function AIInsights() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedAnalysis, setSelectedAnalysis] = useState<AIAnalysis | null>(null);
  const [feedbackNotes, setFeedbackNotes] = useState('');

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['ai-analyses'],
    queryFn: () => apiClient.getThreats({ hours: 24, limit: 50 }),
    refetchInterval: 10000,
  });

  const runAnalysisMutation = useMutation({
    mutationFn: () => apiClient.runAllAnalysis(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-analyses'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const submitFeedbackMutation = useMutation({
    mutationFn: (data: { analysis_id: number; is_false_positive: boolean; notes?: string }) =>
      apiClient.submitFeedback(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-analyses'] });
      setSelectedAnalysis(null);
      setFeedbackNotes('');
    },
  });

  const canSubmitFeedback = user && ['admin', 'analyst'].includes(user.role);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">AI Insights</h1>
        {canSubmitFeedback && (
          <button
            onClick={() => runAnalysisMutation.mutate()}
            disabled={runAnalysisMutation.isPending}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition disabled:opacity-50"
          >
            {runAnalysisMutation.isPending ? 'Running...' : 'Run Analysis'}
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : !analyses || analyses.length === 0 ? (
        <div className="bg-dark-800 rounded-lg p-12 border border-dark-700 text-center">
          <p className="text-gray-400 mb-4">No AI analysis results available</p>
          {canSubmitFeedback && (
            <button
              onClick={() => runAnalysisMutation.mutate()}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
            >
              Run Analysis Now
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {analyses.map((analysis) => (
            <div
              key={analysis.id}
              className="bg-dark-800 rounded-lg p-6 border border-dark-700"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      analysis.threat_level === 'critical'
                        ? 'bg-danger-900/30 text-danger-400'
                        : analysis.threat_level === 'high'
                        ? 'bg-warning-900/30 text-warning-400'
                        : analysis.threat_level === 'medium'
                        ? 'bg-warning-900/20 text-warning-300'
                        : 'bg-primary-900/30 text-primary-400'
                    }`}
                  >
                    {analysis.threat_level?.toUpperCase()}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {new Date(analysis.timestamp).toLocaleString()}
                  </span>
                  <span className="text-gray-400 text-sm">
                    Confidence: {((analysis.confidence_score || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                {canSubmitFeedback && (
                  <button
                    onClick={() => setSelectedAnalysis(analysis)}
                    className="px-3 py-1 bg-dark-700 hover:bg-dark-600 text-gray-300 rounded-lg text-sm transition"
                  >
                    Submit Feedback
                  </button>
                )}
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-semibold text-white mb-2 capitalize">
                  {analysis.analysis_type?.replace(/_/g, ' ')}
                </h3>
                <p className="text-gray-400">{analysis.recommendation}</p>
              </div>

              {analysis.affected_systems && analysis.affected_systems.length > 0 && (
                <div>
                  <p className="text-sm text-gray-400 mb-2">Affected Systems:</p>
                  <div className="flex flex-wrap gap-2">
                    {analysis.affected_systems.map((system, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-dark-700 border border-dark-600 text-gray-300 rounded text-xs"
                      >
                        {system}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysis.false_positive_feedback !== null && (
                <div className="mt-4 pt-4 border-t border-dark-700">
                  <p className="text-sm text-gray-400">
                    Analyst Feedback:{' '}
                    <span
                      className={
                        analysis.false_positive_feedback ? 'text-warning-400' : 'text-success-400'
                      }
                    >
                      {analysis.false_positive_feedback ? 'False Positive' : 'Confirmed'}
                    </span>
                  </p>
                  {analysis.analyst_notes && (
                    <p className="text-sm text-gray-400 mt-1">{analysis.analyst_notes}</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Feedback Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-dark-800 rounded-lg p-6 max-w-md w-full border border-dark-700">
            <h3 className="text-lg font-semibold text-white mb-4">Submit Feedback</h3>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Is this a false positive?
                </label>
                <div className="flex gap-4">
                  <button
                    onClick={() =>
                      submitFeedbackMutation.mutate({
                        analysis_id: selectedAnalysis.id,
                        is_false_positive: true,
                        notes: feedbackNotes,
                      })
                    }
                    className="flex-1 px-4 py-2 bg-warning-600 hover:bg-warning-700 text-white rounded-lg transition"
                  >
                    Yes, False Positive
                  </button>
                  <button
                    onClick={() =>
                      submitFeedbackMutation.mutate({
                        analysis_id: selectedAnalysis.id,
                        is_false_positive: false,
                        notes: feedbackNotes,
                      })
                    }
                    className="flex-1 px-4 py-2 bg-success-600 hover:bg-success-700 text-white rounded-lg transition"
                  >
                    No, Confirmed
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Notes (optional)</label>
                <textarea
                  value={feedbackNotes}
                  onChange={(e) => setFeedbackNotes(e.target.value)}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  rows={3}
                  placeholder="Add any additional notes..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setSelectedAnalysis(null);
                  setFeedbackNotes('');
                }}
                className="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-gray-300 rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
