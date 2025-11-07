import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'
import { format } from 'date-fns'

export default function ThreatTrendsChart() {
  const [data, setData] = useState([])
  const [timeRange, setTimeRange] = useState(24)

  useEffect(() => {
    axios.get(`/api/dashboard/threats/trends?hours=${timeRange}`)
      .then(response => {
        // Group by timestamp and aggregate
        const grouped = {}
        response.data.forEach(item => {
          const time = format(new Date(item.timestamp), 'HH:mm')
          if (!grouped[time]) {
            grouped[time] = { time, critical: 0, high: 0, medium: 0, low: 0 }
          }
          grouped[time][item.severity] = (grouped[time][item.severity] || 0) + item.threat_count
        })
        
        setData(Object.values(grouped))
      })
      .catch(error => console.error('Failed to fetch trends:', error))
  }, [timeRange])

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Threat Trends</h2>
        
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value={6}>Last 6 hours</option>
          <option value={24}>Last 24 hours</option>
          <option value={72}>Last 3 days</option>
          <option value={168}>Last week</option>
        </select>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="critical" stroke="#dc2626" strokeWidth={2} name="Critical" />
          <Line type="monotone" dataKey="high" stroke="#f97316" strokeWidth={2} name="High" />
          <Line type="monotone" dataKey="medium" stroke="#fbbf24" strokeWidth={2} name="Medium" />
          <Line type="monotone" dataKey="low" stroke="#3b82f6" strokeWidth={2} name="Low" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
