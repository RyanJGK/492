import React from 'react'
import { Alert } from '@/lib/types'
import { formatTimeAgo, getSeverityColor, getStatusColor } from '@/lib/utils'
import { AlertCircle, Clock, Activity } from 'lucide-react'

interface AlertCardProps {
  alert: Alert
  onClick?: () => void
}

export default function AlertCard({ alert, onClick }: AlertCardProps) {
  const severityClass = getSeverityColor(alert.severity)
  const statusClass = getStatusColor(alert.status)

  return (
    <div
      onClick={onClick}
      className="bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${severityClass}`}>
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-white text-sm">{alert.type}</h3>
            <p className="text-xs text-slate-400 mt-1">{alert.source}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={`px-2 py-1 rounded text-xs font-medium ${severityClass}`}>
            {alert.severity.toUpperCase()}
          </span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${statusClass}`}>
            {alert.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      <p className="text-sm text-slate-300 mb-3">{alert.description}</p>

      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1 text-slate-400">
            <Clock className="w-3 h-3" />
            <span>{formatTimeAgo(alert.timestamp)}</span>
          </div>
          {alert.ai_score !== undefined && (
            <div className="flex items-center gap-1 text-blue-400">
              <Activity className="w-3 h-3" />
              <span>AI: {(alert.ai_score * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
        {alert.metadata?.source_ip && (
          <span className="text-slate-500 font-mono text-xs">
            {alert.metadata.source_ip}
          </span>
        )}
      </div>
    </div>
  )
}
