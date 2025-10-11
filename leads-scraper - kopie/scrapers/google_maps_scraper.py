"""
Google Maps Scraper
Enriches business data with Google Maps information using API or Selenium
"""
import time
import logging
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import googlemaps

from utils.validators import normalize_phone, normalize_url


class GoogleMapsScraper:
    """Scraper for Google Maps business information"""

    def __init__(self, api_key: str = "", use_api: bool = False, timeout: int = 30, logger: logging.Logger = None):
        """
        Initialize Google Maps scraper

        Args:
            api_key: Google Maps API key
            use_api: If True, use Google Maps API; otherwise use Selenium
            timeout: Request timeout in seconds
            logger: Logger instance
        """
        self.api_key = api_key
        self.use_api = use_api and api_key
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)

        # Initialize API client if using API
        if self.use_api:
            try:
                self.gmaps_client = googlemaps.Client(key=api_key)
                self.logger.info("Using Google Maps API")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Google Maps API: {e}. Falling back to Selenium.")
                self.use_api = False

        # Initialize Selenium driver if not using API
        self.driver = None
        if not self.use_api:
            self._init_selenium()

    def _init_selenium(self):
        """Initialize Selenium WebDriver"""
        try:
            self.logger.info("Initializing Selenium WebDriver for Google Maps")
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Selenium WebDriver initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.driver = None

    def search_business(self, business_name: str, address: str) -> Dict:
        """
        Search for business on Google Maps and extract information

        Args:
            business_name: Name of the business
            address: Business address

        Returns:
            Dictionary with enriched business data
        """
        if self.use_api:
            return self._search_with_api(business_name, address)
        else:
            return self._search_with_selenium(business_name, address)

    def _search_with_api(self, business_name: str, address: str) -> Dict:
        """
        Search using Google Maps Places API

        Args:
            business_name: Name of the business
            address: Business address

        Returns:
            Dictionary with business data
        """
        enriched_data = {}

        try:
            # Search for place
            query = f"{business_name}, {address}"
            self.logger.debug(f"Searching Google Maps API for: {query}")

            places_result = self.gmaps_client.places(query=query, language='cs')

            if places_result['status'] == 'OK' and places_result['results']:
                place = places_result['results'][0]
                place_id = place.get('place_id')

                # Get detailed place information
                if place_id:
                    details = self.gmaps_client.place(place_id=place_id, language='cs')

                    if details['status'] == 'OK':
                        result = details['result']

                        # Extract phone
                        phone = result.get('formatted_phone_number', '') or result.get('international_phone_number', '')
                        if phone:
                            enriched_data['phone'] = normalize_phone(phone) or phone

                        # Extract website
                        website = result.get('website', '')
                        if website:
                            enriched_data['website'] = normalize_url(website) or website

                        # Extract rating
                        rating = result.get('rating')
                        if rating:
                            enriched_data['google_rating'] = float(rating)

                        # Extract reviews count
                        reviews = result.get('user_ratings_total', 0)
                        enriched_data['reviews_count'] = reviews

                        # Extract business hours
                        if 'opening_hours' in result:
                            enriched_data['is_open'] = result['opening_hours'].get('open_now', None)

                        self.logger.debug(f"Enriched data from API: {enriched_data}")

        except Exception as e:
            self.logger.error(f"Error searching Google Maps API: {e}")

        return enriched_data

    def _search_with_selenium(self, business_name: str, address: str) -> Dict:
        """
        Search using Selenium (fallback method)

        Args:
            business_name: Name of the business
            address: Business address

        Returns:
            Dictionary with business data
        """
        enriched_data = {}

        if not self.driver:
            self.logger.warning("Selenium driver not initialized")
            return enriched_data

        try:
            # Build search URL
            query = f"{business_name} {address}"
            encoded_query = query.replace(' ', '+')
            url = f"https://www.google.com/maps/search/{encoded_query}"

            self.logger.debug(f"Searching Google Maps with Selenium: {query}")
            self.driver.get(url)

            # Wait for results to load
            time.sleep(3)

            # Try to click on the first result
            try:
                first_result = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Nv2PK a"))
                )
                first_result.click()
                time.sleep(2)
            except TimeoutException:
                self.logger.debug("No results found on Google Maps")
                return enriched_data

            # Extract phone number
            try:
                phone_elem = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                phone = phone_elem.get_attribute('data-item-id').replace('phone:tel:', '')
                if phone:
                    enriched_data['phone'] = normalize_phone(phone) or phone
            except NoSuchElementException:
                pass

            # Extract website
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                website = website_elem.get_attribute('href')
                if website:
                    enriched_data['website'] = normalize_url(website) or website
            except NoSuchElementException:
                pass

            # Extract rating
            try:
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, "span.ceNzKf")
                rating_text = rating_elem.get_attribute('aria-label')
                # Extract number from text like "4.5 stars"
                import re
                rating_match = re.search(r'(\d+[.,]\d+)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1).replace(',', '.'))
                    enriched_data['google_rating'] = rating
            except (NoSuchElementException, ValueError):
                pass

            self.logger.debug(f"Enriched data from Selenium: {enriched_data}")

        except Exception as e:
            self.logger.error(f"Error searching Google Maps with Selenium: {e}")

        return enriched_data

    def enrich_businesses(self, businesses: list) -> list:
        """
        Enrich multiple businesses with Google Maps data

        Args:
            businesses: List of business dictionaries

        Returns:
            List of enriched business dictionaries
        """
        self.logger.info(f"Enriching {len(businesses)} businesses with Google Maps data")

        enriched = []
        for i, business in enumerate(businesses):
            try:
                business_name = business.get('business_name', '')
                address = business.get('address', '')

                if not business_name:
                    enriched.append(business)
                    continue

                # Search Google Maps
                maps_data = self.search_business(business_name, address)

                # Merge data (don't overwrite existing data)
                for key, value in maps_data.items():
                    if value and not business.get(key):
                        business[key] = value

                enriched.append(business)

                # Rate limiting
                if not self.use_api:
                    time.sleep(2)  # Be nice to Google
                else:
                    time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error enriching business {i+1}: {e}")
                enriched.append(business)

        self.logger.info(f"Enrichment complete: {len(enriched)} businesses processed")
        return enriched

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium driver closed")
            except Exception as e:
                self.logger.error(f"Error closing Selenium driver: {e}")
