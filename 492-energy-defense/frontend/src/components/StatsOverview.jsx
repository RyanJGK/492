import { AlertTriangle, Shield, FileWarning, Activity } from 'lucide-react'

export default function StatsOverview({ summary }) {
  const stats = [
    {
      title: 'Critical Threats',
      value: summary.critical_threats,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
    },
    {
      title: 'High Priority',
      value: summary.high_threats,
      icon: FileWarning,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
    },
    {
      title: 'Open Vulnerabilities',
      value: summary.open_vulnerabilities,
      icon: Shield,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
    },
    {
      title: 'Pending Patches',
      value: summary.pending_patches,
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className={`bg-white rounded-lg shadow-md border-2 ${stat.borderColor} p-6 hover:shadow-lg transition-shadow`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                {stat.title}
              </p>
              <p className={`text-3xl font-bold mt-2 ${stat.color}`}>
                {stat.value}
              </p>
            </div>
            <div className={`${stat.bgColor} p-3 rounded-lg`}>
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
