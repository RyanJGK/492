// Supabase Edge Function to generate synthetic alerts
// This function simulates a live SOC environment by creating periodic alerts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Alert generation configuration
    const alertTypes = [
      'Intrusion Detection',
      'Malware Detection',
      'Unauthorized Access',
      'DDoS Attack',
      'Port Scan',
      'Brute Force Attempt',
      'Data Exfiltration',
      'Anomalous Network Traffic',
      'Suspicious Login',
      'Configuration Change',
      'SCADA Protocol Violation',
      'ICS Command Injection'
    ]

    const sources = [
      'Firewall-01',
      'IDS-Gateway',
      'SCADA-Monitor',
      'Substation-Alpha',
      'Substation-Beta',
      'Substation-Gamma',
      'Distribution-Controller',
      'External-Perimeter',
      'VPN-Gateway',
      'Authentication-Server'
    ]

    const descriptions = [
      'Multiple failed authentication attempts detected',
      'Suspicious network traffic pattern identified',
      'Unauthorized access attempt to SCADA system',
      'Malicious payload detected in network stream',
      'Abnormal data transfer volume detected',
      'Unknown device attempting connection',
      'Critical system file modification detected',
      'Port scanning activity from external IP',
      'SQL injection attempt on web interface',
      'Privilege escalation attempt detected'
    ]

    const severities = ['critical', 'high', 'medium', 'low']

    // Generate random alert
    const severity = severities[Math.floor(Math.random() * severities.length)]
    const type = alertTypes[Math.floor(Math.random() * alertTypes.length)]
    const source = sources[Math.floor(Math.random() * sources.length)]
    const description = descriptions[Math.floor(Math.random() * descriptions.length)]

    const newAlert = {
      timestamp: new Date().toISOString(),
      severity,
      type,
      source,
      description,
      status: 'new',
      ai_score: Math.random(),
      ai_confidence: 0.6 + Math.random() * 0.35,
      metadata: {
        source_ip: `10.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        destination_port: [22, 80, 443, 3389, 502, 20000][Math.floor(Math.random() * 6)],
        auto_generated: true
      }
    }

    // Insert alert into database
    const { data, error } = await supabase
      .from('alerts')
      .insert([newAlert])
      .select()

    if (error) {
      throw error
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        alert: data[0],
        message: 'Alert generated successfully' 
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message 
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      }
    )
  }
})
