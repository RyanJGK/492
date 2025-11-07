'use client'

import React, { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, Shield, Activity, AlertTriangle, Clock, CheckCircle } from 'lucide-react'
import StatsCard from '@/components/StatsCard'
import { Alert, SystemMetrics } from '@/lib/types'
import { generateMockAlert, generateMockSystemMetrics } from '@/lib/mock-data'
import { formatTimeAgo } from '@/lib/utils'

export default function ObserverView() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [metrics, setMetrics] = useState<SystemMetrics[]>([])

  useEffect(() => {
    // Initialize with mock data
    const initialAlerts = Array.from({ length: 50 }, () => generateMockAlert())
    setAlerts(initialAlerts)

    const initialMetrics = Array.from({ length: 20 }, (_, i) => ({
      ...generateMockSystemMetrics(),
      timestamp: new Date(Date.now() - (19 - i) * 60000).toISOString()
    }))
    setMetrics(initialMetrics)

    // Update metrics every 10 seconds
    const metricsInterval = setInterval(() => {
      setMetrics(prev => {
        const newMetric = generateMockSystemMetrics()
        return [...prev.slice(1), newMetric]
      })
    }, 10000)

    // Simulate new alerts
    const alertInterval = setInterval(() => {
      const newAlert = generateMockAlert()
      setAlerts(prev => [newAlert, ...prev].slice(0, 100))
    }, 25000)

    return () => {
      clearInterval(metricsInterval)
      clearInterval(alertInterval)
    }
  }, [])

  // Calculate statistics
  const totalAlerts = alerts.length
  const criticalAlerts = alerts.filter(a => a.severity === 'critical').length
  const resolvedAlerts = alerts.filter(a => a.status === 'resolved').length
  const avgResponseTime = '12.3' // Mock value

  // Severity distribution
  const severityData = [
    { name: 'Critical', value: alerts.filter(a => a.severity === 'critical').length, color: '#ef4444' },
    { name: 'High', value: alerts.filter(a => a.severity === 'high').length, color: '#f97316' },
    { name: 'Medium', value: alerts.filter(a => a.severity === 'medium').length, color: '#eab308' },
    { name: 'Low', value: alerts.filter(a => a.severity === 'low').length, color: '#3b82f6' }
  ]

  // Status distribution
  const statusData = [
    { name: 'New', value: alerts.filter(a => a.status === 'new').length },
    { name: 'Investigating', value: alerts.filter(a => a.status === 'investigating').length },
    { name: 'Resolved', value: alerts.filter(a => a.status === 'resolved').length },
    { name: 'False Positive', value: alerts.filter(a => a.status === 'false_positive').length }
  ]

  // Alert trend over time (hourly buckets)
  const alertTrend = (() => {
    const hours = 12
    const data = []
    for (let i = hours - 1; i >= 0; i--) {
      const hourStart = Date.now() - i * 3600000
      const hourEnd = hourStart + 3600000
      const count = alerts.filter(a => {
        const time = new Date(a.timestamp).getTime()
        return time >= hourStart && time < hourEnd
      }).length
      data.push({
        hour: `${i}h ago`,
        alerts: count
      })
    }
    return data
  })()

  // System metrics chart data
  const metricsChartData = metrics.map((m, i) => ({
    time: i,
    cpu: m.cpu_usage,
    memory: m.memory_usage,
    threats: m.threat_events_per_minute
  }))

  return (
    <div className="p-6 space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Alerts"
          value={totalAlerts}
          icon={AlertTriangle}
          color="blue"
          subtitle="Last 24 hours"
        />
        <StatsCard
          title="Critical Alerts"
          value={criticalAlerts}
          icon={Shield}
          color="red"
        />
        <StatsCard
          title="Resolved"
          value={resolvedAlerts}
          icon={CheckCircle}
          color="green"
          subtitle={`${((resolvedAlerts / totalAlerts) * 100).toFixed(0)}% resolution rate`}
        />
        <StatsCard
          title="Avg Response Time"
          value={`${avgResponseTime}m`}
          icon={Clock}
          color="purple"
          trend={{ value: 8, isPositive: true }}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alert Trend */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-white mb-4">Alert Trend (12h)</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={alertTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="hour" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Line type="monotone" dataKey="alerts" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-white mb-4">Severity Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-white mb-4">Alert Status Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* System Metrics */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-white mb-4">System Performance</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={metricsChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              <Line type="monotone" dataKey="cpu" stroke="#3b82f6" name="CPU %" />
              <Line type="monotone" dataKey="memory" stroke="#10b981" name="Memory %" />
              <Line type="monotone" dataKey="threats" stroke="#ef4444" name="Threats/min" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
        <h2 className="text-lg font-bold text-white mb-4">Recent Activity</h2>
        <div className="space-y-3 max-h-[400px] overflow-y-auto">
          {alerts.slice(0, 15).map((alert) => (
            <div key={alert.id} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
              <div className={`p-2 rounded-lg ${
                alert.severity === 'critical' ? 'bg-red-500/20' :
                alert.severity === 'high' ? 'bg-orange-500/20' :
                alert.severity === 'medium' ? 'bg-yellow-500/20' :
                'bg-blue-500/20'
              }`}>
                <AlertTriangle className={`w-4 h-4 ${
                  alert.severity === 'critical' ? 'text-red-500' :
                  alert.severity === 'high' ? 'text-orange-500' :
                  alert.severity === 'medium' ? 'text-yellow-500' :
                  'text-blue-500'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{alert.type}</p>
                    <p className="text-xs text-slate-400">{alert.source}</p>
                  </div>
                  <span className="text-xs text-slate-500 whitespace-nowrap">
                    {formatTimeAgo(alert.timestamp)}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1 line-clamp-1">{alert.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
