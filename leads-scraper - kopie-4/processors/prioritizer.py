"""
Lead Prioritizer
Scores and prioritizes leads based on opportunity criteria
"""
import logging
from typing import List, Dict


class LeadPrioritizer:
    """Scores and prioritizes business leads"""

    # Priority categories
    PRIORITY_IMMEDIATE = "IMMEDIATE OPPORTUNITY"
    PRIORITY_HIGH = "HIGH PRIORITY"
    PRIORITY_MEDIUM = "MEDIUM PRIORITY"
    PRIORITY_LOW = "LOW PRIORITY"

    def __init__(self, scoring_config: Dict = None, logger: logging.Logger = None):
        """
        Initialize lead prioritizer

        Args:
            scoring_config: Dictionary with scoring weights
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

        # Default scoring weights
        self.scoring = scoring_config or {
            'no_website': 100,
            'poor_website': 75,
            'no_email': 50,
            'no_social': 25,
        }

    def score_leads(self, businesses: List[Dict]) -> List[Dict]:
        """
        Calculate priority scores for all leads

        Args:
            businesses: List of business dictionaries

        Returns:
            List with priority_score and priority_category fields added
        """
        self.logger.info(f"Scoring {len(businesses)} leads")

        scored = []
        for business in businesses:
            score = self._calculate_priority_score(business)
            business['priority_score'] = score
            business['priority_category'] = self._get_priority_category(score)
            scored.append(business)

        # Sort by priority score (descending)
        scored.sort(key=lambda x: x['priority_score'], reverse=True)

        self._log_score_distribution(scored)

        return scored

    def _calculate_priority_score(self, business: Dict) -> int:
        """
        Calculate priority score for a single business

        Scoring logic:
        - No website: +100 points (highest opportunity)
        - Poor website quality: +75 points
        - No email: +50 points
        - No social media: +25 points
        - Low Google rating: -10 points
        - No reviews: +20 points

        Args:
            business: Business dictionary

        Returns:
            Priority score (0-200)
        """
        score = 0

        # Check website status
        website = business.get('website', '')
        website_quality = business.get('website_quality_score', 0)

        if not website:
            # No website = highest priority
            score += self.scoring['no_website']
            business['notes'] = self._add_note(business.get('notes', ''), "No website - High opportunity")
        elif website_quality < 50:
            # Poor website = high priority
            score += self.scoring['poor_website']
            business['notes'] = self._add_note(business.get('notes', ''), "Poor website quality")

        # Check email
        email = business.get('email', '')
        if not email:
            score += self.scoring['no_email']
            business['notes'] = self._add_note(business.get('notes', ''), "No email found")

        # Check social media presence
        instagram = business.get('instagram', '')
        facebook = business.get('facebook', '')
        if not instagram and not facebook:
            score += self.scoring['no_social']
            business['notes'] = self._add_note(business.get('notes', ''), "No social media")

        # Check Google rating
        rating = business.get('google_rating')
        if rating is not None:
            if rating < 3.5:
                score -= 10
                business['notes'] = self._add_note(business.get('notes', ''), "Low Google rating")
        else:
            # No rating = might be new business
            score += 20
            business['notes'] = self._add_note(business.get('notes', ''), "No Google reviews")

        # Bonus for Czech domain (local business)
        if website and '.cz' in website:
            score += 5

        # Ensure score is within reasonable bounds
        score = max(0, min(score, 200))

        return score

    def _get_priority_category(self, score: int) -> str:
        """
        Get priority category based on score

        Args:
            score: Priority score

        Returns:
            Priority category string
        """
        if score >= 90:
            return self.PRIORITY_IMMEDIATE
        elif score >= 75:
            return self.PRIORITY_HIGH
        elif score >= 50:
            return self.PRIORITY_MEDIUM
        else:
            return self.PRIORITY_LOW

    def _add_note(self, existing_notes: str, new_note: str) -> str:
        """
        Add a note to existing notes

        Args:
            existing_notes: Existing notes string
            new_note: New note to add

        Returns:
            Combined notes string
        """
        if existing_notes:
            return f"{existing_notes}; {new_note}"
        return new_note

    def _log_score_distribution(self, businesses: List[Dict]) -> None:
        """
        Log distribution of priority scores

        Args:
            businesses: List of scored businesses
        """
        distribution = {
            self.PRIORITY_IMMEDIATE: 0,
            self.PRIORITY_HIGH: 0,
            self.PRIORITY_MEDIUM: 0,
            self.PRIORITY_LOW: 0,
        }

        for business in businesses:
            category = business.get('priority_category', self.PRIORITY_LOW)
            distribution[category] += 1

        self.logger.info("Priority distribution:")
        for category, count in distribution.items():
            percentage = (count / len(businesses) * 100) if businesses else 0
            self.logger.info(f"  {category}: {count} ({percentage:.1f}%)")

    def filter_by_priority(self, businesses: List[Dict], min_score: int = 0) -> List[Dict]:
        """
        Filter businesses by minimum priority score

        Args:
            businesses: List of business dictionaries
            min_score: Minimum priority score

        Returns:
            Filtered list of businesses
        """
        filtered = [b for b in businesses if b.get('priority_score', 0) >= min_score]
        self.logger.info(f"Filtered to {len(filtered)} businesses with score >= {min_score}")
        return filtered

    def get_high_priority_leads(self, businesses: List[Dict]) -> List[Dict]:
        """
        Get only high-priority leads (score >= 75)

        Args:
            businesses: List of business dictionaries

        Returns:
            List of high-priority businesses
        """
        return [b for b in businesses if b.get('priority_score', 0) >= 75]

    def get_immediate_opportunities(self, businesses: List[Dict]) -> List[Dict]:
        """
        Get immediate opportunity leads (score >= 90)

        Args:
            businesses: List of business dictionaries

        Returns:
            List of immediate opportunity businesses
        """
        return [b for b in businesses if b.get('priority_score', 0) >= 90]
