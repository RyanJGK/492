import { useState, useEffect } from 'react'
import axios from 'axios'
import { FileText, ChevronDown, ChevronUp } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function AuditLogViewer() {
  const [logs, setLogs] = useState([])
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/audit/logs?limit=10')
      .then(response => {
        setLogs(response.data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Failed to fetch audit logs:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-bold text-gray-900">
            Audit Log
          </h2>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
        >
          {expanded ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </button>
      </div>

      {loading ? (
        <div className="text-center py-4 text-gray-500">Loading...</div>
      ) : (
        <div className="space-y-2">
          {logs.slice(0, expanded ? logs.length : 5).map((log) => (
            <div
              key={log.id}
              className="border border-gray-200 rounded p-3 text-sm"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-gray-900 capitalize">
                  {log.action.replace(/_/g, ' ')}
                </span>
                <span className={`px-2 py-1 rounded text-xs ${
                  log.success 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {log.success ? 'Success' : 'Failed'}
                </span>
              </div>
              <div className="text-xs text-gray-600 space-y-1">
                <div>User: {log.username || 'System'}</div>
                <div>Resource: {log.resource_type}</div>
                <div>{formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
