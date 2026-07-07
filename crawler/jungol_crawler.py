import re
import json
import time
import logging
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TIER_LABELS = [
    "",
    "Bronze V", "Bronze IV", "Bronze III", "Bronze II", "Bronze I",
    "Silver V", "Silver IV", "Silver III", "Silver II", "Silver I",
    "Gold V", "Gold IV", "Gold III", "Gold II", "Gold I",
    "Platinum V", "Platinum IV", "Platinum III", "Platinum II", "Platinum I",
    "Diamond V", "Diamond IV", "Diamond III", "Diamond II", "Diamond I",
    "Ruby V", "Ruby IV", "Ruby III", "Ruby II", "Ruby I",
]


def tier_number_to_label(n: int) -> str:
    if 0 < n < len(TIER_LABELS):
        return TIER_LABELS[n]
    return ""


def _js_to_json(js_str: str) -> str:
    placeholders = {}

    def _protect(m):
        key = "##S%d##" % len(placeholders)
        placeholders[key] = m.group(0)
        return key

    # Protect string literals (both double and single-quoted)
    s = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', _protect, js_str)
    s = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", _protect, s)

    # Quote unquoted keys
    s = re.sub(r'(\{|\,)\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', s)
    # Remove trailing commas
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    # Fix leading-dot decimals  e.g. .55 -> 0.55
    s = re.sub(r'([,:\[])\s*\.(\d)', lambda m: m.group(1) + '0.' + m.group(2), s)
    s = re.sub(r'([,:\[])\s*\-\.(\d)', lambda m: m.group(1) + '-0.' + m.group(2), s)

    for key, val in placeholders.items():
        s = s.replace(key, val)
    return s


def _extract_page_data(html: str) -> tuple:
    """
    Extract the problem list and pagination info from the HTML.
    Returns (list_of_problems, total_pages) or ([], 0) on failure.
    """
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup.find_all('script'):
        text = script.string
        if not text:
            continue
        match = re.search(r'data:\s*(\[.+?\]),\s*form:', text, re.DOTALL)
        if not match:
            continue
        raw = match.group(1)
        try:
            converted = _js_to_json(raw)
            data = json.loads(converted)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse embedded data: {e}")
            continue
        if not isinstance(data, list) or len(data) < 3:
            continue
        # data[2].data["$/problem?page=N"].data.{list, paging}
        page_data = data[2]
        if not isinstance(page_data, dict):
            continue
        inner = page_data.get('data', {})
        if not isinstance(inner, dict):
            continue
        for key, val in inner.items():
            if isinstance(val, dict) and 'data' in val:
                problems = val['data'].get('list', [])
                paging = val['data'].get('paging', {})
                return problems, paging.get('pages', 0)
    return [], 0


def _parse_problems(raw_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    problems = []
    for item in raw_list:
        pid = item.get('id')
        if not pid:
            continue

        tier_obj = item.get('tier') or {}
        f_tier = item.get('fTier')
        tier_num = f_tier if f_tier is not None else (tier_obj.get('tier', 0) if isinstance(tier_obj, dict) else 0)
        tier_label = tier_number_to_label(tier_num)

        tags = list(item.get('tag') or [])
        for key, val in item.items():
            if key.startswith('t:') and val == '1':
                tags.append(key[2:])

        rank = item.get('rank') or {}
        if isinstance(rank, dict) and 'solvedSub' in rank:
            solved = rank.get('solvedSub', 0)
            total_sub = rank.get('totalSub', 0)
        else:
            solved = item.get('solved', 0)
            total_sub = item.get('totalSub', 0)
        link = f"https://jungol.co.kr/problem/{pid}"

        problems.append({
            'number': pid,
            'title': item.get('title', ''),
            'author': item.get('from', ''),
            'tier': tier_label,
            'tags': tags,
            'description': '',
            'link': link,
            'solved': str(solved),
            'attempted': str(total_sub),
        })
    return problems


class JungolCrawler:
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.base_url = "https://jungol.co.kr"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        self.problems: List[Dict[str, Any]] = []

    def _fetch_page(self, page_num: int) -> str:
        url = f"{self.base_url}/problem?page={page_num}"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return resp.text

    def crawl_all_problems(self) -> List[Dict[str, Any]]:
        logger.info("Fetching page 1 to determine total pages...")
        html = self._fetch_page(1)
        raw_list, total_pages = _extract_page_data(html)
        if not raw_list:
            logger.error("Failed to extract problems from page 1")
            return []

        logger.info(f"Total pages to crawl: {total_pages}")

        all_problems = _parse_problems(raw_list)
        logger.info(f"Page 1: {len(all_problems)} problems")

        for page_num in range(2, total_pages + 1):
            logger.info(f"Crawling page {page_num}/{total_pages}")
            time.sleep(self.delay)
            try:
                html = self._fetch_page(page_num)
                raw_list, _ = _extract_page_data(html)
                if not raw_list:
                    logger.warning(f"No data on page {page_num}")
                    continue
                problems = _parse_problems(raw_list)
                all_problems.extend(problems)
                logger.info(f"Page {page_num}: {len(problems)} problems (total: {len(all_problems)})")
            except Exception as e:
                logger.error(f"Failed to crawl page {page_num}: {e}")

        self.problems = all_problems
        logger.info(f"Crawling completed. Total problems: {len(self.problems)}")
        return self.problems

    def get_problems(self) -> List[Dict[str, Any]]:
        return self.problems


class MockJungolCrawler(JungolCrawler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problems = [
            {
                'number': 1000,
                'title': '두 정수 더하기 (A+B)',
                'author': 'JUNGOL',
                'tier': 'Bronze V',
                'tags': ['arithmetic', '구현', 'math', 'implement', 'ad_hoc', 'precomputation'],
                'description': '',
                'link': 'https://jungol.co.kr/problem/1000'
            },
            {
                'number': 1001,
                'title': '강아지와 병아리',
                'author': 'JUNGOL',
                'tier': 'Bronze II',
                'tags': ['arithmetic', 'math', 'case_work'],
                'description': '',
                'link': 'https://jungol.co.kr/problem/1001'
            },
            {
                'number': 1002,
                'title': '최대공약수, 최소공배수',
                'author': 'JUNGOL',
                'tier': 'Bronze III',
                'tags': ['euclidean', 'number_theory', 'math'],
                'description': '',
                'link': 'https://jungol.co.kr/problem/1002'
            }
        ]

    def crawl_all_problems(self) -> List[Dict[str, Any]]:
        logger.info("Using mock crawler")
        return self.problems
