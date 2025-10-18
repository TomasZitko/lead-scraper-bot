"""
Czech Business Registry Enhancer
Finds contact info from rejstrik-firem.kurzy.cz for businesses without websites
"""
import logging
import time
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import quote_plus

from utils.validators import validate_email, normalize_phone


class RegistryEnhancer:
    """Enhance business data using Czech registry"""

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def enhance_business(self, business: Dict) -> Dict:
        """
        Enhance business data from Czech registry if no website
        
        Args:
            business: Business dictionary
            
        Returns:
            Enhanced business dictionary
        """
        # Only search if missing critical info
        needs_enhancement = (
            not business.get('website') or
            not business.get('email') or
            not business.get('phone')
        )
        
        if not needs_enhancement:
            return business
        
        business_name = business.get('business_name', '')
        if not business_name:
            return business
        
        try:
            self.logger.debug(f"Searching registry for: {business_name}")
            
            # Search Czech registry
            registry_data = self._search_registry(business_name)
            
            if registry_data:
                # Merge data (don't overwrite existing)
                if not business.get('website') and registry_data.get('website'):
                    business['website'] = registry_data['website']
                
                if not business.get('email') and registry_data.get('email'):
                    business['email'] = registry_data['email']
                
                if not business.get('phone') and registry_data.get('phone'):
                    business['phone'] = registry_data['phone']
                
                if not business.get('ico') and registry_data.get('ico'):
                    business['ico'] = registry_data['ico']
                
                self.logger.debug(f"Enhanced: {business_name}")
            
        except Exception as e:
            self.logger.debug(f"Registry search failed for {business_name}: {e}")
        
        return business

    def _search_registry(self, business_name: str) -> Optional[Dict]:
        """
        Search rejstrik-firem.kurzy.cz for business
        
        Args:
            business_name: Business name to search
            
        Returns:
            Dictionary with found data or None
        """
        try:
            # Build search URL
            encoded_name = quote_plus(business_name)
            search_url = f"https://rejstrik-firem.kurzy.cz/hledani/{encoded_name}/"
            
            # Search
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find first result
            result_link = soup.find('a', href=re.compile(r'/subjekt/'))
            
            if not result_link:
                return None
            
            # Get detail page
            detail_url = "https://rejstrik-firem.kurzy.cz" + result_link['href']
            detail_response = self.session.get(detail_url, timeout=10)
            detail_response.raise_for_status()
            
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
            
            # Extract data
            data = {}
            
            # Website
            website_elem = detail_soup.find('a', href=re.compile(r'^https?://'))
            if website_elem:
                data['website'] = website_elem['href']
            
            # Email
            email_text = detail_soup.get_text()
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_text)
            if emails:
                for email in emails:
                    if validate_email(email):
                        data['email'] = email.lower()
                        break
            
            # Phone
            phone_elems = detail_soup.find_all(string=re.compile(r'[\d\s\+]{9,}'))
            for elem in phone_elems:
                phone = re.sub(r'\s+', '', elem)
                normalized = normalize_phone(phone)
                if normalized:
                    data['phone'] = normalized
                    break
            
            # IČO
            ico_elem = detail_soup.find(string=re.compile(r'IČO|IČ:'))
            if ico_elem:
                ico_match = re.search(r'\d{8}', ico_elem.parent.get_text())
                if ico_match:
                    data['ico'] = ico_match.group()
            
            time.sleep(1)  # Rate limit
            
            return data if data else None
            
        except Exception as e:
            self.logger.debug(f"Registry fetch error: {e}")
            return None

    def enhance_batch(self, businesses: list) -> list:
        """
        Enhance multiple businesses
        
        Args:
            businesses: List of business dictionaries
            
        Returns:
            List of enhanced businesses
        """
        enhanced = []
        
        for business in businesses:
            try:
                enhanced_business = self.enhance_business(business)
                enhanced.append(enhanced_business)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.warning(f"Error enhancing business: {e}")
                enhanced.append(business)
        
        return enhanced