"""
Czech Business Registry Scraper
Scrapes business data from rejstrik-firem.kurzy.cz
"""
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote
import logging
from tqdm import tqdm

from utils.validators import validate_ico, clean_business_name


class RegistryScraper:
    """Scraper for Czech business registry (rejstrik-firem.kurzy.cz)"""

    BASE_URL = "https://rejstrik-firem.kurzy.cz"
    SEARCH_URL = f"{BASE_URL}/hledani/"

    def __init__(self, delay: int = 2, timeout: int = 30, retry_attempts: int = 3, logger: logging.Logger = None):
        """
        Initialize registry scraper

        Args:
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            logger: Logger instance
        """
        self.delay = delay
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.logger = logger or logging.getLogger(__name__)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'cs,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def search_registry(self, keywords: List[str], location: str, max_results: int = 500) -> List[Dict]:
        """
        Search business registry for businesses matching keywords and location

        Args:
            keywords: List of search keywords
            location: City/location name
            max_results: Maximum number of results to return

        Returns:
            List of business dictionaries
        """
        all_businesses = []
        seen_icos = set()

        self.logger.info(f"Searching registry for: {', '.join(keywords)} in {location}")

        for keyword in keywords:
            if len(all_businesses) >= max_results:
                break

            # Search for keyword + location
            search_query = f"{keyword} {location}"
            businesses = self._search_query(search_query, max_results - len(all_businesses))

            # Deduplicate by IČO
            for business in businesses:
                ico = business.get('ico', '')
                if ico and ico not in seen_icos:
                    seen_icos.add(ico)
                    all_businesses.append(business)
                elif not ico:
                    # Include businesses without IČO
                    all_businesses.append(business)

            self.logger.info(f"Found {len(businesses)} businesses for '{keyword}'")
            time.sleep(self.delay)

        self.logger.info(f"Total businesses found: {len(all_businesses)}")
        return all_businesses[:max_results]

    def _search_query(self, query: str, max_results: int) -> List[Dict]:
        """
        Perform a single search query

        Args:
            query: Search query string
            max_results: Maximum results to fetch

        Returns:
            List of business dictionaries
        """
        businesses = []
        encoded_query = quote(query)
        search_url = f"{self.SEARCH_URL}{encoded_query}/"

        try:
            page = 1
            while len(businesses) < max_results:
                # Build page URL
                if page > 1:
                    url = f"{search_url}?page={page}"
                else:
                    url = search_url

                # Fetch page with retry
                html = self._fetch_with_retry(url)
                if not html:
                    break

                # Parse results
                page_businesses = self._parse_search_results(html)
                if not page_businesses:
                    break

                businesses.extend(page_businesses)

                # Check if there are more pages
                soup = BeautifulSoup(html, 'lxml')
                if not self._has_next_page(soup):
                    break

                page += 1
                time.sleep(self.delay)

        except Exception as e:
            self.logger.error(f"Error searching query '{query}': {e}")

        return businesses[:max_results]

    def _parse_search_results(self, html: str) -> List[Dict]:
        """
        Parse search results page

        Args:
            html: Page HTML

        Returns:
            List of business dictionaries
        """
        businesses = []

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all business listings
            # The structure may vary, so we try multiple selectors
            listings = soup.find_all('div', class_='company-item') or \
                      soup.find_all('div', class_='item') or \
                      soup.find_all('article')

            for listing in listings:
                try:
                    business = self._extract_business_data(listing)
                    if business:
                        businesses.append(business)
                except Exception as e:
                    self.logger.debug(f"Error parsing listing: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing search results: {e}")

        return businesses

    def _extract_business_data(self, listing) -> Optional[Dict]:
        """
        Extract business data from a listing element

        Args:
            listing: BeautifulSoup element containing business listing

        Returns:
            Business dictionary or None if extraction fails
        """
        try:
            # Extract business name
            name_elem = listing.find('h2') or listing.find('h3') or listing.find('a', class_='title')
            if not name_elem:
                return None

            business_name = name_elem.get_text(strip=True)
            business_name = clean_business_name(business_name)

            # Extract IČO
            ico = ""
            ico_elem = listing.find(string=lambda text: text and 'IČO' in text)
            if ico_elem:
                ico_text = ico_elem.get_text() if hasattr(ico_elem, 'get_text') else str(ico_elem)
                ico_match = ico_text.split('IČO')[-1].strip().split()[0] if 'IČO' in ico_text else ""
                ico = ''.join(filter(str.isdigit, ico_match))[:8]

            # Extract address
            address = ""
            city = ""
            postal_code = ""

            address_elem = listing.find('div', class_='address') or \
                          listing.find('p', class_='address') or \
                          listing.find(string=lambda text: text and any(c in str(text) for c in ['Praha', 'Brno', 'Ostrava']))

            if address_elem:
                address_text = address_elem.get_text(strip=True) if hasattr(address_elem, 'get_text') else str(address_elem)
                address = address_text

                # Try to extract city and postal code
                import re
                # Czech postal codes: XXX XX
                postal_match = re.search(r'\b\d{3}\s?\d{2}\b', address_text)
                if postal_match:
                    postal_code = postal_match.group(0)

                # Extract city (word before or after postal code, or common city names)
                cities = ['Praha', 'Brno', 'Ostrava', 'Plzeň', 'Liberec', 'Olomouc', 'České Budějovice', 'Hradec Králové', 'Ústí nad Labem', 'Pardubice']
                for city_name in cities:
                    if city_name in address_text:
                        city = city_name
                        break

            # Extract business activities
            activities = []
            activity_elem = listing.find('div', class_='activities') or \
                           listing.find('p', class_='category')
            if activity_elem:
                activities_text = activity_elem.get_text(strip=True)
                activities = [act.strip() for act in activities_text.split(',')]

            return {
                'business_name': business_name,
                'ico': ico if validate_ico(ico) else "",
                'address': address,
                'city': city,
                'postal_code': postal_code,
                'business_activities': activities,
                'source': 'registry',
                'phone': '',
                'email': '',
                'website': '',
                'instagram': '',
                'facebook': '',
                'google_rating': None,
                'notes': ''
            }

        except Exception as e:
            self.logger.debug(f"Error extracting business data: {e}")
            return None

    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """
        Check if there are more pages of results

        Args:
            soup: BeautifulSoup object of current page

        Returns:
            True if next page exists, False otherwise
        """
        # Look for pagination elements
        next_link = soup.find('a', string=lambda text: text and ('další' in text.lower() or 'next' in text.lower()))
        return next_link is not None

    def _fetch_with_retry(self, url: str) -> Optional[str]:
        """
        Fetch URL with retry logic

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if all retries failed
        """
        for attempt in range(self.retry_attempts):
            try:
                self.logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.retry_attempts})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text

            except requests.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.delay * (attempt + 1))  # Exponential backoff
                continue

        self.logger.error(f"Failed to fetch {url} after {self.retry_attempts} attempts")
        return None

    def close(self):
        """Close the session"""
        self.session.close()
