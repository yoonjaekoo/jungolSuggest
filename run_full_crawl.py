import sys, asyncio, json, logging, time
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')

from crawler.jungol_crawler import JungolCrawler, tier_number_to_label
from services.cache_service import CacheService
from database.database import DatabaseService
import sqlite3

async def run():
    t0 = time.time()
    
    crawler = JungolCrawler(headless=True, delay=0.1)
    problems = await crawler.crawl_all_problems()
    
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
    for p in problems:
        if p.get("tier"): tiers.add(p["tier"])
        if p.get("author"): authors.add(p["author"])
    print(f"Unique tiers: {len(tiers)}")
    print(f"Unique sources: {len(authors)}")
    print(f"Tiers: {sorted(tiers)}")
    
    stored = db.get_problems(limit=5)
    print(f"\nSample from DB:")
    for s in stored:
        print(f"  #{s['number']} {s['title'][:30]} tier={s['tier']} author={s['author']}")
    
    # Count rows without loading all
    conn = sqlite3.connect("jungol_recommender.db")
    count = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    conn.close()
    print(f"\nTotal in DB: {count}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(run())
