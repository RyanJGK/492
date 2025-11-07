// Supabase Edge Function for AI threat analysis
// This function triggers AI analysis on new alerts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    const supabase = createClient(supabaseUrl, supabaseKey)

    const { alert_id } = await req.json()

    if (!alert_id) {
      throw new Error('alert_id is required')
    }

    // Fetch the alert
    const { data: alert, error: alertError } = await supabase
      .from('alerts')
      .select('*')
      .eq('id', alert_id)
      .single()

    if (alertError || !alert) {
      throw new Error('Alert not found')
    }

    // Fetch active AI model weights
    const { data: weights } = await supabase
      .from('ai_model_weights')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    // Perform simplified threat analysis
    // In production, this would call the actual TensorFlow model
    const severityScore = {
      'critical': 1.0,
      'high': 0.75,
      'medium': 0.5,
      'low': 0.25
    }[alert.severity] || 0.5

    const threatScore = severityScore * 0.7 + Math.random() * 0.3
    const confidence = 0.65 + Math.random() * 0.3

    const recommendations = []
    if (threatScore > 0.8) {
      recommendations.push('Immediate investigation required')
      recommendations.push('Isolate affected systems if confirmed')
      recommendations.push('Escalate to senior analyst')
    } else if (threatScore > 0.5) {
      recommendations.push('Assign to analyst for review')
      recommendations.push('Correlate with related events')
      recommendations.push('Monitor source for additional activity')
    } else {
      recommendations.push('Log and monitor')
      recommendations.push('Add to low-priority review queue')
    }

    // Create AI analysis record
    const analysis = {
      timestamp: new Date().toISOString(),
      alert_id: alert.id,
      analysis_type: 'threat_triage',
      threat_score: threatScore,
      confidence: confidence,
      findings: `Threat analysis completed with ${(confidence * 100).toFixed(0)}% confidence. Score: ${(threatScore * 100).toFixed(0)}%`,
      recommendations: recommendations,
      false_positive_probability: Math.max(0, 1 - threatScore - 0.2),
      model_version: weights?.model_name || 'v1.0.0'
    }

    const { data, error } = await supabase
      .from('ai_analysis')
      .insert([analysis])
      .select()

    if (error) {
      throw error
    }

    // Update alert with AI scores
    await supabase
      .from('alerts')
      .update({
        ai_score: threatScore,
        ai_confidence: confidence
      })
      .eq('id', alert_id)

    return new Response(
      JSON.stringify({ 
        success: true, 
        analysis: data[0] 
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
