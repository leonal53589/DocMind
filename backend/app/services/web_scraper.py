"""Web scraper service for importing web pages."""

import re
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

# Try to import curl_cffi for better anti-bot bypass, fall back to httpx
try:
    from curl_cffi.requests import AsyncSession
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False
    import httpx


class WebScraper:
    """Service for scraping and importing web pages."""

    # Realistic browser headers to avoid being blocked
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    def __init__(self):
        self.client = None
        self._use_curl_cffi = HAS_CURL_CFFI

    async def _get_client(self):
        """Get or create the HTTP client."""
        if self.client is None:
            if self._use_curl_cffi:
                # Use curl_cffi with Chrome impersonation for better anti-bot bypass
                self.client = AsyncSession(impersonate="chrome120")
            else:
                # Fall back to httpx
                self.client = httpx.AsyncClient(
                    timeout=30.0,
                    follow_redirects=True,
                    headers=self.DEFAULT_HEADERS,
                )
        return self.client

    async def _fetch_url(self, url: str) -> tuple[str, str]:
        """
        Fetch URL content.

        Returns:
            Tuple of (html_content, final_url)
        """
        client = await self._get_client()

        if self._use_curl_cffi:
            # curl_cffi request
            response = await client.get(
                url,
                headers=self.DEFAULT_HEADERS,
                allow_redirects=True,
                timeout=30,
            )
            if response.status_code >= 400:
                raise Exception(f"HTTP {response.status_code}: {response.reason}")
            return response.text, str(response.url)
        else:
            # httpx request
            response = await client.get(url)
            response.raise_for_status()
            return response.text, str(response.url)

    async def scrape_url(self, url: str) -> dict:
        """
        Scrape a URL and extract content.

        Returns:
            Dictionary with:
            - title: page title
            - description: meta description
            - extracted_text: main content text
            - url: final URL (after redirects)
            - metadata: additional metadata
        """
        html_content, final_url = await self._fetch_url(url)

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title = self._extract_title(soup)
        if not title:
            title = urlparse(url).netloc

        # Extract description
        description = self._extract_description(soup)

        # Extract main content
        extracted_text = self._extract_content(soup)

        # Extract metadata
        metadata = {
            'original_url': url,
            'final_url': final_url,
            'domain': urlparse(final_url).netloc,
        }

        # Try to extract Open Graph data
        og_data = self._extract_og_data(soup)
        if og_data:
            metadata['og'] = og_data

        return {
            'title': title,
            'description': description,
            'extracted_text': extracted_text,
            'url': final_url,
            'metadata': metadata,
        }

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        # Try og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        # Try standard title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        # Try h1
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)

        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description."""
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        # Try standard meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text from the page."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header',
                           'aside', 'form', 'iframe', 'noscript']):
            element.decompose()

        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'content|main|post|article|RichText', re.I)) or
            soup.find('div', id=re.compile(r'content|main|post|article', re.I)) or
            soup.body
        )

        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)

    def _extract_og_data(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract Open Graph metadata."""
        og_data = {}

        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                og_data[prop] = content

        return og_data if og_data else None

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            if self._use_curl_cffi:
                await self.client.close()
            else:
                await self.client.aclose()
            self.client = None
