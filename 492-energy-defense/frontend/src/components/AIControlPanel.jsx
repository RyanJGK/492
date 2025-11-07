import { useState, useEffect } from 'react'
import axios from 'axios'
import { Settings, Save, AlertCircle } from 'lucide-react'
import { useUser } from '../context/UserContext'

export default function AIControlPanel() {
  const { user } = useUser()
  const [weights, setWeights] = useState({
    auth_events: 0.30,
    vulnerability_severity: 0.35,
    firewall_anomalies: 0.25,
    patch_criticality: 0.10,
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    axios.get('/api/ai/config/active')
      .then(response => setWeights(response.data.weights))
      .catch(error => console.error('Failed to fetch config:', error))
  }, [])

  const handleWeightChange = (key, value) => {
    setWeights(prev => ({ ...prev, [key]: parseFloat(value) }))
  }

  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0)

  const handleSave = async () => {
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      setMessage({ type: 'error', text: 'Weights must sum to 1.0' })
      return
    }

    setSaving(true)
    setMessage(null)

    try {
      await axios.post(`/api/ai/config/weights?username=${user.username}`, weights)
      setMessage({ type: 'success', text: 'AI weights updated successfully' })
      setTimeout(() => setMessage(null), 3000)
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to update weights' 
      })
    } finally {
      setSaving(false)
    }
  }

  const weightLabels = {
    auth_events: 'Authentication Events',
    vulnerability_severity: 'Vulnerability Severity',
    firewall_anomalies: 'Firewall Anomalies',
    patch_criticality: 'Patch Criticality',
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Settings className="w-5 h-5 text-purple-600" />
        <h2 className="text-lg font-bold text-gray-900">
          AI Model Configuration
        </h2>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mb-4">
        <p className="text-xs text-purple-800">
          <strong>Admin Only:</strong> Adjust feature importance weights for AI threat scoring
        </p>
      </div>

      <div className="space-y-4 mb-4">
        {Object.entries(weights).map(([key, value]) => (
          <div key={key}>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-gray-700">
                {weightLabels[key]}
              </label>
              <span className="text-sm font-semibold text-blue-600">
                {(value * 100).toFixed(0)}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={value}
              onChange={(e) => handleWeightChange(key, e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        ))}
      </div>

      <div className="bg-gray-50 rounded p-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-gray-700">Total Weight:</span>
          <span className={`font-bold ${Math.abs(totalWeight - 1.0) < 0.01 ? 'text-green-600' : 'text-red-600'}`}>
            {totalWeight.toFixed(2)}
          </span>
        </div>
        {Math.abs(totalWeight - 1.0) >= 0.01 && (
          <div className="flex items-center space-x-1 mt-2 text-xs text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span>Must equal 1.00</span>
          </div>
        )}
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200'
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <button
        onClick={handleSave}
        disabled={saving || Math.abs(totalWeight - 1.0) >= 0.01}
        className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Save className="w-4 h-4" />
        <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
      </button>
    </div>
  )
}
