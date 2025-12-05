"""
Cache Manager
Implement caching for AWS API responses to improve performance
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = '.cache'):
        """Initialize cache manager"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str, params: Dict = None) -> str:
        """Generate cache key from function name and parameters"""
        if params:
            param_str = json.dumps(params, sort_keys=True)
            hash_obj = hashlib.md5(param_str.encode())
            return f"{key}_{hash_obj.hexdigest()}"
        return key
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, key: str, params: Dict = None, max_age_minutes: int = 60) -> Optional[Any]:
        """Get cached data if it exists and is not expired"""
        cache_key = self._get_cache_key(key, params)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > timedelta(minutes=max_age_minutes):
                # Cache expired
                os.remove(cache_path)
                return None
            
            return cached_data['data']
            
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def set(self, key: str, data: Any, params: Dict = None):
        """Store data in cache"""
        cache_key = self._get_cache_key(key, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, default=str)
                
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def clear(self, key: Optional[str] = None):
        """Clear cache for specific key or all cache"""
        if key:
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            # Clear all cache
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not os.path.exists(self.cache_dir):
            return {'total_files': 0, 'total_size_mb': 0}
        
        total_files = 0
        total_size = 0
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                total_files += 1
                total_size += os.path.getsize(file_path)
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
