import json
import logging
import time
from typing import Optional, Any
import redis

logger = logging.getLogger(__name__)

class CacheService:
    """
    Redis Cache Service with an automated in-memory fallback
    for environments without an active Redis server.
    """
    _redis_checked = False
    _redis_available = False

    def __init__(self, redis_url: str = "redis://localhost:6379/0", default_ttl: int = 600):
        self.default_ttl = default_ttl
        self.redis_url = redis_url
        self.redis_client = None
        self._memory_cache = {}  # Fallback: {key: (data, expire_at)}
        self._init_redis()

    def _init_redis(self):
        if CacheService._redis_checked:
            if not CacheService._redis_available:
                self.redis_client = None
                return
        CacheService._redis_checked = True
        try:
            client = redis.from_url(
                self.redis_url, 
                decode_responses=True, 
                socket_timeout=0.3, 
                socket_connect_timeout=0.3
            )
            client.ping()
            self.redis_client = client
            CacheService._redis_available = True
            logger.info("Connected to Redis cache successfully.")
        except Exception as e:
            self.redis_client = None
            CacheService._redis_available = False
            logger.warning(f"Redis not available ({e}). Using in-memory fallback cache.")

    def _format_key(self, query: str) -> str:
        return f"blackhole:query:{query.strip().lower()}"

    def get(self, query: str) -> Optional[dict]:
        """Retrieves cached search results for the given query."""
        key = self._format_key(query)
        
        # Try Redis first if available
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    logger.debug(f"Redis cache HIT for '{query}'")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}. Falling back to memory.")

        # Fallback to in-memory cache
        if key in self._memory_cache:
            data, expire_at = self._memory_cache[key]
            if time.time() < expire_at:
                logger.debug(f"Memory cache HIT for '{query}'")
                return data
            else:
                del self._memory_cache[key]
                
        return None

    def set(self, query: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Stores search results in cache with TTL (seconds)."""
        key = self._format_key(query)
        ttl = ttl if ttl is not None else self.default_ttl
        
        saved = False
        # Try Redis first
        if self.redis_client:
            try:
                serialized = json.dumps(data)
                self.redis_client.setex(key, ttl, serialized)
                saved = True
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # Always maintain memory cache as mirror/fallback
        self._memory_cache[key] = (data, time.time() + ttl)
        return saved or True

    def clear(self):
        """Clears all cached queries."""
        if self.redis_client:
            try:
                keys = self.redis_client.keys("blackhole:query:*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")
        self._memory_cache.clear()

# Global cache instance
cache_service = CacheService()

def init_cache(app):
    """Initializes cache service with app config."""
    global cache_service
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
    ttl = app.config.get("CACHE_DEFAULT_TTL", 600)
    cache_service = CacheService(redis_url=redis_url, default_ttl=ttl)
    return cache_service
