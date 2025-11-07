import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export function formatTimeAgo(timestamp: string): string {
  const now = Date.now()
  const then = new Date(timestamp).getTime()
  const diff = now - then

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  return `${seconds}s ago`
}

export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-red-500 bg-red-500/10 border-red-500/20'
    case 'high':
      return 'text-orange-500 bg-orange-500/10 border-orange-500/20'
    case 'medium':
      return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20'
    case 'low':
      return 'text-blue-500 bg-blue-500/10 border-blue-500/20'
    default:
      return 'text-gray-500 bg-gray-500/10 border-gray-500/20'
  }
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'new':
      return 'text-purple-500 bg-purple-500/10'
    case 'investigating':
      return 'text-yellow-500 bg-yellow-500/10'
    case 'resolved':
      return 'text-green-500 bg-green-500/10'
    case 'false_positive':
      return 'text-gray-500 bg-gray-500/10'
    case 'open':
      return 'text-red-500 bg-red-500/10'
    case 'in_progress':
      return 'text-blue-500 bg-blue-500/10'
    case 'patched':
    case 'deployed':
      return 'text-green-500 bg-green-500/10'
    case 'mitigated':
      return 'text-teal-500 bg-teal-500/10'
    case 'accepted':
      return 'text-gray-500 bg-gray-500/10'
    case 'failed':
      return 'text-red-500 bg-red-500/10'
    default:
      return 'text-gray-500 bg-gray-500/10'
  }
}

export function formatNumber(num: number, decimals: number = 0): string {
  return num.toFixed(decimals)
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
