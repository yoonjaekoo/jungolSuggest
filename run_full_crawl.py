import sys, json, logging, time
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')

from crawler.jungol_crawler import JungolCrawler
from services.cache_service import CacheService
from database.database import DatabaseService
import sqlite3

def main():
    t0 = time.time()

    crawler = JungolCrawler(delay=0.3)
    problems = crawler.crawl_all_problems()

    t1 = time.time()
    print(f"\n{'='*50}")
    print(f"Crawling completed in {t1-t0:.1f}s")
    print(f"Total problems: {len(problems)}")

    # Save to cache
    cache = CacheService()
    cache.save_cache(problems)

    # Save to DB
    db = DatabaseService()
    db.store_problems(problems)

    # Stats
    tiers = set()
    authors = set()
    tags = set()
    for p in problems:
        if p.get("tier"): tiers.add(p["tier"])
        if p.get("author"): authors.add(p["author"])
        for tag in p.get("tags", []):
            tags.add(tag)
    print(f"Unique tiers: {len(tiers)}")
    print(f"Unique sources: {len(authors)}")
    print(f"Unique tags: {len(tags)}")
    if tags:
        print(f"Sample tags: {sorted(tags)[:20]}")

    stored = db.get_problems(limit=5)
    print(f"\nSample from DB:")
    for s in stored:
        tags_str = ', '.join(s.get('tags', [])[:5])
        print(f"  #{s['number']} {s['title'][:30]} tier={s['tier']} tags=[{tags_str}]")

    # Count rows without loading all
    conn = sqlite3.connect("jungol_recommender.db")
    count = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    conn.close()
    print(f"\nTotal in DB: {count}")

    db.close()

if __name__ == "__main__":
    main()
