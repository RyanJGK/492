'use client'

import React, { useState, useEffect } from 'react'
import { AlertTriangle, Search, Filter, CheckCircle, XCircle, Clock, Brain } from 'lucide-react'
import AlertCard from '@/components/AlertCard'
import StatsCard from '@/components/StatsCard'
import { Alert, AIAnalysis } from '@/lib/types'
import { generateMockAlert } from '@/lib/mock-data'
import { getAIAgent } from '@/lib/ai-agent'
import { formatTimeAgo } from '@/lib/utils'

export default function AnalystView() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Initialize with mock data
    const initialAlerts = Array.from({ length: 30 }, () => generateMockAlert())
    setAlerts(initialAlerts)

    // Simulate new alerts arriving
    const interval = setInterval(() => {
      const newAlert = generateMockAlert()
      setAlerts(prev => [newAlert, ...prev].slice(0, 100))
    }, 20000) // New alert every 20 seconds

    return () => clearInterval(interval)
  }, [])

  const handleAlertClick = async (alert: Alert) => {
    setSelectedAlert(alert)
    setIsAnalyzing(true)
    setAiAnalysis(null)

    try {
      const agent = getAIAgent()
      await agent.initialize()
      const analysis = await agent.analyzeAlert(alert)
      setAiAnalysis(analysis)
    } catch (error) {
      console.error('Error analyzing alert:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleUpdateStatus = (newStatus: Alert['status']) => {
    if (!selectedAlert) return

    setAlerts(prev => prev.map(a => 
      a.id === selectedAlert.id ? { ...a, status: newStatus } : a
    ))
    setSelectedAlert(prev => prev ? { ...prev, status: newStatus } : null)
  }

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    const matchesSeverity = filterSeverity === 'all' || alert.severity === filterSeverity
    const matchesStatus = filterStatus === 'all' || alert.status === filterStatus
    const matchesSearch = searchTerm === '' || 
      alert.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.source.toLowerCase().includes(searchTerm.toLowerCase())
    
    return matchesSeverity && matchesStatus && matchesSearch
  })

  const newAlerts = alerts.filter(a => a.status === 'new').length
  const investigating = alerts.filter(a => a.status === 'investigating').length
  const resolved = alerts.filter(a => a.status === 'resolved').length

  return (
    <div className="p-6 space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="New Alerts"
          value={newAlerts}
          icon={AlertTriangle}
          color="red"
        />
        <StatsCard
          title="Investigating"
          value={investigating}
          icon={Clock}
          color="yellow"
        />
        <StatsCard
          title="Resolved Today"
          value={resolved}
          icon={CheckCircle}
          color="green"
        />
        <StatsCard
          title="Total Alerts"
          value={alerts.length}
          icon={Brain}
          color="blue"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts List */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Alert Queue</h2>
            <div className="flex gap-2">
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="px-3 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm border border-slate-700 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm border border-slate-700 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="new">New</option>
                <option value="investigating">Investigating</option>
                <option value="resolved">Resolved</option>
                <option value="false_positive">False Positive</option>
              </select>
            </div>
          </div>

          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search alerts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm border border-slate-700 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="space-y-3 max-h-[700px] overflow-y-auto">
            {filteredAlerts.map((alert) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                onClick={() => handleAlertClick(alert)}
              />
            ))}
            {filteredAlerts.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                No alerts match your filters
              </div>
            )}
          </div>
        </div>

        {/* Alert Details & AI Analysis */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-white mb-4">Alert Details</h2>
          
          {!selectedAlert ? (
            <div className="text-center py-12 text-slate-500">
              <Brain className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Select an alert to view details and AI analysis</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-slate-400 mb-2">Basic Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Type:</span>
                    <span className="text-slate-300 font-medium">{selectedAlert.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Source:</span>
                    <span className="text-slate-300 font-medium">{selectedAlert.source}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Time:</span>
                    <span className="text-slate-300">{formatTimeAgo(selectedAlert.timestamp)}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800">
                <h3 className="text-sm font-semibold text-slate-400 mb-2">Description</h3>
                <p className="text-sm text-slate-300">{selectedAlert.description}</p>
              </div>

              {/* AI Analysis */}
              <div className="pt-4 border-t border-slate-800">
                <h3 className="text-sm font-semibold text-slate-400 mb-3 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-blue-500" />
                  AI Analysis
                </h3>
                
                {isAnalyzing ? (
                  <div className="text-center py-6">
                    <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                    <p className="text-sm text-slate-500">Analyzing...</p>
                  </div>
                ) : aiAnalysis ? (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-500">Threat Score:</span>
                      <span className={`text-lg font-bold ${
                        aiAnalysis.threat_score > 0.7 ? 'text-red-500' :
                        aiAnalysis.threat_score > 0.4 ? 'text-yellow-500' :
                        'text-green-500'
                      }`}>
                        {(aiAnalysis.threat_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-500">Confidence:</span>
                      <span className="text-sm text-blue-400 font-medium">
                        {(aiAnalysis.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-500">False Positive:</span>
                      <span className="text-sm text-slate-400">
                        {(aiAnalysis.false_positive_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <div className="pt-3 border-t border-slate-800">
                      <h4 className="text-xs font-semibold text-slate-500 mb-2">Findings</h4>
                      <p className="text-xs text-slate-300">{aiAnalysis.findings}</p>
                    </div>

                    <div className="pt-3 border-t border-slate-800">
                      <h4 className="text-xs font-semibold text-slate-500 mb-2">Recommendations</h4>
                      <ul className="space-y-1">
                        {aiAnalysis.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : null}
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-slate-800 space-y-2">
                <h3 className="text-sm font-semibold text-slate-400 mb-3">Actions</h3>
                <button
                  onClick={() => handleUpdateStatus('investigating')}
                  className="w-full py-2 px-3 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Start Investigation
                </button>
                <button
                  onClick={() => handleUpdateStatus('resolved')}
                  className="w-full py-2 px-3 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Mark Resolved
                </button>
                <button
                  onClick={() => handleUpdateStatus('false_positive')}
                  className="w-full py-2 px-3 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Mark False Positive
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
