"""
Data Merger
Merges and consolidates data from multiple sources
"""
import logging
from typing import List, Dict, Optional


class DataMerger:
    """Merges business data from multiple sources"""

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize data merger

        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

    def merge_business_data(self, *data_sources: List[Dict]) -> List[Dict]:
        """
        Merge business data from multiple sources

        Args:
            *data_sources: Variable number of data source lists

        Returns:
            Merged list of business dictionaries
        """
        if not data_sources:
            return []

        # Start with first data source
        merged = list(data_sources[0])

        self.logger.info(f"Merging data from {len(data_sources)} sources")

        # Merge additional sources
        for source in data_sources[1:]:
            for business in source:
                # Try to find matching business in merged list
                match_index = self._find_matching_business(merged, business)

                if match_index is not None:
                    # Merge with existing business
                    merged[match_index] = self._merge_business_records(merged[match_index], business)
                else:
                    # Add as new business
                    merged.append(business)

        self.logger.info(f"Merged {len(merged)} unique businesses")
        return merged

    def _find_matching_business(self, businesses: List[Dict], target: Dict) -> Optional[int]:
        """
        Find a matching business in the list

        Args:
            businesses: List of business dictionaries
            target: Business to find

        Returns:
            Index of matching business or None
        """
        target_name = target.get('business_name', '').lower()
        target_ico = target.get('ico', '')
        target_phone = target.get('phone', '')

        for i, business in enumerate(businesses):
            # Match by IČO (strongest match)
            if target_ico and business.get('ico') == target_ico:
                return i

            # Match by phone
            if target_phone and business.get('phone') == target_phone:
                return i

            # Match by business name (exact)
            business_name = business.get('business_name', '').lower()
            if target_name and business_name == target_name:
                return i

        return None

    def _merge_business_records(self, existing: Dict, new: Dict) -> Dict:
        """
        Merge two business records, prioritizing non-empty values

        Args:
            existing: Existing business record
            new: New business record

        Returns:
            Merged business record
        """
        merged = existing.copy()

        # For each field in new record
        for key, value in new.items():
            # Skip empty values
            if not value:
                continue

            # If existing record doesn't have this field or it's empty, use new value
            if not merged.get(key):
                merged[key] = value
            # Special handling for ratings (prefer higher)
            elif key == 'google_rating' and isinstance(value, (int, float)):
                existing_rating = merged.get('google_rating')
                if existing_rating is None or value > existing_rating:
                    merged[key] = value
            # Special handling for quality scores (prefer higher)
            elif key == 'website_quality_score' and isinstance(value, (int, float)):
                existing_score = merged.get('website_quality_score', 0)
                if value > existing_score:
                    merged[key] = value

        return merged

    def fill_missing_fields(self, businesses: List[Dict]) -> List[Dict]:
        """
        Ensure all businesses have all required fields

        Args:
            businesses: List of business dictionaries

        Returns:
            List with all fields populated
        """
        required_fields = {
            'business_name': '',
            'ico': '',
            'address': '',
            'city': '',
            'postal_code': '',
            'phone': '',
            'email': '',
            'website': '',
            'instagram': '',
            'facebook': '',
            'google_rating': None,
            'business_activities': [],
            'website_quality_score': 0,
            'priority_score': 0,
            'notes': '',
            'source': '',
        }

        for business in businesses:
            for field, default in required_fields.items():
                if field not in business:
                    business[field] = default

        return businesses

    def clean_data(self, businesses: List[Dict]) -> List[Dict]:
        """
        Clean and normalize business data

        Args:
            businesses: List of business dictionaries

        Returns:
            Cleaned list of businesses
        """
        cleaned = []

        for business in businesses:
            # Skip businesses without name
            if not business.get('business_name'):
                self.logger.debug("Skipping business without name")
                continue

            # Clean business name
            business['business_name'] = business['business_name'].strip()

            # Remove duplicates in lists
            if isinstance(business.get('business_activities'), list):
                business['business_activities'] = list(set(business['business_activities']))

            # Ensure numeric fields are proper type
            if 'google_rating' in business and business['google_rating']:
                try:
                    business['google_rating'] = float(business['google_rating'])
                except (ValueError, TypeError):
                    business['google_rating'] = None

            if 'website_quality_score' in business:
                try:
                    business['website_quality_score'] = int(business['website_quality_score'])
                except (ValueError, TypeError):
                    business['website_quality_score'] = 0

            cleaned.append(business)

        return cleaned
