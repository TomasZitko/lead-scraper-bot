"""
Website Scraper - FIXED VERSION
Falls back gracefully when lxml not available
"""
import time
import re
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from utils.email_extractor import extract_emails_from_html, get_primary_email, extract_domain_from_url
from utils.validators import validate_url, normalize_url


class WebsiteScraper:
    """Scraper for individual business websites"""

    def __init__(self, timeout: int = 30, delay: int = 1, logger: logging.Logger = None):
        """
        Initialize website scraper

        Args:
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
            logger: Logger instance
        """
        self.timeout = timeout
        self.delay = delay
        self.logger = logger or logging.getLogger(__name__)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'cs,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Determine best parser
        self.parser = self._get_best_parser()

    def _get_best_parser(self) -> str:
        """Determine best available HTML parser"""
        try:
            import lxml
            return 'lxml'
        except ImportError:
            self.logger.debug("lxml not available, using html.parser")
            return 'html.parser'

    def scrape_website(self, url: str) -> Dict:
        """
        Scrape a business website for contact info and quality metrics

        Args:
            url: Website URL to scrape

        Returns:
            Dictionary with scraped data
        """
        if not url or not validate_url(url):
            return {}

        self.logger.debug(f"Scraping website: {url}")

        try:
            # Fetch website
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            html = response.text
            
            # Use best available parser with fallback
            try:
                soup = BeautifulSoup(html, self.parser)
            except Exception as e:
                self.logger.debug(f"Parser {self.parser} failed, falling back to html.parser")
                soup = BeautifulSoup(html, 'html.parser')

            # Extract data
            data = {
                'email': '',
                'instagram': '',
                'facebook': '',
                'website_quality_score': 0,
                'has_https': url.startswith('https://'),
                'is_mobile_responsive': False,
                'last_updated': None,
            }

            # Extract emails
            emails = extract_emails_from_html(html)
            domain = extract_domain_from_url(url)
            if emails:
                data['email'] = get_primary_email(emails, domain)

            # Extract social media links
            social_links = self._find_social_links(soup, url)
            data['instagram'] = social_links.get('instagram', '')
            data['facebook'] = social_links.get('facebook', '')

            # Analyze website quality
            quality_metrics = self._analyze_website_quality(soup, url, response)
            data.update(quality_metrics)

            self.logger.debug(f"Website scraped successfully: {url}")
            return data

        except requests.Timeout:
            self.logger.warning(f"Timeout scraping website: {url}")
        except requests.RequestException as e:
            self.logger.warning(f"Error scraping website {url}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {e}")

        return {}

    def _find_social_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """
        Find social media links in the page

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with social media URLs
        """
        social = {
            'instagram': '',
            'facebook': '',
        }

        try:
            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link.get('href', '').lower()

                # Check for Instagram
                if 'instagram.com' in href:
                    # Extract username/profile URL
                    instagram_match = re.search(r'instagram\.com/([^/\?]+)', href)
                    if instagram_match and not social['instagram']:
                        social['instagram'] = f"https://instagram.com/{instagram_match.group(1)}"

                # Check for Facebook
                if 'facebook.com' in href or 'fb.com' in href:
                    # Extract page URL
                    facebook_match = re.search(r'(?:facebook|fb)\.com/([^/\?]+)', href)
                    if facebook_match and not social['facebook']:
                        social['facebook'] = f"https://facebook.com/{facebook_match.group(1)}"

        except Exception as e:
            self.logger.debug(f"Error finding social links: {e}")

        return social

    def _analyze_website_quality(self, soup: BeautifulSoup, url: str, response: requests.Response) -> Dict:
        """
        Analyze website quality and assign a score

        Args:
            soup: BeautifulSoup object
            url: Website URL
            response: Response object

        Returns:
            Dictionary with quality metrics
        """
        quality_data = {
            'website_quality_score': 0,
            'is_mobile_responsive': False,
            'last_updated': None,
        }

        try:
            score = 0

            # Check HTTPS (security)
            if url.startswith('https://'):
                score += 20
                quality_data['has_https'] = True

            # Check for mobile responsiveness
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if viewport_meta:
                score += 15
                quality_data['is_mobile_responsive'] = True

            # Check for modern design indicators
            # - CSS frameworks (Bootstrap, Tailwind, etc.)
            stylesheets = soup.find_all('link', rel='stylesheet')
            has_modern_css = any('bootstrap' in str(link).lower() or 'tailwind' in str(link).lower()
                                for link in stylesheets)
            if has_modern_css:
                score += 10

            # Check for contact page
            has_contact = self._has_contact_page(soup)
            if has_contact:
                score += 15

            # Check if recently updated (look for copyright year)
            current_year = datetime.now().year
            copyright_match = re.search(r'©?\s*(\d{4})', soup.get_text())
            if copyright_match:
                year = int(copyright_match.group(1))
                quality_data['last_updated'] = year
                if year >= current_year - 1:  # Updated in last year
                    score += 20
                elif year >= current_year - 3:  # Updated in last 3 years
                    score += 10

            # Check for professional images
            images = soup.find_all('img')
            if len(images) >= 3:  # Has multiple images
                score += 10

            # Check for structured content
            if soup.find_all(['article', 'section']):
                score += 10

            quality_data['website_quality_score'] = min(score, 100)  # Cap at 100

        except Exception as e:
            self.logger.debug(f"Error analyzing website quality: {e}")

        return quality_data

    def _has_contact_page(self, soup: BeautifulSoup) -> bool:
        """
        Check if website has a contact page

        Args:
            soup: BeautifulSoup object

        Returns:
            True if contact page found, False otherwise
        """
        contact_keywords = ['kontakt', 'contact', 'kontakty', 'rezervace', 'reservation']

        # Check navigation links
        links = soup.find_all('a', href=True)
        for link in links:
            text = link.get_text().lower()
            href = link.get('href', '').lower()

            if any(keyword in text or keyword in href for keyword in contact_keywords):
                return True

        return False

    def scrape_websites(self, businesses: List[Dict]) -> List[Dict]:
        """
        Scrape websites for multiple businesses

        Args:
            businesses: List of business dictionaries with 'website' field

        Returns:
            List of businesses enriched with website data
        """
        self.logger.info(f"Scraping websites for {len(businesses)} businesses")

        enriched = []
        for i, business in enumerate(businesses):
            try:
                website = business.get('website', '')

                if not website:
                    enriched.append(business)
                    continue

                # Scrape website
                website_data = self.scrape_website(website)

                # Merge data (don't overwrite existing data)
                for key, value in website_data.items():
                    if value and not business.get(key):
                        business[key] = value

                enriched.append(business)

                # Rate limiting
                time.sleep(self.delay)

            except Exception as e:
                self.logger.error(f"Error processing business {i+1}: {e}")
                enriched.append(business)

        self.logger.info(f"Website scraping complete: {len(enriched)} businesses processed")
        return enriched

    def close(self):
        """Close the session"""
        self.session.close()