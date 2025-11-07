import * as tf from '@tensorflow/tfjs'
import { Alert, AIAnalysis, AIModelWeights } from './types'

/**
 * TensorFlow-based AI Agent for threat triage and scoring
 * This agent evaluates security alerts and provides risk scoring
 */
export class ThreatAnalysisAgent {
  private model: tf.LayersModel | null = null
  private weights: AIModelWeights
  private isInitialized = false

  constructor(weights?: AIModelWeights) {
    this.weights = weights || this.getDefaultWeights()
  }

  /**
   * Initialize the TensorFlow model
   */
  async initialize(): Promise<void> {
    try {
      // Set TensorFlow backend
      await tf.ready()
      
      // Create a simple neural network for threat scoring
      this.model = tf.sequential({
        layers: [
          tf.layers.dense({ units: 64, activation: 'relu', inputShape: [5] }),
          tf.layers.dropout({ rate: 0.2 }),
          tf.layers.dense({ units: 32, activation: 'relu' }),
          tf.layers.dense({ units: 16, activation: 'relu' }),
          tf.layers.dense({ units: 1, activation: 'sigmoid' })
        ]
      })

      this.model.compile({
        optimizer: tf.train.adam(0.001),
        loss: 'binaryCrossentropy',
        metrics: ['accuracy']
      })

      this.isInitialized = true
      console.log('AI Agent initialized successfully')
    } catch (error) {
      console.error('Error initializing AI Agent:', error)
      throw error
    }
  }

  /**
   * Analyze an alert and provide AI scoring
   */
  async analyzeAlert(alert: Alert): Promise<AIAnalysis> {
    if (!this.isInitialized || !this.model) {
      await this.initialize()
    }

    // Extract features from alert
    const features = this.extractFeatures(alert)
    
    // Create tensor and predict
    const inputTensor = tf.tensor2d([features])
    const prediction = this.model!.predict(inputTensor) as tf.Tensor
    const threatScore = (await prediction.data())[0]

    // Calculate confidence based on feature consistency
    const confidence = this.calculateConfidence(features, threatScore)

    // Determine if likely false positive
    const falsePositiveProbability = this.calculateFalsePositiveProbability(alert, threatScore)

    // Generate findings and recommendations
    const findings = this.generateFindings(alert, threatScore, features)
    const recommendations = this.generateRecommendations(alert, threatScore)

    // Clean up tensors
    inputTensor.dispose()
    prediction.dispose()

    const analysis: AIAnalysis = {
      id: `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      alert_id: alert.id,
      analysis_type: 'threat_triage',
      threat_score: threatScore,
      confidence: confidence,
      findings: findings,
      recommendations: recommendations,
      false_positive_probability: falsePositiveProbability,
      model_version: '1.0.0'
    }

    return analysis
  }

  /**
   * Extract numerical features from alert for model input
   */
  private extractFeatures(alert: Alert): number[] {
    const severityMap = { critical: 1.0, high: 0.75, medium: 0.5, low: 0.25 }
    const severityScore = severityMap[alert.severity]

    // Feature engineering
    const features = [
      severityScore * this.weights.weights.severity_weight,
      this.calculateSourceRisk(alert.source) * this.weights.weights.source_reputation_weight,
      this.calculatePatternMatch(alert) * this.weights.weights.pattern_match_weight,
      this.calculateAnomalyScore(alert) * this.weights.weights.anomaly_score_weight,
      this.calculateFrequencyScore(alert) * this.weights.weights.frequency_weight
    ]

    return features
  }

  /**
   * Calculate source risk score (0-1)
   */
  private calculateSourceRisk(source: string): number {
    // In a real system, this would query threat intelligence databases
    const knownHighRiskSources = ['external', 'internet', 'unknown']
    const knownLowRiskSources = ['internal', 'trusted', 'scada']

    if (knownHighRiskSources.some(s => source.toLowerCase().includes(s))) {
      return 0.8 + Math.random() * 0.2
    } else if (knownLowRiskSources.some(s => source.toLowerCase().includes(s))) {
      return 0.1 + Math.random() * 0.2
    }
    return 0.4 + Math.random() * 0.3
  }

  /**
   * Calculate pattern match score based on known attack patterns
   */
  private calculatePatternMatch(alert: Alert): number {
    const attackPatterns = [
      'intrusion', 'malware', 'ransomware', 'dos', 'ddos', 
      'unauthorized', 'breach', 'exploit', 'injection'
    ]

    const description = alert.description.toLowerCase()
    const matches = attackPatterns.filter(pattern => description.includes(pattern))
    
    return Math.min(matches.length / 3, 1.0)
  }

  /**
   * Calculate anomaly score
   */
  private calculateAnomalyScore(alert: Alert): number {
    // Simulate anomaly detection based on alert characteristics
    const baseScore = 0.3 + Math.random() * 0.4
    
    // Adjust based on type
    if (alert.type.includes('anomaly') || alert.type.includes('unusual')) {
      return Math.min(baseScore + 0.3, 1.0)
    }
    
    return baseScore
  }

  /**
   * Calculate frequency score (higher if alert type is rare)
   */
  private calculateFrequencyScore(alert: Alert): number {
    // In production, this would check historical frequency
    // For simulation, return a reasonable value
    return 0.4 + Math.random() * 0.4
  }

  /**
   * Calculate confidence in the prediction
   */
  private calculateConfidence(features: number[], score: number): number {
    // Higher confidence if features are consistent with score
    const avgFeature = features.reduce((a, b) => a + b, 0) / features.length
    const consistency = 1 - Math.abs(score - avgFeature)
    return Math.max(0.5, Math.min(consistency + 0.2, 0.98))
  }

  /**
   * Calculate probability of false positive
   */
  private calculateFalsePositiveProbability(alert: Alert, score: number): number {
    let baseFP = 0.15

    // Lower FP probability for high scores and high severity
    if (score > 0.8 && alert.severity === 'critical') {
      baseFP = 0.05
    } else if (score < 0.3) {
      baseFP = 0.6
    }

    return baseFP + (Math.random() * 0.1 - 0.05)
  }

  /**
   * Generate human-readable findings
   */
  private generateFindings(alert: Alert, score: number, features: number[]): string {
    const findings: string[] = []

    if (score > 0.7) {
      findings.push(`High-confidence threat detected with score ${(score * 100).toFixed(1)}%.`)
    } else if (score > 0.4) {
      findings.push(`Moderate threat level with score ${(score * 100).toFixed(1)}%.`)
    } else {
      findings.push(`Low threat level detected (${(score * 100).toFixed(1)}%).`)
    }

    if (features[0] > 0.6) {
      findings.push('Alert severity indicates significant risk.')
    }

    if (features[1] > 0.7) {
      findings.push('Source has elevated risk profile based on threat intelligence.')
    }

    if (features[2] > 0.5) {
      findings.push('Alert matches known attack patterns.')
    }

    return findings.join(' ')
  }

  /**
   * Generate actionable recommendations
   */
  private generateRecommendations(alert: Alert, score: number): string[] {
    const recommendations: string[] = []

    if (score > 0.8) {
      recommendations.push('Immediate investigation required')
      recommendations.push('Isolate affected systems if confirmed')
      recommendations.push('Escalate to senior analyst')
      recommendations.push('Check for lateral movement indicators')
    } else if (score > 0.5) {
      recommendations.push('Assign to analyst for review')
      recommendations.push('Correlate with related events')
      recommendations.push('Monitor source for additional activity')
    } else {
      recommendations.push('Log and monitor')
      recommendations.push('Add to low-priority review queue')
      recommendations.push('Consider adjusting detection rules')
    }

    if (alert.severity === 'critical') {
      recommendations.push('Notify infrastructure team')
    }

    return recommendations
  }

  /**
   * Update model weights (Admin only function)
   */
  updateWeights(newWeights: AIModelWeights): void {
    this.weights = newWeights
    console.log('Model weights updated:', newWeights)
  }

  /**
   * Get current weights configuration
   */
  getWeights(): AIModelWeights {
    return { ...this.weights }
  }

  /**
   * Get default weights
   */
  private getDefaultWeights(): AIModelWeights {
    return {
      model_name: 'threat_triage_v1',
      weights: {
        severity_weight: 0.30,
        frequency_weight: 0.15,
        source_reputation_weight: 0.25,
        pattern_match_weight: 0.20,
        anomaly_score_weight: 0.10
      },
      threshold_settings: {
        critical_threshold: 0.80,
        high_threshold: 0.60,
        medium_threshold: 0.40,
        auto_escalate_threshold: 0.85
      },
      last_updated: new Date().toISOString(),
      updated_by: 'system'
    }
  }

  /**
   * Batch analyze multiple alerts
   */
  async analyzeAlerts(alerts: Alert[]): Promise<AIAnalysis[]> {
    const analyses: AIAnalysis[] = []
    
    for (const alert of alerts) {
      try {
        const analysis = await this.analyzeAlert(alert)
        analyses.push(analysis)
      } catch (error) {
        console.error(`Error analyzing alert ${alert.id}:`, error)
      }
    }

    return analyses
  }

  /**
   * Clean up resources
   */
  dispose(): void {
    if (this.model) {
      this.model.dispose()
      this.model = null
    }
    this.isInitialized = false
  }
}

// Singleton instance
let agentInstance: ThreatAnalysisAgent | null = null

export const getAIAgent = (): ThreatAnalysisAgent => {
  if (!agentInstance) {
    agentInstance = new ThreatAnalysisAgent()
  }
  return agentInstance
}
