import { useState } from 'react'
import { AlertCircle, CheckCircle, MessageSquare } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { useUser } from '../context/UserContext'
import FeedbackModal from './FeedbackModal'

export default function ThreatsList({ threats, onRefresh }) {
  const { user } = useUser()
  const [selectedThreat, setSelectedThreat] = useState(null)
  const [showFeedback, setShowFeedback] = useState(false)

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getCategoryIcon = (category) => {
    return <AlertCircle className="w-5 h-5" />
  }

  const handleFeedback = (threat) => {
    if (user && (user.role === 'admin' || user.role === 'analyst')) {
      setSelectedThreat(threat)
      setShowFeedback(true)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">
          Recent AI Threat Analyses
        </h2>
        <span className="text-sm text-gray-500">
          {threats.length} analyses
        </span>
      </div>

      <div className="space-y-3">
        {threats.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No threat analyses available</p>
          </div>
        ) : (
          threats.map((threat) => (
            <div
              key={threat.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="mt-1">
                    {getCategoryIcon(threat.threat_category)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 text-xs font-semibold rounded border ${getSeverityColor(threat.severity)}`}>
                        {threat.severity.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-600 capitalize">
                        {threat.threat_category.replace(/_/g, ' ')}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-2">
                      {threat.explanation || 'No explanation available'}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>
                        Threat Score: <span className="font-semibold">{(threat.threat_score * 100).toFixed(1)}%</span>
                      </span>
                      <span>
                        Confidence: <span className="font-semibold">{(threat.confidence_score * 100).toFixed(1)}%</span>
                      </span>
                      <span>
                        {formatDistanceToNow(new Date(threat.analysis_time), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {threat.acknowledged && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                  
                  {user && (user.role === 'admin' || user.role === 'analyst') && (
                    <button
                      onClick={() => handleFeedback(threat)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Submit Feedback"
                    >
                      <MessageSquare className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>

              {threat.recommended_actions && threat.recommended_actions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs font-semibold text-gray-600 mb-1">
                    Recommended Actions:
                  </p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {threat.recommended_actions.slice(0, 2).map((action, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {showFeedback && selectedThreat && (
        <FeedbackModal
          threat={selectedThreat}
          onClose={() => {
            setShowFeedback(false)
            setSelectedThreat(null)
            onRefresh()
          }}
        />
      )}
    </div>
  )
}
