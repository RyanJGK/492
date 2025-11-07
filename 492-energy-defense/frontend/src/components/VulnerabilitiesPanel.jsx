import { useState, useEffect } from 'react'
import axios from 'axios'
import { Shield, TrendingUp } from 'lucide-react'

export default function VulnerabilitiesPanel() {
  const [vulnerabilities, setVulnerabilities] = useState([])
  const [severityCounts, setSeverityCounts] = useState({})

  useEffect(() => {
    Promise.all([
      axios.get('/api/vulnerabilities?status=open&limit=5'),
      axios.get('/api/dashboard/vulnerabilities/by-severity'),
    ])
      .then(([vulnsRes, countsRes]) => {
        setVulnerabilities(vulnsRes.data)
        setSeverityCounts(countsRes.data)
      })
      .catch(error => console.error('Failed to fetch vulnerabilities:', error))
  }, [])

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'high': return 'text-orange-600 bg-orange-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Shield className="w-5 h-5 text-blue-600" />
        <h2 className="text-lg font-bold text-gray-900">
          Open Vulnerabilities
        </h2>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-4">
        {Object.entries(severityCounts).map(([severity, count]) => (
          <div
            key={severity}
            className={`p-3 rounded-lg ${getSeverityColor(severity)}`}
          >
            <div className="text-2xl font-bold">{count}</div>
            <div className="text-xs capitalize">{severity}</div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {vulnerabilities.slice(0, 5).map((vuln) => (
          <div
            key={vuln.id}
            className="border border-gray-200 rounded p-3 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between mb-1">
              <span className="text-sm font-medium text-gray-900">
                {vuln.cve_id || vuln.vuln_id}
              </span>
              <span className={`text-xs px-2 py-1 rounded capitalize ${getSeverityColor(vuln.severity)}`}>
                {vuln.severity}
              </span>
            </div>
            <p className="text-xs text-gray-600 truncate">
              {vuln.affected_system}
            </p>
            {vuln.cvss_score && (
              <div className="text-xs text-gray-500 mt-1">
                CVSS: {vuln.cvss_score.toFixed(1)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
