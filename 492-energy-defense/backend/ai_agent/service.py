"""
AI Agent Service - OpenRouter Integration
Performs threat analysis with configurable weighting and caching
"""
import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
import httpx
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIAgentService:
    """
    AI Agent for cybersecurity threat analysis
    Integrates with OpenRouter API and implements caching strategy
    """
    
    def __init__(
        self,
        openrouter_api_key: str,
        openrouter_model: str,
        redis_url: str,
        database_url: str
    ):
        self.api_key = openrouter_api_key
        self.model = openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        self.redis_url = redis_url
        self.database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # Initialize async components
        self.redis_client: Optional[aioredis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.db_engine = None
        self.AsyncSessionLocal = None
    
    async def initialize(self):
        """Initialize async connections"""
        try:
            # Redis connection for caching
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
            # HTTP client for OpenRouter
            self.http_client = httpx.AsyncClient(timeout=60.0)
            
            # Database connection
            self.db_engine = create_async_engine(self.database_url)
            self.AsyncSessionLocal = async_sessionmaker(
                self.db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("AI Agent Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent Service: {e}")
            raise
    
    async def close(self):
        """Close all connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.http_client:
            await self.http_client.aclose()
        if self.db_engine:
            await self.db_engine.dispose()
        logger.info("AI Agent Service connections closed")
    
    async def get_active_weights(self) -> Dict[str, Any]:
        """Fetch active AI weight configuration from database"""
        try:
            async with self.AsyncSessionLocal() as session:
                from api.models import AIWeightConfig
                
                result = await session.execute(
                    select(AIWeightConfig).where(AIWeightConfig.is_active == True)
                )
                config = result.scalar_one_or_none()
                
                if config:
                    return config.weights
                else:
                    # Default weights if none configured
                    return {
                        "firewall_threat_weight": 0.35,
                        "vulnerability_severity_weight": 0.30,
                        "patch_criticality_weight": 0.20,
                        "auth_anomaly_weight": 0.15,
                        "confidence_threshold": 0.70
                    }
        except Exception as e:
            logger.error(f"Failed to fetch weights: {e}")
            return {}
    
    async def query_openrouter(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query OpenRouter API with caching
        Returns AI response with metadata
        """
        # Generate cache key
        cache_key = f"ai_query:{hash(prompt)}"
        
        # Check cache first
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.info("Cache hit for AI query")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        # Prepare request
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://energy-defense.local",
            "X-Title": "492-Energy-Defense"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = {
                "content": result["choices"][0]["message"]["content"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache response for 1 hour
            try:
                await self.redis_client.setex(
                    cache_key,
                    3600,
                    json.dumps(ai_response)
                )
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
            
            return ai_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to query OpenRouter: {e}")
            raise
    
    async def analyze_threat_correlation(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze threat correlation across multiple data sources
        Applies configurable weights to determine threat severity
        """
        weights = await self.get_active_weights()
        
        # Build analysis prompt
        prompt = self._build_threat_analysis_prompt(data, weights)
        
        system_message = """You are a cybersecurity threat analysis AI for an energy sector defense system.
Analyze the provided security data and identify potential threats, correlations, and recommend actions.
Be concise, factual, and prioritize critical findings."""
        
        # Query AI
        ai_response = await self.query_openrouter(prompt, system_message)
        
        # Calculate confidence score based on data completeness and weights
        confidence = self._calculate_confidence(data, weights)
        
        # Determine threat level
        threat_level = self._determine_threat_level(data, weights, confidence)
        
        result = {
            "analysis_id": str(uuid4()),
            "analysis_type": "threat_correlation",
            "ai_response": ai_response["content"],
            "confidence_score": confidence,
            "threat_level": threat_level,
            "model_version": ai_response["model"],
            "weight_configuration": weights,
            "data_sources": list(data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store analysis in database
        await self._store_analysis(result)
        
        return result
    
    def _build_threat_analysis_prompt(
        self,
        data: Dict[str, Any],
        weights: Dict[str, Any]
    ) -> str:
        """Build structured prompt for threat analysis"""
        prompt_parts = [
            "# Cybersecurity Threat Analysis Request\n",
            "## Data Sources and Weights:\n"
        ]
        
        if "firewall_logs" in data:
            prompt_parts.append(
                f"- Firewall Events (weight: {weights.get('firewall_threat_weight', 0.35)}): "
                f"{len(data['firewall_logs'])} events\n"
            )
        
        if "vulnerabilities" in data:
            prompt_parts.append(
                f"- Vulnerabilities (weight: {weights.get('vulnerability_severity_weight', 0.30)}): "
                f"{len(data['vulnerabilities'])} findings\n"
            )
        
        if "patch_levels" in data:
            prompt_parts.append(
                f"- Patch Status (weight: {weights.get('patch_criticality_weight', 0.20)}): "
                f"{len(data['patch_levels'])} systems\n"
            )
        
        prompt_parts.append("\n## Security Data:\n")
        prompt_parts.append(json.dumps(data, indent=2, default=str))
        
        prompt_parts.append("\n## Analysis Request:\n")
        prompt_parts.append(
            "1. Identify critical threats and attack patterns\n"
            "2. Correlate events across data sources\n"
            "3. Assess overall risk level\n"
            "4. Provide prioritized remediation recommendations\n"
        )
        
        return "".join(prompt_parts)
    
    def _calculate_confidence(
        self,
        data: Dict[str, Any],
        weights: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on data completeness"""
        data_sources_count = len(data)
        max_sources = 4  # firewall, vulnerabilities, patches, auth
        
        completeness = data_sources_count / max_sources
        
        # Adjust by threshold
        threshold = weights.get("confidence_threshold", 0.70)
        confidence = min(completeness / threshold, 1.0)
        
        return round(confidence, 4)
    
    def _determine_threat_level(
        self,
        data: Dict[str, Any],
        weights: Dict[str, Any],
        confidence: float
    ) -> str:
        """Determine threat level based on weighted analysis"""
        severity_multipliers = weights.get("severity_multipliers", {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.50,
            "low": 0.25,
            "info": 0.10
        })
        
        threat_score = 0.0
        
        # Analyze firewall threats
        if "firewall_logs" in data:
            threat_indicators = sum(
                1 for log in data["firewall_logs"]
                if log.get("threat_indicator", False)
            )
            threat_score += (
                threat_indicators / max(len(data["firewall_logs"]), 1)
                * weights.get("firewall_threat_weight", 0.35)
            )
        
        # Analyze vulnerabilities
        if "vulnerabilities" in data:
            critical_vulns = sum(
                1 for vuln in data["vulnerabilities"]
                if vuln.get("severity") == "critical"
            )
            threat_score += (
                critical_vulns / max(len(data["vulnerabilities"]), 1)
                * weights.get("vulnerability_severity_weight", 0.30)
            )
        
        # Determine level
        if threat_score >= 0.75:
            return "critical"
        elif threat_score >= 0.50:
            return "high"
        elif threat_score >= 0.25:
            return "medium"
        else:
            return "low"
    
    async def _store_analysis(self, result: Dict[str, Any]):
        """Store analysis result in database"""
        try:
            async with self.AsyncSessionLocal() as session:
                from api.models import AIAnalysis
                
                analysis = AIAnalysis(
                    analysis_id=result["analysis_id"],
                    analysis_type=result["analysis_type"],
                    input_data={},  # Simplified for storage
                    ai_response=result["ai_response"],
                    confidence_score=result["confidence_score"],
                    threat_level=result["threat_level"],
                    data_sources=result["data_sources"],
                    weight_configuration=result["weight_configuration"],
                    model_version=result["model_version"]
                )
                
                session.add(analysis)
                await session.commit()
                logger.info(f"Stored analysis: {result['analysis_id']}")
                
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")


async def main():
    """Main service loop"""
    # Load configuration from environment
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo-preview")
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    database_url = os.getenv("DATABASE_URL")
    
    if not openrouter_api_key or not database_url:
        logger.error("Missing required environment variables")
        return
    
    # Initialize service
    agent = AIAgentService(
        openrouter_api_key=openrouter_api_key,
        openrouter_model=openrouter_model,
        redis_url=redis_url,
        database_url=database_url
    )
    
    try:
        await agent.initialize()
        logger.info("AI Agent Service running...")
        
        # Keep service alive
        while True:
            await asyncio.sleep(60)
            logger.info("AI Agent Service heartbeat")
            
    except KeyboardInterrupt:
        logger.info("Shutting down AI Agent Service...")
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
