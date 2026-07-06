"""
Database service for Jungol Recommender.
Handles SQLite database operations for storing problems, solved problems, favorites, etc.
"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db_path: str = "jungol_recommender.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def _initialize_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                number INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                tier TEXT,
                tags TEXT,
                description TEXT,
                link TEXT UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solved_problems (
                problem_number INTEGER PRIMARY KEY,
                solved_date TEXT NOT NULL,
                memo TEXT,
                FOREIGN KEY (problem_number) REFERENCES problems (number)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                problem_number INTEGER PRIMARY KEY,
                added_date TEXT NOT NULL,
                FOREIGN KEY (problem_number) REFERENCES problems (number)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recent_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_number INTEGER NOT NULL,
                recommended_at TEXT NOT NULL,
                FOREIGN KEY (problem_number) REFERENCES problems (number)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_tier ON problems(tier)')
        conn.commit()
        logger.info("Database initialized.")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def store_problems(self, problems: List[Dict[str, Any]]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        for problem in problems:
            tags_json = json.dumps(problem.get('tags', []))
            cursor.execute('''
                INSERT OR REPLACE INTO problems (number, title, author, tier, tags, description, link)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                problem.get('number'),
                problem.get('title', ''),
                problem.get('author', ''),
                problem.get('tier', ''),
                tags_json,
                problem.get('description', ''),
                problem.get('link', '')
            ))
        conn.commit()
        logger.info(f"Stored {len(problems)} problems in the database.")

    def get_problems(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if limit:
            cursor.execute('SELECT number, title, author, tier, tags, description, link FROM problems LIMIT ?', (limit,))
        else:
            cursor.execute('SELECT number, title, author, tier, tags, description, link FROM problems')
        rows = cursor.fetchall()
        problems = []
        for row in rows:
            number, title, author, tier, tags_json, description, link = row
            try:
                tags = json.loads(tags_json) if tags_json else []
            except json.JSONDecodeError:
                tags = []
            problems.append({
                'number': number,
                'title': title,
                'author': author,
                'tier': tier,
                'tags': tags,
                'description': description,
                'link': link
            })
        return problems

    def get_problem_by_number(self, number: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT number, title, author, tier, tags, description, link FROM problems WHERE number = ?', (number,))
        row = cursor.fetchone()
        if row:
            number, title, author, tier, tags_json, description, link = row
            try:
                tags = json.loads(tags_json) if tags_json else []
            except json.JSONDecodeError:
                tags = []
            return {
                'number': number,
                'title': title,
                'author': author,
                'tier': tier,
                'tags': tags,
                'description': description,
                'link': link
            }
        return None

    def get_tags(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT tags FROM problems WHERE tags IS NOT NULL AND tags != ""')
        rows = cursor.fetchall()
        tags_set = set()
        for row in rows:
            tags_json = row[0]
            try:
                tags = json.loads(tags_json)
                tags_set.update(tags)
            except json.JSONDecodeError:
                pass
        return sorted(list(tags_set))

    def get_tiers(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT tier FROM problems WHERE tier IS NOT NULL AND tier != "" ORDER BY tier')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def mark_as_solved(self, problem_number: int, memo: str = "") -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        solved_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO solved_problems (problem_number, solved_date, memo)
            VALUES (?, ?, ?)
        ''', (problem_number, solved_date, memo))
        conn.commit()
        logger.info(f"Problem {problem_number} marked as solved.")

    def is_solved(self, problem_number: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM solved_problems WHERE problem_number = ?', (problem_number,))
        return cursor.fetchone() is not None

    def add_to_favorites(self, problem_number: int) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        added_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO favorites (problem_number, added_date)
            VALUES (?, ?)
        ''', (problem_number, added_date))
        conn.commit()
        logger.info(f"Problem {problem_number} added to favorites.")

    def remove_from_favorites(self, problem_number: int) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE problem_number = ?', (problem_number,))
        conn.commit()
        logger.info(f"Problem {problem_number} removed from favorites.")

    def is_favorite(self, problem_number: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM favorites WHERE problem_number = ?', (problem_number,))
        return cursor.fetchone() is not None

    def add_recent_recommendation(self, problem_number: int) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        recommended_at = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO recent_recommendations (problem_number, recommended_at)
            VALUES (?, ?)
        ''', (problem_number, recommended_at))
        conn.commit()

    def get_recent_recommendations(self, limit: int = 50) -> List[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT problem_number FROM recent_recommendations
            ORDER BY recommended_at DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_solved_problems(self) -> List[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT problem_number FROM solved_problems')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_favorites(self) -> List[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT problem_number FROM favorites')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def clear_recent_recommendations(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recent_recommendations')
        conn.commit()
