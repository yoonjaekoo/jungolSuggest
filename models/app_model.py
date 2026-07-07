"""
Application Model for Jungol Recommender.
Handles data loading, crawling, database interactions, and caching.
"""

import threading
import time
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from services.crawler_service import CrawlerService
from services.cache_service import CacheService
from database.database import DatabaseService

class AppModel:
    def __init__(self):
        """
        Initialize the application model.
        Sets up services and starts background threads for data loading.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Placeholder for services
        self.crawler_service = None
        self.database_service = None
        self.cache_service = None

        # Data state
        self.problems: List[Dict[str, Any]] = []  # List of problem dictionaries
        self.tags: List[str] = []  # Unique tags
        self.tiers: List[str] = []  # Unique tiers (difficulty levels)

        # UI state (shared with view/controller)
        self.selected_tags: List[str] = []
        self.selected_min_tier: str = ""
        self.selected_max_tier: str = ""
        self.recommendation_mode: str = "random"  # random, sequential, easy, hard, etc.
        self.exclude_solved: bool = True
        self.exclude_favorites: bool = False
        self.exclude_recent: bool = True
        self.exclude_untiered: bool = True
        self.recent_recommendations: List[int] = []  # Stores problem numbers

        # Solved/favorites sets loaded from DB
        self.solved_set: set = set()
        self.favorites_set: set = set()

        # Threading control
        self._loading_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._data_loaded_callbacks: list = []

        # Initialize services (we'll create them later)
        self._initialize_services()

    def _initialize_services(self):
        self.cache_service = CacheService()
        self.database_service = DatabaseService()
        self.crawler_service = CrawlerService(use_mock=False)

    def on_data_loaded(self, callback):
        self._data_loaded_callbacks.append(callback)

    def _fire_data_loaded(self):
        for cb in self._data_loaded_callbacks:
            try:
                cb()
            except Exception as e:
                self.logger.error(f"Data loaded callback error: {e}")

    def start_background_tasks(self):
        """Start background threads for data loading and crawling."""
        if self._loading_thread is None or not self._loading_thread.is_alive():
            self._stop_event.clear()
            self._loading_thread = threading.Thread(target=self._background_loader, daemon=True)
            self._loading_thread.start()
            self.logger.info("Background data loading started.")

    def stop_background_tasks(self):
        """Stop background threads."""
        self._stop_event.set()
        if self._loading_thread and self._loading_thread.is_alive():
            self._loading_thread.join(timeout=5.0)
        if self.database_service:
            self.database_service.close()
        self.logger.info("Background tasks stopped.")

    def _background_loader(self):
        """
        Background task to load or update problem data.
        Checks cache, crawls if necessary, and updates the model.
        """
        try:
            self.logger.info("Starting background data loader...")
            data = None
            if self.cache_service:
                data = self.cache_service.load_cache()
            if data:
                self.logger.info("Data loaded from cache.")
                self._update_model_from_data(data)
            else:
                self.logger.info("Cache invalid or missing. Starting crawl...")
                if self.crawler_service:
                    crawled_data = self.crawler_service.fetch_all_problems()
                    if crawled_data:
                        if self.cache_service:
                            self.cache_service.save_cache(crawled_data)
                        self._update_model_from_data(crawled_data)
                        self.logger.info("Crawl completed and data cached.")
                    else:
                        self.logger.error("Crawl returned no data.")
                else:
                    self.logger.error("Crawler service not initialized.")

            self.load_solved_problems()
            self.load_favorites()

        except Exception as e:
            self.logger.exception(f"Error in background loader: {e}")

    def _update_model_from_data(self, data: List[Dict[str, Any]]):
        """
        Update the model's internal data from crawled data.
        :param data: List of problem dictionaries.
        """
        self.problems = data
        # Extract unique tags and tiers
        tags_set = set()
        tiers_set = set()
        for problem in data:
            if 'tags' in problem and isinstance(problem['tags'], list):
                tags_set.update(problem['tags'])
            tier = problem.get('tier') or ''
            if tier and not tier.startswith('Tier '):
                tiers_set.add(tier)
        self.tags = sorted(list(tags_set))
        self.tiers = sorted(list(tiers_set), key=self._tier_sort_key)
        self.logger.info(f"Model updated with {len(self.problems)} problems, {len(self.tags)} tags, {len(self.tiers)} tiers.")
        self._fire_data_loaded()

    def _tier_sort_key(self, tier: str) -> tuple:
        metal_order = {"Bronze": 0, "Silver": 1, "Gold": 2, "Platinum": 3, "Diamond": 4, "Ruby": 5}
        roman_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
        parts = tier.split()
        if len(parts) != 2:
            return (0, 0)
        metal, level_str = parts
        metal_val = metal_order.get(metal, -1)
        level = roman_to_int.get(level_str, 0)
        return (metal_val, level)

    # Getter methods for the view/controller
    def get_problems(self) -> List[Dict[str, Any]]:
        return self.problems

    def get_tags(self) -> List[str]:
        return self.tags

    def get_tiers(self) -> List[str]:
        return self.tiers

    # Methods to update UI state (called by controller)
    def set_selected_tags(self, tags: List[str]):
        self.selected_tags = tags

    def set_selected_tier_range(self, min_tier: str, max_tier: str):
        self.selected_min_tier = min_tier
        self.selected_max_tier = max_tier

    # ... more state setters as needed

    # Method to get filtered problems based on current state
    def get_filtered_problems(self) -> List[Dict[str, Any]]:
        """
        Return problems that match the current filters (tags, tier range, etc.)
        """
        filtered = self.problems
        # Filter by tags
        if self.selected_tags:
            # Depending on mode: all tags must be present or at least one
            # We'll assume the controller sets a flag for match mode.
            # For now, we'll require all selected tags to be present (AND mode).
            filtered = [p for p in filtered if
                        'tags' in p and
                        all(tag in p['tags'] for tag in self.selected_tags)]
        # Filter by tier range
        if self.selected_min_tier and self.selected_max_tier:
            min_key = self._tier_sort_key(self.selected_min_tier)
            max_key = self._tier_sort_key(self.selected_max_tier)
            filtered = [p for p in filtered
                        if 'tier' in p and p['tier']
                        and min_key <= self._tier_sort_key(p['tier']) <= max_key]
        if self.exclude_solved:
            filtered = [p for p in filtered if p.get('number') not in self.solved_set]
        if self.exclude_favorites:
            filtered = [p for p in filtered if p.get('number') not in self.favorites_set]
        if self.exclude_untiered:
            filtered = [p for p in filtered if p.get('tier')]
        # Exclude recently recommended (if enabled)
        if self.exclude_recent:
            filtered = [p for p in filtered if p.get('number') not in self.recent_recommendations]
        return filtered

    # Method to get a recommendation based on mode
    def get_recommendation(self) -> Optional[Dict[str, Any]]:
        """
        Return a single problem recommendation based on the current mode and filters.
        """
        filtered = self.get_filtered_problems()
        if not filtered:
            return None

        import random
        if self.recommendation_mode == "random":
            return random.choice(filtered)
        elif self.recommendation_mode == "sequential":
            # We'll need to remember the last recommended index; for simplicity, we'll just return the first
            # In a real app, we'd store the last index and increment.
            return filtered[0] if filtered else None
        elif self.recommendation_mode == "easy":
            # Sort by tier (easiest first) and then pick the first
            sorted_by_tier = sorted(filtered, key=lambda p: self._tier_sort_key(p.get('tier', '')))
            return sorted_by_tier[0] if sorted_by_tier else None
        elif self.recommendation_mode == "hard":
            sorted_by_tier = sorted(filtered, key=lambda p: self._tier_sort_key(p.get('tier', '')), reverse=True)
            return sorted_by_tier[0] if sorted_by_tier else None
        else:
            # Default to random
            return random.choice(filtered)

    # Methods to mark problems as solved, favorite, etc.
    def mark_as_solved(self, problem_number: int, memo: str = ""):
        """
        Mark a problem as solved and store in database.
        """
        if self.database_service:
            self.database_service.add_solved_problem(problem_number, memo=memo)
        # Also update recent recommendations if needed
        self.add_to_recent_recommendations(problem_number)

    def add_to_favorites(self, problem_number: int):
        if self.database_service:
            self.database_service.add_favorite(problem_number)

    def remove_from_favorites(self, problem_number: int):
        if self.database_service:
            self.database_service.remove_favorite(problem_number)

    def add_to_recent_recommendations(self, problem_number: int):
        """Add a problem number to the recent recommendations list (with a limit)."""
        self.recent_recommendations.append(problem_number)
        # Keep only the last, say, 50 recommendations
        if len(self.recent_recommendations) > 50:
            self.recent_recommendations = self.recent_recommendations[-50:]

    @property
    def solved_count(self) -> int:
        if self.database_service:
            return len(self.database_service.get_solved_problems())
        return 0

    @property
    def favorite_count(self) -> int:
        if self.database_service:
            return len(self.database_service.get_favorites())
        return 0

    def load_solved_problems(self):
        if self.database_service:
            self.solved_set = set(self.database_service.get_solved_problems())

    def load_favorites(self):
        if self.database_service:
            self.favorites_set = set(self.database_service.get_favorites())

