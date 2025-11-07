"""
AI-powered security analysis service.
Implements threat correlation, risk assessment, and anomaly detection.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from app.services.openrouter import openrouter_client
from app.services.cache import cache_service

logger = logging.getLogger(__name__)


class SecurityAnalyzer:
    """AI-powered security analysis engine."""
    
    ANALYSIS_PROMPTS = {
        "threat_correlation": """You are a cybersecurity analyst for an energy sector organization. 
Analyze the following security data and identify correlations between different threat indicators.
Focus on patterns that might indicate coordinated attacks or persistent threats.

Security Data:
{data}

Weight Configuration:
{weights}

Provide a detailed analysis including:
1. Correlation patterns identified
2. Risk assessment (critical/high/medium/low)
3. Confidence score (0-100)
4. Specific recommendations for mitigation
5. Priority actions

Format your response as structured analysis with clear sections.""",
        
        "risk_assessment": """You are a cybersecurity risk analyst for critical energy infrastructure.
Perform a comprehensive risk assessment based on the provided security data.

Security Data:
{data}

Weight Configuration:
{weights}

Provide:
1. Overall risk level (critical/high/medium/low)
2. Key risk factors identified
3. Confidence score (0-100)
4. Asset criticality impact
5. Recommended risk mitigation strategies
6. Timeline for remediation actions

Be specific and actionable in your recommendations.""",
        
        "anomaly_detection": """You are a security anomaly detection specialist for energy sector systems.
Analyze the provided data for unusual patterns, outliers, or suspicious activities.

Security Data:
{data}

Weight Configuration:
{weights}

Identify:
1. Specific anomalies detected
2. Severity of each anomaly (critical/high/medium/low)
3. Confidence score (0-100)
4. Potential causes or explanations
5. Recommended investigation steps
6. Whether this could be part of a larger attack pattern

Focus on detecting sophisticated threats that might evade traditional detection.""",
        
        "trend_analysis": """You are a security trend analyst for critical infrastructure.
Analyze temporal patterns and trends in the security data.

Security Data:
{data}

Weight Configuration:
{weights}

Provide:
1. Key trends identified over time
2. Emerging threats or patterns
3. Confidence score (0-100)
4. Prediction of future security posture
5. Recommendations for proactive defense
6. Areas requiring increased monitoring

Focus on actionable insights for security operations.""",
        
        "incident_prediction": """You are a predictive security analyst for energy infrastructure.
Based on current security indicators, predict potential future incidents.

Security Data:
{data}

Weight Configuration:
{weights}

Provide:
1. Potential incident scenarios
2. Likelihood and severity assessment
3. Confidence score (0-100)
4. Indicators that support predictions
5. Preventive measures to implement
6. Early warning signs to monitor

Be specific about timeframes and threat vectors."""
    }
    
    def __init__(self):
        self.client = openrouter_client
        self.cache = cache_service
    
    async def analyze(
        self,
        analysis_type: str,
        source_data: Dict[str, Any],
        weight_config: Dict[str, Any],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform AI-powered security analysis.
        
        Args:
            analysis_type: Type of analysis to perform
            source_data: Security data to analyze
            weight_config: Weight configuration for analysis
            query: Optional custom query
            
        Returns:
            Dict containing analysis results
        """
        # Check cache first
        cache_key = self._generate_cache_key(analysis_type, source_data, weight_config)
        cached_result = await self.cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached result for analysis type: {analysis_type}")
            cached_result["cached"] = True
            return cached_result
        
        # Prepare prompt
        prompt_template = self.ANALYSIS_PROMPTS.get(analysis_type)
        if not prompt_template:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Format data and weights for the prompt
        formatted_data = self._format_security_data(source_data)
        formatted_weights = json.dumps(weight_config, indent=2)
        
        prompt = prompt_template.format(
            data=formatted_data,
            weights=formatted_weights
        )
        
        if query:
            prompt += f"\n\nSpecific Question: {query}"
        
        # System prompt for consistent behavior
        system_prompt = """You are an expert cybersecurity analyst specializing in energy sector critical infrastructure protection.
Your analyses must be:
- Technically accurate and detailed
- Actionable with specific recommendations
- Risk-aware and prioritized
- Compliant with energy sector security standards (NERC CIP, ICS security best practices)

Always provide confidence scores and severity assessments.
Focus on threats relevant to SCADA systems, ICS components, and energy infrastructure."""
        
        try:
            # Generate analysis
            result = await self.client.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            # Parse and structure the response
            analysis_result = self._structure_analysis(result, analysis_type, weight_config)
            
            # Cache the result
            await self.cache.set(cache_key, analysis_result)
            
            logger.info(f"Analysis completed: {analysis_type}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise
    
    def _format_security_data(self, data: Dict[str, Any]) -> str:
        """Format security data for LLM consumption."""
        formatted = []
        
        for category, items in data.items():
            formatted.append(f"\n=== {category.upper().replace('_', ' ')} ===")
            
            if isinstance(items, list):
                for idx, item in enumerate(items, 1):
                    formatted.append(f"\nEntry {idx}:")
                    formatted.append(json.dumps(item, indent=2, default=str))
            else:
                formatted.append(json.dumps(items, indent=2, default=str))
        
        return "\n".join(formatted)
    
    def _structure_analysis(
        self,
        raw_result: Dict[str, Any],
        analysis_type: str,
        weight_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Structure the raw AI response into a standardized format."""
        response_text = raw_result["response"]
        
        # Extract severity if present
        severity = self._extract_severity(response_text)
        
        # Extract confidence score if present
        confidence = self._extract_confidence(response_text)
        
        return {
            "analysis_type": analysis_type,
            "response": response_text,
            "confidence_score": confidence,
            "severity": severity,
            "recommendations": self._extract_recommendations(response_text),
            "weight_config": weight_config,
            "model_used": raw_result["model_used"],
            "tokens_used": raw_result["tokens_used"],
            "timestamp": raw_result["timestamp"],
            "cached": False
        }
    
    def _extract_severity(self, text: str) -> str:
        """Extract severity level from analysis text."""
        text_lower = text.lower()
        
        if "critical" in text_lower:
            return "critical"
        elif "high" in text_lower:
            return "high"
        elif "medium" in text_lower:
            return "medium"
        elif "low" in text_lower:
            return "low"
        
        return "informational"
    
    def _extract_confidence(self, text: str) -> Optional[Decimal]:
        """Extract confidence score from analysis text."""
        import re
        
        # Look for patterns like "confidence: 85", "85% confidence", etc.
        patterns = [
            r"confidence[:\s]+(\d+)",
            r"(\d+)%?\s*confidence",
            r"confidence score[:\s]+(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    return Decimal(str(score))
        
        # Default confidence if not found
        return Decimal("75.0")
    
    def _extract_recommendations(self, text: str) -> str:
        """Extract recommendations section from analysis text."""
        import re
        
        # Look for recommendations section
        patterns = [
            r"recommendations?:(.+?)(?=\n\n|\Z)",
            r"recommended.+?:(.+?)(?=\n\n|\Z)",
            r"mitigation.+?:(.+?)(?=\n\n|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower(), re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Return full text if no specific recommendations section found
        return text
    
    def _generate_cache_key(
        self,
        analysis_type: str,
        source_data: Dict[str, Any],
        weight_config: Dict[str, Any]
    ) -> str:
        """Generate a cache key for the analysis."""
        import hashlib
        
        # Create a deterministic hash of the inputs
        data_str = json.dumps({
            "type": analysis_type,
            "data": source_data,
            "weights": weight_config
        }, sort_keys=True, default=str)
        
        return f"analysis_{hashlib.sha256(data_str.encode()).hexdigest()}"


# Global analyzer instance
security_analyzer = SecurityAnalyzer()
