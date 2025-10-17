"""
Google Maps Scraper - SIMPLE WORKING VERSION
No fancy options, just works
"""
import time
import random
import logging
import re
from typing import Dict, List, Optional

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from utils.validators import normalize_phone, normalize_url, clean_business_name


class GoogleMapsScraper:
    """Simple working Google Maps scraper"""

    def __init__(self, timeout: int = 30, logger: logging.Logger = None):
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        self.use_selenium = False
        
        if SELENIUM_AVAILABLE:
            try:
                self._init_browser()
                self.use_selenium = True
            except Exception as e:
                self.logger.error(f"Browser init failed: {e}")

    def _init_browser(self):
        """Initialize Chrome - SIMPLE version"""
        try:
            self.logger.info("🕵️  Initializing browser...")
            
            options = uc.ChromeOptions()
            # ONLY simple, working options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            self.driver = uc.Chrome(options=options)
            self.logger.info("✅ Browser ready!")
            
        except Exception as e:
            self.logger.error(f"Browser init failed: {e}")
            raise

    def search_businesses_on_maps(self, keyword: str, location: str, max_results: int = 100) -> List[Dict]:
        """
        Search Google Maps and extract businesses
        """
        if not self.use_selenium or not self.driver:
            self.logger.warning("Selenium not available")
            return []
        
        businesses = []
        
        try:
            query = f"{keyword} {location}"
            self.logger.info(f"🔍 Searching: {query}")
            
            # Navigate
            maps_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            self.driver.get(maps_url)
            time.sleep(random.uniform(4, 6))
            
            # Scroll and collect
            listings = self._scroll_and_collect(max_results)
            
            if not listings:
                self.logger.warning("No listings found")
                return []
            
            self.logger.info(f"📋 Found {len(listings)} listings")
            
            # Extract data
            for idx, listing in enumerate(listings[:max_results], 1):
                try:
                    if idx % 10 == 0:
                        self.logger.info(f"   Processing {idx}/{len(listings)}...")
                    
                    business = self._extract_business(listing)
                    
                    if business and business.get('business_name'):
                        businesses.append(business)
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    self.logger.debug(f"Error on listing {idx}: {e}")
                    continue
            
            self.logger.info(f"✅ Extracted {len(businesses)} businesses")
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
        
        return businesses

    def _scroll_and_collect(self, max_results: int) -> List:
        """Scroll results panel and collect listings"""
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Find results container
            selectors = ["div[role='feed']", "div.m6QErb"]
            
            container = None
            for selector in selectors:
                try:
                    container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    self.logger.info(f"✓ Found results")
                    break
                except:
                    continue
            
            if not container:
                return []
            
            # Scroll
            last_height = 0
            scrolls = 0
            max_scrolls = 30
            no_change = 0
            
            while scrolls < max_scrolls:
                try:
                    # Scroll
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        container
                    )
                    
                    time.sleep(random.uniform(2, 3))
                    
                    # Check height
                    new_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight", 
                        container
                    )
                    
                    listings = self._get_listings()
                    
                    if scrolls % 3 == 0:
                        self.logger.info(f"   ✓ {len(listings)} listings after {scrolls} scrolls")
                    
                    if new_height == last_height:
                        no_change += 1
                        if no_change >= 3:
                            break
                    else:
                        no_change = 0
                    
                    last_height = new_height
                    scrolls += 1
                    
                    if len(listings) >= max_results:
                        break
                
                except StaleElementReferenceException:
                    for selector in selectors:
                        try:
                            container = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue
            
            return self._get_listings()
            
        except Exception as e:
            self.logger.error(f"Scroll error: {e}")
            return []

    def _get_listings(self) -> List:
        """Get visible listings"""
        selectors = ["div.Nv2PK", "a.hfpxzc"]
        
        for selector in selectors:
            try:
                listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if listings:
                    return listings
            except:
                continue
        
        return []

    def _extract_business(self, listing) -> Optional[Dict]:
        """Extract business data from listing"""
        try:
            # Click
            try:
                listing.click()
            except:
                self.driver.execute_script("arguments[0].click();", listing)
            
            time.sleep(random.uniform(2, 3))
            
            # Extract
            return self._extract_from_panel()
            
        except Exception as e:
            self.logger.debug(f"Extract error: {e}")
            return None

    def _extract_from_panel(self) -> Optional[Dict]:
        """Extract from detail panel"""
        try:
            # Name
            name = None
            name_selectors = ["h1.DUwDvf", "h1.fontHeadlineLarge", "h1"]
            
            for selector in name_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    name = elem.text.strip()
                    if name and len(name) > 2:
                        break
                except:
                    continue
            
            if not name:
                return None
            
            name = clean_business_name(name)
            
            # Website
            website = None
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                website = elem.get_attribute('href')
                website = normalize_url(website)
            except:
                pass
            
            # Phone
            phone = None
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']")
                phone_text = elem.get_attribute('data-item-id')
                if phone_text:
                    phone = phone_text.replace('phone:tel:', '')
                    phone = normalize_phone(phone)
            except:
                pass
            
            # Address
            address = None
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']")
                address = elem.get_attribute('aria-label')
                if address:
                    address = address.replace('Address: ', '').strip()
            except:
                pass
            
            # Rating
            rating = None
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']")
                rating_text = elem.text.replace(',', '.')
                rating = float(rating_text)
            except:
                pass
            
            # Place ID
            place_id = None
            try:
                url = self.driver.current_url
                if '1s' in url:
                    match = re.search(r'1s([^!]+)', url)
                    if match:
                        place_id = match.group(1)
            except:
                pass
            
            return {
                'business_name': name,
                'address': address or '',
                'city': '',
                'postal_code': '',
                'phone': phone or '',
                'email': '',
                'website': website or '',
                'instagram': '',
                'facebook': '',
                'google_rating': rating,
                'google_place_id': place_id,
                'source': 'google_maps',
                'notes': ''
            }
            
        except Exception as e:
            self.logger.debug(f"Panel extract error: {e}")
            return None

    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("✓ Browser closed")
            except:
                pass


# Alias for compatibility
EnhancedGoogleMapsScraper = GoogleMapsScraper