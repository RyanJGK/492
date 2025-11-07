"""
TensorFlow model manager for threat classification
Implements configurable weighting and explainability
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow import keras
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ModelManager:
    """
    Manages TensorFlow threat classification model
    Supports configurable feature weighting and explainability
    """
    
    def __init__(self):
        self.model: Optional[keras.Model] = None
        self.feature_names = [
            "auth_events",
            "vulnerability_severity",
            "firewall_anomalies",
            "patch_criticality",
        ]
        self.default_weights = {
            "auth_events": 0.30,
            "vulnerability_severity": 0.35,
            "firewall_anomalies": 0.25,
            "patch_criticality": 0.10,
        }
        self.current_weights = self.default_weights.copy()
        self._ready = False
    
    async def initialize(self) -> None:
        """Initialize or build the TensorFlow model"""
        model_path = os.path.join(settings.MODEL_PATH, "threat_classifier.h5")
        
        if os.path.exists(model_path):
            try:
                self.model = keras.models.load_model(model_path)
                logger.info("model_loaded_from_disk", path=model_path)
            except Exception as e:
                logger.warning("model_load_failed", error=str(e))
                self._build_model()
        else:
            self._build_model()
        
        self._ready = True
        logger.info("model_manager_initialized")
    
    def _build_model(self) -> None:
        """
        Build a simple neural network for threat classification
        This is a deterministic model for demonstration
        """
        # Simple feedforward network
        model = keras.Sequential([
            keras.layers.Input(shape=(4,), name="features"),
            keras.layers.Dense(16, activation="relu", name="hidden1"),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(8, activation="relu", name="hidden2"),
            keras.layers.Dense(1, activation="sigmoid", name="output"),
        ])
        
        model.compile(
            optimizer="adam",
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )
        
        self.model = model
        logger.info("model_built", architecture="sequential")
        
        # Save the model
        try:
            os.makedirs(settings.MODEL_PATH, exist_ok=True)
            model_path = os.path.join(settings.MODEL_PATH, "threat_classifier.h5")
            model.save(model_path)
            logger.info("model_saved", path=model_path)
        except Exception as e:
            logger.warning("model_save_failed", error=str(e))
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self._ready and self.model is not None
    
    def update_weights(self, weights: Dict[str, float]) -> None:
        """
        Update feature importance weights
        Must be called by admin users only
        """
        # Validate weights sum to 1.0
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.current_weights = weights.copy()
        logger.info("weights_updated", weights=self.current_weights)
    
    def _compute_feature_scores(
        self,
        auth_score: float,
        vuln_score: float,
        firewall_score: float,
        patch_score: float,
    ) -> Dict[str, float]:
        """
        Compute weighted feature scores
        All inputs should be normalized to [0, 1]
        """
        scores = {
            "auth_events": auth_score,
            "vulnerability_severity": vuln_score,
            "firewall_anomalies": firewall_score,
            "patch_criticality": patch_score,
        }
        
        # Apply weights
        weighted_scores = {
            feature: score * self.current_weights[feature]
            for feature, score in scores.items()
        }
        
        return weighted_scores
    
    def _compute_confidence(
        self,
        model_output: float,
        feature_variance: float,
    ) -> float:
        """
        Compute confidence score based on model output and feature variance
        Higher variance = lower confidence
        """
        # Base confidence from model certainty
        base_confidence = abs(model_output - 0.5) * 2  # Maps [0.5, 1.0] to [0, 1]
        
        # Adjust for feature variance (low variance = high confidence)
        variance_factor = 1.0 - min(feature_variance, 0.5) * 2
        
        confidence = (base_confidence + variance_factor) / 2
        return float(np.clip(confidence, 0, 1))
    
    def _categorize_threat(
        self,
        threat_score: float,
        weighted_scores: Dict[str, float],
    ) -> str:
        """
        Categorize threat based on dominant feature
        """
        dominant_feature = max(weighted_scores, key=weighted_scores.get)
        
        categories = {
            "auth_events": "authentication_anomaly",
            "vulnerability_severity": "vulnerability_exploitation",
            "firewall_anomalies": "network_intrusion",
            "patch_criticality": "misconfiguration",
        }
        
        return categories.get(dominant_feature, "unknown")
    
    def _determine_severity(self, threat_score: float) -> str:
        """Determine severity level from threat score"""
        if threat_score >= 0.85:
            return "critical"
        elif threat_score >= 0.65:
            return "high"
        elif threat_score >= 0.40:
            return "medium"
        elif threat_score >= 0.20:
            return "low"
        else:
            return "info"
    
    def _generate_recommendations(
        self,
        threat_category: str,
        severity: str,
        weighted_scores: Dict[str, float],
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if threat_category == "authentication_anomaly":
            recommendations.extend([
                "Review recent authentication logs for suspicious activity",
                "Verify user account integrity and permissions",
                "Consider implementing multi-factor authentication",
            ])
        elif threat_category == "vulnerability_exploitation":
            recommendations.extend([
                "Apply available security patches immediately",
                "Isolate affected systems if exploitation is confirmed",
                "Review vulnerability scan results in detail",
            ])
        elif threat_category == "network_intrusion":
            recommendations.extend([
                "Analyze firewall logs for attack patterns",
                "Update firewall rules to block malicious IPs",
                "Monitor network traffic for lateral movement",
            ])
        elif threat_category == "misconfiguration":
            recommendations.extend([
                "Review system configurations against security baselines",
                "Schedule pending critical patches",
                "Implement configuration management automation",
            ])
        
        if severity in ["critical", "high"]:
            recommendations.insert(0, "IMMEDIATE ACTION REQUIRED: Escalate to incident response team")
        
        return recommendations
    
    async def analyze_threat(
        self,
        auth_score: float,
        vuln_score: float,
        firewall_score: float,
        patch_score: float,
    ) -> Dict[str, Any]:
        """
        Perform threat analysis using the TensorFlow model
        
        Args:
            auth_score: Authentication anomaly score [0, 1]
            vuln_score: Vulnerability severity score [0, 1]
            firewall_score: Firewall anomaly score [0, 1]
            patch_score: Patch criticality score [0, 1]
        
        Returns:
            Complete analysis with explainability
        """
        if not self.is_ready():
            raise RuntimeError("Model not ready")
        
        # Compute weighted scores
        weighted_scores = self._compute_feature_scores(
            auth_score, vuln_score, firewall_score, patch_score
        )
        
        # Prepare input for model
        features = np.array([[
            auth_score,
            vuln_score,
            firewall_score,
            patch_score,
        ]], dtype=np.float32)
        
        # Model inference
        model_output = self.model.predict(features, verbose=0)[0][0]
        
        # Apply weighted aggregation
        weighted_sum = sum(weighted_scores.values())
        threat_score = float((model_output + weighted_sum) / 2)
        threat_score = np.clip(threat_score, 0, 1)
        
        # Compute feature variance for confidence calculation
        feature_variance = float(np.var([auth_score, vuln_score, firewall_score, patch_score]))
        confidence = self._compute_confidence(threat_score, feature_variance)
        
        # Categorize and determine severity
        threat_category = self._categorize_threat(threat_score, weighted_scores)
        severity = self._determine_severity(threat_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            threat_category, severity, weighted_scores
        )
        
        # Build explanation
        explanation = self._build_explanation(
            threat_score, confidence, weighted_scores, feature_variance
        )
        
        return {
            "threat_score": float(threat_score),
            "confidence_score": float(confidence),
            "threat_category": threat_category,
            "severity": severity,
            "explanation": explanation,
            "recommended_actions": recommendations,
            "weight_application": self.current_weights.copy(),
            "contributing_events": {
                "auth_events": {"score": float(auth_score), "weighted": float(weighted_scores["auth_events"])},
                "vulnerability_severity": {"score": float(vuln_score), "weighted": float(weighted_scores["vulnerability_severity"])},
                "firewall_anomalies": {"score": float(firewall_score), "weighted": float(weighted_scores["firewall_anomalies"])},
                "patch_criticality": {"score": float(patch_score), "weighted": float(weighted_scores["patch_criticality"])},
            },
            "model_version": "1.0.0",
            "analysis_time": datetime.utcnow().isoformat(),
        }
    
    def _build_explanation(
        self,
        threat_score: float,
        confidence: float,
        weighted_scores: Dict[str, float],
        variance: float,
    ) -> str:
        """Build human-readable explanation of the analysis"""
        dominant = max(weighted_scores, key=weighted_scores.get)
        dominant_name = dominant.replace("_", " ").title()
        
        explanation = (
            f"Threat score of {threat_score:.3f} ({confidence*100:.1f}% confidence) "
            f"primarily driven by {dominant_name} "
            f"(weighted contribution: {weighted_scores[dominant]:.3f}). "
        )
        
        # Add context about other contributing factors
        other_factors = [
            f"{k.replace('_', ' ').title()} ({v:.3f})"
            for k, v in weighted_scores.items() if k != dominant and v > 0.1
        ]
        
        if other_factors:
            explanation += f"Additional factors: {', '.join(other_factors)}. "
        
        # Add confidence context
        if confidence < 0.6:
            explanation += "Note: Low confidence due to inconsistent feature values."
        elif confidence > 0.85:
            explanation += "High confidence assessment based on consistent indicators."
        
        return explanation
