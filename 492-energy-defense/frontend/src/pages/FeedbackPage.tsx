/**
 * Feedback Page (Analyst)
 * Submit feedback on AI analysis accuracy
 */
import React, { useState } from 'react';
import { apiClient } from '@/services/api';
import { RequireRole } from '@/context/AuthContext';
import { MessageSquare, Send } from 'lucide-react';

export function FeedbackPage() {
  const [analysisId, setAnalysisId] = useState('');
  const [rating, setRating] = useState(3);
  const [isAccurate, setIsAccurate] = useState(true);
  const [falsePositive, setFalsePositive] = useState(false);
  const [falseNegative, setFalseNegative] = useState(false);
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSuccess(false);

    try {
      await apiClient.submitAIFeedback({
        analysis_id: analysisId,
        accuracy_rating: rating,
        is_accurate: isAccurate,
        false_positive: falsePositive,
        false_negative: falseNegative,
        comments: comments,
      });

      setSuccess(true);
      // Reset form
      setAnalysisId('');
      setRating(3);
      setIsAccurate(true);
      setFalsePositive(false);
      setFalseNegative(false);
      setComments('');

      setTimeout(() => setSuccess(false), 5000);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <RequireRole roles={['admin', 'analyst']}>
      <div>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Analysis Feedback
          </h1>
          <p className="text-gray-600 mt-2">
            Help improve AI accuracy by providing feedback on analysis results
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-primary-900 mb-2">
            Why Feedback Matters
          </h3>
          <p className="text-sm text-primary-700">
            Your feedback helps refine the AI agent's threat detection
            capabilities. Accurate feedback improves the model's ability to
            identify real threats while reducing false positives.
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 bg-success-50 border border-success-200 rounded-lg p-4 flex items-center">
            <MessageSquare className="w-5 h-5 text-success-600 mr-3" />
            <div>
              <h3 className="font-semibold text-success-800">
                Feedback Submitted
              </h3>
              <p className="text-sm text-success-700 mt-1">
                Thank you for helping improve our AI analysis system.
              </p>
            </div>
          </div>
        )}

        {/* Feedback Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Analysis ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analysis ID
              </label>
              <input
                type="text"
                required
                value={analysisId}
                onChange={(e) => setAnalysisId(e.target.value)}
                placeholder="Enter the analysis UUID"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Find this in the AI analysis details
              </p>
            </div>

            {/* Accuracy Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Accuracy Rating (1-5)
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={rating}
                  onChange={(e) => setRating(parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-2xl font-bold text-primary-600 w-12 text-center">
                  {rating}
                </span>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Poor</span>
                <span>Excellent</span>
              </div>
            </div>

            {/* Checkboxes */}
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={isAccurate}
                  onChange={(e) => setIsAccurate(e.target.checked)}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="ml-3 text-sm text-gray-700">
                  Analysis was accurate
                </span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={falsePositive}
                  onChange={(e) => setFalsePositive(e.target.checked)}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="ml-3 text-sm text-gray-700">
                  False positive (identified threat that wasn't real)
                </span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={falseNegative}
                  onChange={(e) => setFalseNegative(e.target.checked)}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="ml-3 text-sm text-gray-700">
                  False negative (missed a real threat)
                </span>
              </label>
            </div>

            {/* Comments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Comments
              </label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={4}
                placeholder="Provide detailed feedback about the analysis..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center"
            >
              {submitting ? (
                'Submitting...'
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Submit Feedback
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </RequireRole>
  );
}
