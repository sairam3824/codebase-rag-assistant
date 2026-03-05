"""Simple caching layer for embeddings and search results."""
import json
import hashlib
from pathlib import Path
from typing import Optional, List, Any
from datetime import datetime, timedelta


class SimpleCache:
    """File-based cache for embeddings and search results."""
    
    def __init__(self, cache_dir: str = "./.cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_key_hash(self, key: str) -> str:
        """Generate hash for cache key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        key_hash = self._get_key_hash(key)
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check TTL
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_path.unlink()  # Delete expired cache
                return None
            
            return data['value']
        except Exception:
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'value': value
            }
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass  # Silently fail on cache write errors
    
    def clear(self):
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception:
                pass
    
    def get_size(self) -> int:
        """Get total cache size in bytes."""
        total = 0
        for cache_file in self.cache_dir.glob("*.json"):
            total += cache_file.stat().st_size
        return total
