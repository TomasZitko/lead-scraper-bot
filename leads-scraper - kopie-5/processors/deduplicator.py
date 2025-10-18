"""
Deduplicator
Removes duplicate business entries using fuzzy matching
"""
import logging
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class Deduplicator:
    """Removes duplicate business entries"""

    def __init__(self, similarity_threshold: float = 0.9, logger: logging.Logger = None):
        """
        Initialize deduplicator

        Args:
            similarity_threshold: Threshold for fuzzy name matching (0.0-1.0)
            logger: Logger instance
        """
        self.similarity_threshold = similarity_threshold
        self.logger = logger or logging.getLogger(__name__)

    def deduplicate(self, businesses: List[Dict]) -> List[Dict]:
        """
        Remove duplicate businesses from list

        Args:
            businesses: List of business dictionaries

        Returns:
            Deduplicated list of businesses
        """
        if not businesses:
            return []

        self.logger.info(f"Deduplicating {len(businesses)} businesses")

        # Track which businesses to keep
        unique_businesses = []
        seen_icos = set()
        seen_phones = set()
        processed_indices = set()

        for i, business in enumerate(businesses):
            if i in processed_indices:
                continue

            ico = business.get('ico', '')
            phone = business.get('phone', '')
            business_name = business.get('business_name', '')

            # Check for exact IČO match (strongest identifier)
            if ico and ico in seen_icos:
                self.logger.debug(f"Duplicate IČO found: {ico} ({business_name})")
                continue

            # Check for exact phone match
            if phone and phone in seen_phones:
                self.logger.debug(f"Duplicate phone found: {phone} ({business_name})")
                continue

            # Check for fuzzy name match with remaining businesses
            duplicate_index = self._find_fuzzy_duplicate(
                business, businesses[i+1:], start_index=i+1
            )

            if duplicate_index is not None:
                # Merge duplicate records
                duplicate = businesses[duplicate_index]
                merged = self._merge_duplicates(business, duplicate)
                unique_businesses.append(merged)
                processed_indices.add(duplicate_index)
                self.logger.debug(f"Merged duplicate: {business_name}")
            else:
                unique_businesses.append(business)

            # Mark as seen
            if ico:
                seen_icos.add(ico)
            if phone:
                seen_phones.add(phone)

            processed_indices.add(i)

        duplicates_removed = len(businesses) - len(unique_businesses)
        self.logger.info(f"Removed {duplicates_removed} duplicates. {len(unique_businesses)} unique businesses remain.")

        return unique_businesses

    def _find_fuzzy_duplicate(self, target: Dict, candidates: List[Dict], start_index: int = 0) -> int:
        """
        Find fuzzy duplicate in candidate list

        Args:
            target: Target business to match
            candidates: List of candidate businesses
            start_index: Starting index for matching

        Returns:
            Index of duplicate or None
        """
        target_name = target.get('business_name', '').lower().strip()
        target_address = target.get('address', '').lower().strip()

        if not target_name:
            return None

        for i, candidate in enumerate(candidates):
            candidate_name = candidate.get('business_name', '').lower().strip()

            if not candidate_name:
                continue

            # Calculate name similarity
            name_similarity = self._calculate_similarity(target_name, candidate_name)

            if name_similarity >= self.similarity_threshold:
                # High name similarity - check address for confirmation
                candidate_address = candidate.get('address', '').lower().strip()

                if target_address and candidate_address:
                    address_similarity = self._calculate_similarity(target_address, candidate_address)

                    # If addresses are very different, probably not a duplicate
                    if address_similarity < 0.5:
                        continue

                self.logger.debug(
                    f"Fuzzy match found: '{target_name}' ~ '{candidate_name}' "
                    f"(similarity: {name_similarity:.2f})"
                )
                return start_index + i

        return None

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity ratio (0.0-1.0)
        """
        return SequenceMatcher(None, str1, str2).ratio()

    def _merge_duplicates(self, business1: Dict, business2: Dict) -> Dict:
        """
        Merge two duplicate business records

        Args:
            business1: First business record
            business2: Second business record

        Returns:
            Merged business record with most complete data
        """
        # Start with the record that has more non-empty fields
        completeness1 = sum(1 for v in business1.values() if v)
        completeness2 = sum(1 for v in business2.values() if v)

        if completeness1 >= completeness2:
            merged = business1.copy()
            source = business2
        else:
            merged = business2.copy()
            source = business1

        # Fill in missing fields from the other record
        for key, value in source.items():
            if value and not merged.get(key):
                merged[key] = value

        # Special handling for ratings and scores (use higher value)
        if 'google_rating' in source and source['google_rating']:
            merged_rating = merged.get('google_rating')
            if merged_rating is None or source['google_rating'] > merged_rating:
                merged['google_rating'] = source['google_rating']

        if 'website_quality_score' in source:
            merged_score = merged.get('website_quality_score', 0)
            if source['website_quality_score'] > merged_score:
                merged['website_quality_score'] = source['website_quality_score']

        # Merge business activities
        activities1 = set(merged.get('business_activities', []))
        activities2 = set(source.get('business_activities', []))
        merged['business_activities'] = list(activities1.union(activities2))

        return merged

    def remove_invalid_entries(self, businesses: List[Dict]) -> List[Dict]:
        """
        Remove businesses with insufficient data

        Args:
            businesses: List of business dictionaries

        Returns:
            Filtered list of valid businesses
        """
        valid_businesses = []

        for business in businesses:
            # Must have at least a business name
            if not business.get('business_name'):
                self.logger.debug("Skipping business without name")
                continue

            # Should have at least one contact method or address
            has_contact = any([
                business.get('phone'),
                business.get('email'),
                business.get('website'),
                business.get('address'),
            ])

            if not has_contact:
                self.logger.debug(f"Skipping business without contact info: {business.get('business_name')}")
                continue

            valid_businesses.append(business)

        removed = len(businesses) - len(valid_businesses)
        if removed > 0:
            self.logger.info(f"Removed {removed} invalid entries")

        return valid_businesses
