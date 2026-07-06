import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

TIER_LABELS = [
    "",
    "Bronze V", "Bronze IV", "Bronze III", "Bronze II", "Bronze I",
    "Silver V", "Silver IV", "Silver III", "Silver II", "Silver I",
    "Gold V", "Gold IV", "Gold III", "Gold II", "Gold I",
    "Platinum V", "Platinum IV", "Platinum III", "Platinum II", "Platinum I",
    "Diamond V", "Diamond IV", "Diamond III", "Diamond II", "Diamond I",
    "Ruby V", "Ruby IV", "Ruby III", "Ruby II", "Ruby I",
]


def tier_number_to_label(n: str) -> str:
    try:
        idx = int(n)
        return TIER_LABELS[idx] if 0 < idx < len(TIER_LABELS) else f"Tier {n}"
    except (ValueError, IndexError):
        return ""


JS_EXTRACT = """(baseUrl) => {
    const rows = document.querySelectorAll('table.S-1bbneo1 tbody tr');
    const result = [];
    for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length < 6) continue;
        const numberText = cells[0].innerText.trim();
        const numMatch = numberText.match(/(\\d+)/);
        if (!numMatch) continue;
        const problemNumber = parseInt(numMatch[1], 10);
        const title = cells[1].innerText.trim().replace(/translate$/, '').trim();
        const img = cells[0].querySelector('img[src*="solved"]');
        let tierNumber = '';
        if (img) {
            const src = img.getAttribute('src') || '';
            const m = src.match(/solved\\/(\\d+)\\.svg/);
            if (m) tierNumber = m[1];
        }
        result.push({
            number: problemNumber,
            title: title,
            author: cells[2].innerText.trim(),
            tier: tierNumber,
            tags: [],
            description: '',
            solved: cells[3].innerText.trim(),
            attempted: cells[4].innerText.trim(),
            accuracy: cells[5].innerText.trim(),
            link: baseUrl + '/problem/' + problemNumber,
        });
    }
    return result;
}"""


class JungolCrawler:
    def __init__(self, headless: bool = True, delay: float = 0.2):
        self.headless = headless
        self.delay = delay
        self.base_url = "https://jungol.co.kr"
        self.problems: List[Dict[str, Any]] = []

    async def _get_total_pages(self, page) -> int:
        await page.goto(f"{self.base_url}/problem", wait_until="networkidle", timeout=30000)
        await page.wait_for_function(
            "document.querySelectorAll('table.S-1bbneo1 tbody tr').length >= 1",
            timeout=15000
        )
        await page.wait_for_timeout(300)
        total = await page.evaluate("""() => {
            const links = document.querySelectorAll('a');
            let maxPage = 0;
            for (const a of links) {
                const href = a.getAttribute('href') || '';
                const m = href.match(/^\\?page=(\\d+)$/);
                if (m) {
                    const p = parseInt(m[1], 10);
                    if (p > maxPage) maxPage = p;
                }
            }
            return maxPage;
        }""")
        return max(total, 1)

    async def _crawl_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        if page_num == 1:
            await page.goto(f"{self.base_url}/problem", wait_until="networkidle", timeout=30000)
            await page.wait_for_function(
                "document.querySelectorAll('table.S-1bbneo1 tbody tr').length >= 1",
                timeout=15000
            )
            await page.wait_for_timeout(500)
        else:
            old_first = await page.evaluate("""() => {
                const td = document.querySelector('table.S-1bbneo1 tbody tr td');
                if (!td) return 0;
                const m = td.innerText.trim().match(/(\\d+)/);
                return m ? parseInt(m[1]) : 0;
            }""")

            await page.click(f'a[href="?page={page_num}"]')

            try:
                await page.wait_for_function(
                    f"""() => {{
                        const td = document.querySelector('table.S-1bbneo1 tbody tr td');
                        if (!td) return false;
                        const m = td.innerText.trim().match(/(\\d+)/);
                        if (!m) return false;
                        return parseInt(m[1]) !== {old_first};
                    }}""",
                    timeout=15000
                )
            except Exception:
                pass

            await page.wait_for_timeout(200)

        problems = await page.evaluate(JS_EXTRACT, self.base_url)
        return problems

    async def crawl_all_problems(self) -> List[Dict[str, Any]]:
        if not HAS_PLAYWRIGHT:
            raise ImportError(
                "Playwright is required for the real crawler. "
                "Install it with: pip install playwright && playwright install chromium"
            )

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            page = await context.new_page()

            try:
                total_pages = await self._get_total_pages(page)
                logger.info(f"Total pages to crawl: {total_pages}")

                all_problems = []
                for page_num in range(1, total_pages + 1):
                    logger.info(f"Crawling page {page_num}/{total_pages}")
                    problems = await self._crawl_page(page, page_num)
                    all_problems.extend(problems)
                    logger.info(f"Page {page_num}: {len(problems)} problems (total: {len(all_problems)})")

                    if self.delay and page_num < total_pages:
                        await asyncio.sleep(self.delay)

                self.problems = all_problems
                logger.info(f"Crawling completed. Total problems: {len(self.problems)}")

                for problem in self.problems:
                    if problem.get("tier"):
                        problem["tier"] = tier_number_to_label(problem["tier"])

                return self.problems

            finally:
                await browser.close()

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
                'tags': [],
                'description': '',
                'link': 'https://jungol.co.kr/problem/1000'
            },
            {
                'number': 1001,
                'title': '강아지와 병아리',
                'author': 'JUNGOL',
                'tier': 'Bronze II',
                'tags': [],
                'description': '',
                'link': 'https://jungol.co.kr/problem/1001'
            },
            {
                'number': 1002,
                'title': '최대공약수, 최소공배수',
                'author': 'JUNGOL',
                'tier': 'Bronze III',
                'tags': [],
                'description': '',
                'link': 'https://jungol.co.kr/problem/1002'
            }
        ]

    async def crawl_all_problems(self) -> List[Dict[str, Any]]:
        logger.info("Using mock crawler")
        return self.problems
