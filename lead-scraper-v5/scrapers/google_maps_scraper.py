"""
Enhanced Google Maps Scraper - AGGRESSIVE VERSION
Extracts ALL businesses with aggressive scrolling and complete data
"""
import time
import random
import logging
import re
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

# Anti-detection imports
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Install undetected-chromedriver: pip install undetected-chromedriver")

from utils.validators import normalize_phone, normalize_url, clean_business_name


class EnhancedGoogleMapsScraper:
    """Professional Google Maps scraper with AGGRESSIVE extraction"""

    def __init__(self, timeout: int = 30, logger: logging.Logger = None):
        """Initialize enhanced scraper"""
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        self.use_selenium = False
        
        # User agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Initialize stealth browser
        if SELENIUM_AVAILABLE:
            try:
                self._init_stealth_browser()
                self.use_selenium = True
            except Exception as e:
                self.logger.warning(f"Stealth browser init failed: {e}")
    
    def _init_stealth_browser(self):
        """Initialize undetected Chrome"""
        try:
            self.logger.info("🕵️  Initializing stealth browser...")
            
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument(f'user-agent={random.choice(self.user_agents)}')
            
            # Window size
            options.add_argument(f'--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}')
            
            self.driver = uc.Chrome(options=options)
            self._inject_stealth_js()
            
            self.logger.info("✅ Stealth browser initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to init stealth browser: {e}")
            raise

    def _inject_stealth_js(self):
        """Inject stealth JavaScript"""
        try:
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
            """
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_js})
        except:
            pass

    def search_businesses_on_maps(self, keyword: str, location: str, max_results: int = 500) -> List[Dict]:
        """
        Search Google Maps and extract COMPLETE data
        
        CRITICAL FIX: Much more aggressive scrolling to get ALL results
        """
        if not self.use_selenium or not self.driver:
            self.logger.warning("Selenium not available")
            return []
        
        businesses = []
        
        try:
            query = f"{keyword} {location}"
            self.logger.info(f"🔍 Searching Google Maps: {query}")
            
            # Navigate
            self._human_navigate_to_maps(query)
            time.sleep(random.uniform(4, 6))
            
            # Get ALL listings with AGGRESSIVE scrolling
            listings = self._aggressive_scroll_and_collect(max_results)
            
            self.logger.info(f"📋 Found {len(listings)} listings to process")
            
            # Extract data from each listing
            for idx, listing in enumerate(listings[:max_results], 1):
                try:
                    if idx % 10 == 0:
                        self.logger.info(f"   Processing {idx}/{len(listings)}...")
                    
                    business_data = self._extract_complete_business_data(listing)
                    
                    if business_data and business_data.get('business_name'):
                        businesses.append(business_data)
                    
                    # Small delay
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    self.logger.debug(f"Error processing listing {idx}: {e}")
                    continue
            
            self.logger.info(f"✅ Found {len(businesses)} businesses")
            
        except Exception as e:
            self.logger.error(f"Error in Maps search: {e}")
        
        return businesses

    def _human_navigate_to_maps(self, query: str):
        """Navigate like human"""
        try:
            # Go to Google first
            self.driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 3))
            
            # Now Maps
            encoded_query = query.replace(' ', '+')
            maps_url = f"https://www.google.com/maps/search/{encoded_query}"
            self.driver.get(maps_url)
            time.sleep(random.uniform(3, 4))
            
        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            raise

    def _aggressive_scroll_and_collect(self, max_results: int) -> List:
        """
        AGGRESSIVE scrolling to get ALL listing elements
        
        CRITICAL FIX: Much more scrolling, slower pace, better detection
        """
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Find results container
            possible_selectors = [
                "div[role='feed']",
                "div.m6QErb",
                "div[aria-label*='Results']",
            ]
            
            results_container = None
            for selector in possible_selectors:
                try:
                    results_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    self.logger.info(f"✓ Found results with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not results_container:
                self.logger.warning("Could not find results container")
                return []
            
            # AGGRESSIVE SCROLLING PARAMETERS
            last_height = 0
            scroll_attempts = 0
            max_scrolls = 100  # Much higher limit!
            stale_count = 0  # Count how many times height didn't change
            max_stale = 5  # Give up after 5 consecutive no-changes
            
            self.logger.info(f"🔄 Starting aggressive scrolling (max {max_scrolls} scrolls)...")
            
            while scroll_attempts < max_scrolls:
                try:
                    # Scroll down
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        results_container
                    )
                    
                    # LONGER delay to let content load
                    time.sleep(random.uniform(3, 5))
                    
                    # Get new height
                    new_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight", 
                        results_container
                    )
                    
                    # Check current count
                    current_listings = self._get_current_listings()
                    current_count = len(current_listings)
                    
                    if scroll_attempts % 5 == 0:
                        self.logger.info(f"   Scroll {scroll_attempts}: {current_count} listings found")
                    
                    # Check if height changed
                    if new_height == last_height:
                        stale_count += 1
                        if stale_count >= max_stale:
                            self.logger.info(f"   ✓ Reached end after {scroll_attempts} scrolls (no new content)")
                            break
                    else:
                        stale_count = 0  # Reset stale counter
                    
                    last_height = new_height
                    scroll_attempts += 1
                    
                    # Check if we have enough
                    if current_count >= max_results:
                        self.logger.info(f"   ✓ Target reached: {current_count} listings")
                        break
                    
                    # Small random variation in scrolling
                    if scroll_attempts % 10 == 0:
                        # Sometimes scroll up a bit (human behavior)
                        self.driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollTop - 200",
                            results_container
                        )
                        time.sleep(1)
                
                except StaleElementReferenceException:
                    # Element became stale, try to re-find it
                    self.logger.debug("Stale element, refinding...")
                    for selector in possible_selectors:
                        try:
                            results_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue
            
            # Get all visible listings
            all_listings = self._get_current_listings()
            self.logger.info(f"✓ Collected {len(all_listings)} listings after {scroll_attempts} scrolls")
            
            return all_listings
            
        except Exception as e:
            self.logger.error(f"Error in aggressive scrolling: {e}")
            return []

    def _get_current_listings(self) -> List:
        """Get currently visible listing elements"""
        listing_selectors = [
            "div.Nv2PK",
            "a.hfpxzc",
            "div[jsaction*='mouseover']",
        ]
        
        for selector in listing_selectors:
            try:
                listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if listings:
                    return listings
            except:
                continue
        
        return []

    def _extract_complete_business_data(self, listing) -> Optional[Dict]:
        """
        Click into listing and extract COMPLETE data
        """
        try:
            # Click the listing
            try:
                listing.click()
                time.sleep(random.uniform(2, 3))
            except:
                # If click fails, try JavaScript click
                self.driver.execute_script("arguments[0].click();", listing)
                time.sleep(random.uniform(2, 3))
            
            # Now extract data from the detail panel
            return self._extract_from_detail_panel()
            
        except Exception as e:
            self.logger.debug(f"Error extracting business data: {e}")
            return None

    def _extract_from_detail_panel(self) -> Optional[Dict]:
        """Extract data from the business detail panel"""
        try:
            wait = WebDriverWait(self.driver, 5)
            
            # Business name
            business_name = None
            name_selectors = [
                "h1.DUwDvf",
                "h1.fontHeadlineLarge",
                "h1",
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    business_name = name_elem.text.strip()
                    if business_name and len(business_name) > 2:
                        break
                except:
                    continue
            
            if not business_name:
                return None
            
            business_name = clean_business_name(business_name)
            
            # Website
            website = None
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                website = website_elem.get_attribute('href')
                website = normalize_url(website)
            except:
                pass
            
            # Phone
            phone = None
            try:
                phone_elem = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']")
                phone_text = phone_elem.get_attribute('data-item-id')
                if phone_text:
                    phone = phone_text.replace('phone:tel:', '')
                    phone = normalize_phone(phone)
            except:
                pass
            
            # Address
            address = None
            try:
                address_elem = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']")
                address = address_elem.get_attribute('aria-label')
                if address:
                    address = address.replace('Address: ', '').strip()
            except:
                pass
            
            # Rating
            rating = None
            try:
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']")
                rating_text = rating_elem.text.replace(',', '.')
                rating = float(rating_text)
            except:
                pass
            
            # Extract place ID from URL
            place_id = None
            try:
                current_url = self.driver.current_url
                if '1s' in current_url:
                    # Extract place ID from URL
                    match = re.search(r'1s([^!]+)', current_url)
                    if match:
                        place_id = match.group(1)
            except:
                pass
            
            return {
                'business_name': business_name,
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
                'source': 'google_maps_enhanced',
                'notes': 'Complete extraction with website'
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting from detail panel: {e}")
            return None

    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("✓ Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
