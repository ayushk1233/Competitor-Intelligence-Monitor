import httpx
import asyncio
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from backend.config import get_settings
from backend.models.schemas import PageData, CompetitorPages
from backend.utils.cleaner import clean_html

import time
from backend.metrics import (
    scrape_requests_total,
    scrape_success_total,
    scrape_failure_total,
    scrape_duration,
)

settings = get_settings()

# Pages we want to find per competitor, in priority order
TARGET_PATHS = {
    "pricing":  ["/pricing", "/plans", "/price"],
    "about":    ["/about", "/about-us", "/company"],
    "blog":     ["/blog", "/news", "/updates", "/changelog"],
    "careers":  ["/careers", "/jobs", "/join-us", "/hiring"],
}


class ScraperService:

    def __init__(self):
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.request_timeout_seconds,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
        )

    async def close(self):
        await self.client.aclose()

    

    async def fetch_competitor(self, identifier: str) -> CompetitorPages:
        """
        Main method. Takes a name or URL, returns all fetched pages.
        """
        domain = await self._resolve_domain(identifier)
        name = self._extract_name(identifier, domain)

        print(f"  [scraper] Starting {name} → {domain}")

        # ✅ FIX: pass domain as third argument so metrics can label by domain
        homepage_data = await self._fetch_page(f"https://{domain}", "homepage", domain)

        # Discover and fetch sub-pages concurrently
        sub_urls = await self._discover_pages(domain, homepage_data.content)
        sub_tasks = [
            # ✅ FIX: pass domain here too
            self._fetch_page(url, page_type, domain)
            for page_type, url in sub_urls.items()
        ]
        
        sub_results = await asyncio.gather(*sub_tasks, return_exceptions=True)

        # Collect successful fetches
        pages = [homepage_data]
        errors = []

        for result in sub_results:
            if isinstance(result, Exception):
                errors.append(str(result))
            elif result.fetch_success:
                pages.append(result)

        print(f"  [scraper] {name}: {len(pages)} pages fetched, {len(errors)} errors")

        return CompetitorPages(
            name=name,
            domain=domain,
            pages=pages,
            fetch_errors=errors
        )

    

    async def _resolve_domain(self, identifier: str) -> str:
        """
        If given a URL → strip to domain.
        If given a name → try common TLDs and return first that responds.
        """
        # Looks like a URL already
        if "." in identifier and (
            identifier.startswith("http") or "/" not in identifier
        ):
            parsed = urlparse(
                identifier if identifier.startswith("http")
                else f"https://{identifier}"
            )
            return parsed.netloc.replace("www.", "")

        # It's a company name — try common TLDs
        name_clean = identifier.lower().replace(" ", "")
        candidates = [
            f"{name_clean}.com",
            f"{name_clean}.io",
            f"{name_clean}.co",
            f"{name_clean}.ai",
        ]

        for candidate in candidates:
            try:
                response = await self.client.head(
                    f"https://{candidate}", timeout=5
                )
                if response.status_code < 400:
                    print(f"  [scraper] Resolved '{identifier}' → {candidate}")
                    return candidate
            except Exception:
                continue

        # Fall back to .com even if unreachable
        fallback = f"{name_clean}.com"
        print(f"  [scraper] Could not verify '{identifier}', falling back to {fallback}")
        return fallback

    

    async def _discover_pages(
        self, domain: str, homepage_content: str
    ) -> dict[str, str]:
        """
        Try to find pricing, about, blog, careers pages.
        First scan the homepage HTML for matching hrefs.
        Fall back to trying known common paths directly.
        """
        found: dict[str, str] = {}
        base_url = f"https://{domain}"

        try:
            raw_response = await self.client.get(base_url)
            soup = BeautifulSoup(raw_response.text, "lxml")
            all_links = [
                a.get("href", "") for a in soup.find_all("a", href=True)
            ]
        except Exception:
            all_links = []

        for page_type, paths in TARGET_PATHS.items():
            # Check if already have enough pages
            if len(found) >= settings.max_pages_per_competitor - 1:
                break

            # Try to find in scraped links first
            match = self._find_in_links(all_links, paths, base_url)
            if match:
                found[page_type] = match
                continue

            # Fall back: try each path directly
            for path in paths:
                url = f"{base_url}{path}"
                try:
                    resp = await self.client.head(url, timeout=5)
                    if resp.status_code < 400:
                        found[page_type] = url
                        break
                except Exception:
                    continue

        return found

    def _find_in_links(
        self, links: list[str], target_paths: list[str], base_url: str
    ) -> str | None:
        """Scan a list of hrefs for any that contain a target path keyword."""
        for link in links:
            for path in target_paths:
                keyword = path.strip("/")
                if keyword in link.lower():
                    # Make absolute URL if relative
                    if link.startswith("http"):
                        return link
                    return urljoin(base_url, link)
        return None

    

    async def _fetch_page(
        self, url: str, page_type: str, domain: str
    ) -> PageData:
        """Fetch a single page — tries Jina first, falls back to BS4."""
        start = time.time()

        # ── Try Jina AI Reader ────────────────────────────────────────────
        scrape_requests_total.labels(
            domain=domain, page_type=page_type, method="jina"
        ).inc()

        try:
            jina_url = f"https://r.jina.ai/{url}"
            response = await self.client.get(jina_url, timeout=15)
            response.raise_for_status()
            content = clean_html(response.text)

            if content and len(content) > 100:
                duration = time.time() - start
                scrape_success_total.labels(
                    domain=domain, page_type=page_type
                ).inc()
                scrape_duration.labels(page_type=page_type).observe(duration)

                return PageData(
                    url=url,
                    page_type=page_type,
                    content=content,
                    fetch_success=True
                )
            raise ValueError("Jina returned empty content")

        except Exception as e:
            print(f"  [scraper] Jina failed for {url}: {e}")

        # ── Fallback: BeautifulSoup ───────────────────────────────────────
        scrape_requests_total.labels(
            domain=domain, page_type=page_type, method="beautifulsoup"
        ).inc()

        try:
            response = await self.client.get(url, timeout=15)
            response.raise_for_status()
            content = clean_html(response.text)
            duration = time.time() - start

            if content and len(content) > 100:
                scrape_success_total.labels(
                    domain=domain, page_type=page_type
                ).inc()
                scrape_duration.labels(page_type=page_type).observe(duration)

                return PageData(
                    url=url,
                    page_type=page_type,
                    content=content,
                    fetch_success=True
                )

        except Exception as e:
            duration = time.time() - start
            error_str = str(e)

            # Classify failure reason for the metric label
            if "timeout" in error_str.lower():
                reason = "timeout"
            elif "ssl" in error_str.lower() or "certificate" in error_str.lower():
                reason = "ssl"
            elif "404" in error_str or "403" in error_str:
                reason = "http_error"
            else:
                reason = "unknown"

            scrape_failure_total.labels(
                domain=domain, reason=reason
            ).inc()
            scrape_duration.labels(page_type=page_type).observe(duration)

            print(f"  [scraper] Raw fetch failed for {url}: {e}")

        return PageData(
            url=url,
            page_type=page_type,
            content="",
            fetch_success=False
        )

    async def _fetch_via_jina(self, url: str) -> str | None:
        """
        Use Jina AI reader (r.jina.ai) to get clean markdown from any URL.
        Returns None on failure so caller can fall back.
        """
        try:
            headers = {}
            if settings.jina_api_key:
                headers["Authorization"] = f"Bearer {settings.jina_api_key}"

            response = await self.client.get(
                f"https://r.jina.ai/{url}",
                headers=headers,
                timeout=15
            )
            if response.status_code == 200 and len(response.text) > 100:
                return response.text
        except Exception as e:
            print(f"  [scraper] Jina failed for {url}: {e}")
        return None

    async def _fetch_raw_and_clean(self, url: str) -> str | None:
        """
        Fetch raw HTML and clean with BeautifulSoup.
        Used as fallback when Jina is unavailable.
        """
        try:
            response = await self.client.get(url, timeout=10)
            if response.status_code == 200:
                return clean_html(response.text)
        except Exception as e:
            print(f"  [scraper] Raw fetch failed for {url}: {e}")
        return None

    

    def _extract_name(self, identifier: str, domain: str) -> str:
        """
        Get a clean display name.
        'hubspot.com' → 'HubSpot' (best effort, capitalize domain root)
        """
        if "." not in identifier:
            return identifier.title()
        root = domain.split(".")[0]
        return root.capitalize()
