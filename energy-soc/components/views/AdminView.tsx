'use client'

import React, { useState, useEffect } from 'react'
import { AlertTriangle, Shield, Activity, TrendingUp, Settings, Zap } from 'lucide-react'
import StatsCard from '@/components/StatsCard'
import AlertCard from '@/components/AlertCard'
import { Alert, AIModelWeights } from '@/lib/types'
import { generateMockAlert } from '@/lib/mock-data'
import { getAIAgent } from '@/lib/ai-agent'

export default function AdminView() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [weights, setWeights] = useState<AIModelWeights>(() => getAIAgent().getWeights())
  const [isUpdating, setIsUpdating] = useState(false)

  useEffect(() => {
    // Initialize with mock data
    const initialAlerts = Array.from({ length: 20 }, () => generateMockAlert())
    setAlerts(initialAlerts)

    // Simulate new alerts arriving
    const interval = setInterval(() => {
      const newAlert = generateMockAlert()
      setAlerts(prev => [newAlert, ...prev].slice(0, 50))
    }, 15000) // New alert every 15 seconds

    return () => clearInterval(interval)
  }, [])

  const handleWeightChange = (category: keyof typeof weights.weights, value: number) => {
    setWeights(prev => ({
      ...prev,
      weights: {
        ...prev.weights,
        [category]: value
      },
      last_updated: new Date().toISOString()
    }))
  }

  const handleThresholdChange = (threshold: keyof typeof weights.threshold_settings, value: number) => {
    setWeights(prev => ({
      ...prev,
      threshold_settings: {
        ...prev.threshold_settings,
        [threshold]: value
      },
      last_updated: new Date().toISOString()
    }))
  }

  const handleUpdateWeights = async () => {
    setIsUpdating(true)
    try {
      const agent = getAIAgent()
      agent.updateWeights(weights)
      
      // Simulate API update delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      alert('AI model weights updated successfully!')
    } catch (error) {
      console.error('Error updating weights:', error)
      alert('Error updating weights')
    } finally {
      setIsUpdating(false)
    }
  }

  const criticalAlerts = alerts.filter(a => a.severity === 'critical').length
  const activeInvestigations = alerts.filter(a => a.status === 'investigating').length
  const avgAIScore = alerts.length > 0 
    ? (alerts.reduce((sum, a) => sum + (a.ai_score || 0), 0) / alerts.length * 100).toFixed(1)
    : '0'

  return (
    <div className="p-6 space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Alerts"
          value={alerts.length}
          icon={AlertTriangle}
          color="blue"
          subtitle="Last 24 hours"
        />
        <StatsCard
          title="Critical Alerts"
          value={criticalAlerts}
          icon={Shield}
          color="red"
          trend={{ value: 12, isPositive: false }}
        />
        <StatsCard
          title="Active Investigations"
          value={activeInvestigations}
          icon={Activity}
          color="yellow"
        />
        <StatsCard
          title="Avg AI Score"
          value={`${avgAIScore}%`}
          icon={TrendingUp}
          color="purple"
          trend={{ value: 5, isPositive: true }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AI Model Configuration */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Settings className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Model Configuration</h2>
              <p className="text-sm text-slate-400">Adjust threat analysis weights and thresholds</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Weight Configuration */}
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Feature Weights</h3>
              <div className="space-y-4">
                {Object.entries(weights.weights).map(([key, value]) => (
                  <div key={key} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <label className="text-sm text-slate-400 capitalize">
                        {key.replace(/_/g, ' ')}
                      </label>
                      <span className="text-sm font-mono text-blue-400">{value.toFixed(2)}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={value}
                      onChange={(e) => handleWeightChange(key as any, parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Threshold Configuration */}
            <div className="pt-4 border-t border-slate-800">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Threat Thresholds</h3>
              <div className="space-y-4">
                {Object.entries(weights.threshold_settings).map(([key, value]) => (
                  <div key={key} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <label className="text-sm text-slate-400 capitalize">
                        {key.replace(/_/g, ' ')}
                      </label>
                      <span className="text-sm font-mono text-orange-400">{value.toFixed(2)}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={value}
                      onChange={(e) => handleThresholdChange(key as any, parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-orange-500"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Update Button */}
            <button
              onClick={handleUpdateWeights}
              disabled={isUpdating}
              className="w-full mt-6 py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4" />
              {isUpdating ? 'Updating...' : 'Apply Configuration'}
            </button>

            <p className="text-xs text-slate-500 text-center">
              Last updated: {new Date(weights.last_updated).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-white mb-4">Recent Alerts</h2>
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {alerts.slice(0, 10).map((alert) => (
              <div key={alert.id} className="text-sm">
                <div className="flex items-start justify-between mb-1">
                  <span className="text-slate-300 font-medium">{alert.type}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    alert.severity === 'critical' ? 'bg-red-500/20 text-red-500' :
                    alert.severity === 'high' ? 'bg-orange-500/20 text-orange-500' :
                    alert.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                    'bg-blue-500/20 text-blue-500'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-500">{alert.source}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alert Feed */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
        <h2 className="text-lg font-bold text-white mb-4">Live Alert Feed</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {alerts.slice(0, 6).map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      </div>
    </div>
  )
}
