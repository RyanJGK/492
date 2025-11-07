import { useEffect, useState } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { SystemMetrics } from '@/lib/types'
import { generateMockSystemMetrics } from '@/lib/mock-data'

/**
 * Hook for subscribing to real-time system metrics
 * Falls back to mock data generation if Supabase is not configured
 */
export function useRealtimeMetrics(initialMetrics: SystemMetrics[] = []) {
  const [metrics, setMetrics] = useState<SystemMetrics[]>(initialMetrics)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (isSupabaseConfigured()) {
      // Supabase real-time subscription
      const channel = supabase
        .channel('metrics-channel')
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'system_metrics'
          },
          (payload) => {
            setMetrics((prev) => [...prev.slice(-19), payload.new as SystemMetrics])
          }
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            setIsConnected(true)
            console.log('Connected to real-time metrics')
          }
        })

      return () => {
        channel.unsubscribe()
        setIsConnected(false)
      }
    } else {
      // Mock data mode
      setIsConnected(true)

      const interval = setInterval(() => {
        const newMetric = generateMockSystemMetrics()
        setMetrics((prev) => [...prev.slice(-19), newMetric])
      }, 10000) // Update every 10 seconds

      return () => clearInterval(interval)
    }
  }, [])

  return { metrics, isConnected }
}
