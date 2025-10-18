"""
Email extraction utilities for scraping websites
"""
import re
from typing import List, Set
from bs4 import BeautifulSoup
from utils.validators import validate_email


# Email patterns optimized for Czech websites
CZECH_EMAIL_PATTERNS = [
    # Standard email format
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    # Czech-specific domains
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.cz\b',
    # Common Czech prefixes
    r'\bkontakt@[A-Za-z0-9.-]+\.cz\b',
    r'\binfo@[A-Za-z0-9.-]+\.cz\b',
    r'\brezervace@[A-Za-z0-9.-]+\.cz\b',
    r'\bobchod@[A-Za-z0-9.-]+\.cz\b',
    r'\bsalon@[A-Za-z0-9.-]+\.cz\b',
]

# Common email obfuscation patterns
OBFUSCATION_PATTERNS = {
    r'\[at\]': '@',
    r'\(at\)': '@',
    r'\s+at\s+': '@',
    r'\[dot\]': '.',
    r'\(dot\)': '.',
    r'\s+dot\s+': '.',
    r'@\s+': '@',
    r'\s+@': '@',
}


def extract_emails_from_text(text: str) -> Set[str]:
    """
    Extract email addresses from plain text using regex patterns

    Args:
        text: Text to search for emails

    Returns:
        Set of unique email addresses found
    """
    if not text:
        return set()

    emails = set()

    # Apply deobfuscation patterns
    cleaned_text = text
    for pattern, replacement in OBFUSCATION_PATTERNS.items():
        cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)

    # Extract emails using patterns
    for pattern in CZECH_EMAIL_PATTERNS:
        found = re.findall(pattern, cleaned_text, re.IGNORECASE)
        emails.update(found)

    # Validate and clean emails
    valid_emails = set()
    for email in emails:
        email = email.lower().strip()
        if validate_email(email):
            valid_emails.add(email)

    return valid_emails


def extract_emails_from_html(html: str) -> Set[str]:
    """
    Extract email addresses from HTML content

    Args:
        html: HTML content to parse

    Returns:
        Set of unique email addresses found
    """
    if not html:
        return set()

    emails = set()

    try:
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()

        # Extract from mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE))
        for link in mailto_links:
            href = link.get('href', '')
            email_match = re.search(r'mailto:([^\?&]+)', href, re.IGNORECASE)
            if email_match:
                email = email_match.group(1).strip()
                if validate_email(email):
                    emails.add(email.lower())

        # Extract from text content
        text = soup.get_text(separator=' ')
        text_emails = extract_emails_from_text(text)
        emails.update(text_emails)

        # Check meta tags
        meta_tags = soup.find_all('meta', attrs={'name': re.compile(r'email|contact', re.IGNORECASE)})
        for tag in meta_tags:
            content = tag.get('content', '')
            if content:
                meta_emails = extract_emails_from_text(content)
                emails.update(meta_emails)

    except Exception as e:
        # If parsing fails, fall back to text extraction
        emails = extract_emails_from_text(html)

    return emails


def filter_emails(emails: Set[str], domain: str = None) -> List[str]:
    """
    Filter and prioritize emails

    Args:
        emails: Set of email addresses
        domain: Optional domain to prioritize

    Returns:
        Sorted list of emails (prioritized)
    """
    if not emails:
        return []

    email_list = list(emails)

    # Priority order for common Czech business email prefixes
    priority_prefixes = [
        'kontakt@',
        'info@',
        'rezervace@',
        'obchod@',
        'salon@',
        'kavarna@',
        'restaurace@',
    ]

    def email_priority(email: str) -> int:
        """Calculate priority score for email (lower is better)"""
        score = 100

        # Prioritize domain match
        if domain and email.endswith(f'@{domain}'):
            score -= 50

        # Prioritize Czech domains
        if email.endswith('.cz'):
            score -= 20

        # Prioritize common business prefixes
        for i, prefix in enumerate(priority_prefixes):
            if email.startswith(prefix):
                score -= (10 - i)
                break

        # Deprioritize generic emails
        generic = ['noreply@', 'no-reply@', 'mailer-daemon@', 'postmaster@']
        if any(email.startswith(g) for g in generic):
            score += 100

        return score

    # Sort by priority
    email_list.sort(key=email_priority)

    return email_list


def get_primary_email(emails: Set[str], domain: str = None) -> str:
    """
    Get the most likely primary business email

    Args:
        emails: Set of email addresses
        domain: Optional business domain

    Returns:
        Primary email address or empty string
    """
    filtered = filter_emails(emails, domain)
    return filtered[0] if filtered else ""


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL for email filtering

    Args:
        url: Website URL

    Returns:
        Domain name without www
    """
    if not url:
        return ""

    # Remove protocol and path
    domain = re.sub(r'https?://', '', url)
    domain = domain.split('/')[0]

    # Remove www
    domain = re.sub(r'^www\.', '', domain)

    return domain.lower()
