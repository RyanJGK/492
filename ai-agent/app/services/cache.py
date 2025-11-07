"""
Simple file-based caching service for AI analysis results.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """File-based cache service for AI analysis results."""
    
    def __init__(self):
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_enabled = settings.CACHE_ENABLED
        self.ttl_hours = settings.CACHE_TTL_HOURS
        
        # Ensure cache directory exists
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache initialized at {self.cache_dir}")
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check TTL
            cached_at = datetime.fromisoformat(cached_data["cached_at"])
            expiry = cached_at + timedelta(hours=self.ttl_hours)
            
            if datetime.utcnow() > expiry:
                logger.debug(f"Cache expired for key: {key}")
                cache_file.unlink()
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return cached_data["value"]
            
        except Exception as e:
            logger.warning(f"Cache read error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False
        
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            cached_data = {
                "key": key,
                "value": value,
                "cached_at": datetime.utcnow().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2, default=str)
            
            logger.debug(f"Cached value for key: {key}")
            return True
            
        except Exception as e:
            logger.warning(f"Cache write error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete cached value.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.cache_enabled:
            return False
        
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Deleted cache for key: {key}")
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear(self) -> int:
        """
        Clear all cached values.
        
        Returns:
            Number of cache entries cleared
        """
        if not self.cache_enabled:
            return 0
        
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            
            logger.info(f"Cleared {count} cache entries")
            return count
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return count


# Global cache service instance
cache_service = CacheService()
