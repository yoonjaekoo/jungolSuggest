"""
Crawler service for Jungol Recommender.
Coordinates crawling, caching, and database storage of problem data.
"""
import threading
import logging
from typing import List, Dict, Any, Optional
from crawler.jungol_crawler import JungolCrawler, MockJungolCrawler
from database.database import DatabaseService
from services.cache_service import CacheService

logger = logging.getLogger(__name__)

class CrawlerService:
    def __init__(self, use_mock: bool = False):
        """
        Initialize the crawler service.
        :param use_mock: Whether to use the mock crawler (for testing).
        """
        self.use_mock = use_mock
        self.crawler = MockJungolCrawler() if use_mock else JungolCrawler()
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        self._is_crawling = False
        self._lock = threading.Lock()

    def crawl_and_store(self) -> bool:
        """
        Perform the crawling process: check cache, crawl if needed, store in database.
        :return: True if crawling was performed, False if using cached data.
        """
        # Check if we have valid cache
        cached_data = self.cache_service.load_cache()
        if cached_data is not None:
            logger.info("Using cached data.")
            # Store cached data in database
            self.db_service.store_problems(cached_data)
            return False

        # Cache is invalid or empty, we need to crawl
        logger.info("Starting crawl...")
        self._is_crawling = True
        try:
            problems = self.crawler.crawl_all_problems()
            # Save to cache
            self.cache_service.save_cache(problems)
            # Store in database
            self.db_service.store_problems(problems)
            return True
        except Exception as e:
            logger.error(f"Crawling failed: {e}")
            # If crawling fails, we might still have old data in the database
            # We'll just log the error and return False
            return False
        finally:
            self._is_crawling = False

    def get_problems(self) -> List[Dict[str, Any]]:
        """Get all problems from the database."""
        return self.db_service.get_problems()

    def get_tags(self) -> List[str]:
        """Get all unique tags from the database."""
        return self.db_service.get_tags()

    def get_tiers(self) -> List[str]:
        """Get all unique tiers from the database."""
        return self.db_service.get_tiers()

    def fetch_all_problems(self) -> List[Dict[str, Any]]:
        try:
            problems = self.crawler.crawl_all_problems()
            self.db_service.store_problems(problems)
            return problems
        except Exception as e:
            logger.error(f"Failed to fetch problems: {e}")
            return []

    def is_crawling(self) -> bool:
        """Check if a crawl is currently in progress."""
        return self._is_crawling

    def close(self):
        """Close the database connection."""
        self.db_service.close()