import { useState, useEffect } from 'react'
import axios from 'axios'
import { useUser } from '../context/UserContext'
import StatsOverview from '../components/StatsOverview'
import ThreatsList from '../components/ThreatsList'
import ThreatTrendsChart from '../components/ThreatTrendsChart'
import VulnerabilitiesPanel from '../components/VulnerabilitiesPanel'
import AIControlPanel from '../components/AIControlPanel'
import AuditLogViewer from '../components/AuditLogViewer'
import { RefreshCw } from 'lucide-react'

export default function Dashboard() {
  const { user } = useUser()
  const [summary, setSummary] = useState(null)
  const [threats, setThreats] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchData = async () => {
    try {
      const [summaryRes, threatsRes] = await Promise.all([
        axios.get('/api/dashboard/summary'),
        axios.get('/api/ai/analyses?limit=20'),
      ])
      
      setSummary(summaryRes.data)
      setThreats(threatsRes.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchData()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Security Operations Dashboard
          </h1>
          <p className="text-gray-600 mt-1">
            Real-time monitoring and AI-powered threat analysis
          </p>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Overview */}
      {summary && <StatsOverview summary={summary} />}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Threats and Trends */}
        <div className="lg:col-span-2 space-y-6">
          <ThreatTrendsChart />
          <ThreatsList threats={threats} onRefresh={fetchData} />
        </div>

        {/* Right Column - Panels */}
        <div className="space-y-6">
          <VulnerabilitiesPanel />
          
          {/* AI Control Panel - Admin Only */}
          {user && user.role === 'admin' && (
            <AIControlPanel />
          )}
          
          {/* Audit Log - Admin Only */}
          {user && user.role === 'admin' && (
            <AuditLogViewer />
          )}
        </div>
      </div>
    </div>
  )
}
