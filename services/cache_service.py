"""
Cache service for Jungol Recommender.
Handles caching of crawled problem data to avoid repeated crawling.
"""
import json
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, cache_dir: str = "cache", cache_expiry: int = 86400):
        """
        Initialize the cache service.
        :param cache_dir: Directory to store cache files.
        :param cache_expiry: Cache expiry time in seconds (default 24 hours).
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_expiry = cache_expiry  # seconds
        self.cache_file = self.cache_dir / "problems_cache.json"

    def _is_cache_valid(self) -> bool:
        """
        Check if the cache file exists and is not expired.
        :return: True if cache is valid, False otherwise.
        """
        if not self.cache_file.exists():
            return False
        # Check file modification time
        file_mtime = self.cache_file.stat().st_mtime
        current_time = time.time()
        return (current_time - file_mtime) < self.cache_expiry

    def load_cache(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load problems from the cache.
        :return: List of problem dictionaries or None if cache is invalid or empty.
        """
        if not self._is_cache_valid():
            logger.info("Cache is invalid or expired.")
            return None
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} problems from cache.")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def save_cache(self, problems: List[Dict[str, Any]]) -> None:
        """
        Save problems to the cache.
        :param problems: List of problem dictionaries to cache.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(problems, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(problems)} problems to cache.")
        except IOError as e:
            logger.error(f"Failed to save cache: {e}")

    def clear_cache(self) -> None:
        """Clear the cache file."""
        if self.cache_file.exists():
            self.cache_file.unlink()
            logger.info("Cache cleared.")