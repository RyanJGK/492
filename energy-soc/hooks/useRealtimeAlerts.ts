import { useEffect, useState } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { Alert } from '@/lib/types'
import { generateMockAlert } from '@/lib/mock-data'

/**
 * Hook for subscribing to real-time alert updates from Supabase
 * Falls back to mock data generation if Supabase is not configured
 */
export function useRealtimeAlerts(initialAlerts: Alert[] = []) {
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (isSupabaseConfigured()) {
      // Supabase real-time subscription
      const channel = supabase
        .channel('alerts-channel')
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'alerts'
          },
          (payload) => {
            console.log('New alert received:', payload.new)
            setAlerts((prev) => [payload.new as Alert, ...prev])
          }
        )
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'alerts'
          },
          (payload) => {
            console.log('Alert updated:', payload.new)
            setAlerts((prev) =>
              prev.map((alert) =>
                alert.id === payload.new.id ? (payload.new as Alert) : alert
              )
            )
          }
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            setIsConnected(true)
            console.log('Connected to real-time alerts')
          }
        })

      return () => {
        channel.unsubscribe()
        setIsConnected(false)
      }
    } else {
      // Mock data mode - simulate real-time alerts
      console.log('Running in mock data mode (Supabase not configured)')
      setIsConnected(true)

      const interval = setInterval(() => {
        const newAlert = generateMockAlert()
        setAlerts((prev) => [newAlert, ...prev].slice(0, 100))
      }, 15000) // New alert every 15 seconds

      return () => clearInterval(interval)
    }
  }, [])

  return { alerts, isConnected }
}
