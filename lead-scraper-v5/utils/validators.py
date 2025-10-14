"""
Validation utilities for data quality checks
"""
import re
from typing import Optional
from urllib.parse import urlparse
import validators as val


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False

    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    return val.url(url) is True


def validate_email(email: str) -> bool:
    """
    Validate if a string is a valid email address

    Args:
        email: Email string to validate

    Returns:
        True if valid email, False otherwise
    """
    if not email:
        return False

    return val.email(email) is True


def validate_phone(phone: str) -> bool:
    """
    Validate Czech phone number format

    Args:
        phone: Phone number string to validate

    Returns:
        True if valid phone number, False otherwise
    """
    if not phone:
        return False

    # Remove common separators and spaces
    clean_phone = re.sub(r'[\s\-\(\)]+', '', phone)

    # Czech phone patterns:
    # +420XXXXXXXXX or 00420XXXXXXXXX (international)
    # XXXXXXXXX (9 digits)
    patterns = [
        r'^\+420\d{9}$',
        r'^00420\d{9}$',
        r'^\d{9}$',
        r'^\+420\s?\d{3}\s?\d{3}\s?\d{3}$',
    ]

    return any(re.match(pattern, clean_phone) for pattern in patterns)


def validate_ico(ico: str) -> bool:
    """
    Validate Czech IČO (company identification number)
    IČO is 8 digits

    Args:
        ico: IČO string to validate

    Returns:
        True if valid IČO format, False otherwise
    """
    if not ico:
        return False

    # Remove spaces and check if it's 8 digits
    clean_ico = ico.replace(' ', '')

    if not re.match(r'^\d{8}$', clean_ico):
        return False

    # IČO checksum validation (last digit is checksum)
    weights = [8, 7, 6, 5, 4, 3, 2]
    try:
        digits = [int(d) for d in clean_ico]
        checksum = sum(w * d for w, d in zip(weights, digits[:7]))
        checksum_digit = (11 - (checksum % 11)) % 10

        return digits[7] == checksum_digit
    except (ValueError, IndexError):
        return False


def normalize_url(url: str) -> Optional[str]:
    """
    Normalize URL to consistent format

    Args:
        url: URL to normalize

    Returns:
        Normalized URL or None if invalid
    """
    if not url:
        return None

    # Add https if no scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Validate and return
    if validate_url(url):
        parsed = urlparse(url)
        # Ensure lowercase domain
        return f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"

    return None


def normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize Czech phone number to +420XXXXXXXXX format

    Args:
        phone: Phone number to normalize

    Returns:
        Normalized phone number or None if invalid
    """
    if not phone:
        return None

    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Remove leading 00 if present (international prefix)
    if digits.startswith('00'):
        digits = digits[2:]

    # Remove country code if present
    if digits.startswith('420'):
        digits = digits[3:]

    # Should have exactly 9 digits now
    if len(digits) == 9:
        return f"+420{digits}"

    return None


def normalize_email(email: str) -> Optional[str]:
    """
    Normalize email address to lowercase

    Args:
        email: Email to normalize

    Returns:
        Normalized email or None if invalid
    """
    if not email:
        return None

    email = email.strip().lower()

    if validate_email(email):
        return email

    return None


def is_czech_domain(url: str) -> bool:
    """
    Check if URL is a Czech domain (.cz)

    Args:
        url: URL to check

    Returns:
        True if Czech domain, False otherwise
    """
    if not url:
        return False

    try:
        parsed = urlparse(url if url.startswith('http') else f'https://{url}')
        return parsed.netloc.lower().endswith('.cz')
    except Exception:
        return False


def clean_business_name(name: str) -> str:
    """
    Clean and normalize business name

    Args:
        name: Business name to clean

    Returns:
        Cleaned business name
    """
    if not name:
        return ""

    # Remove extra whitespace
    name = ' '.join(name.split())

    # Remove common suffixes
    suffixes = [' s.r.o.', ' s r o', ' s. r. o.', ' a.s.', ' a s', ' v.o.s.']
    name_lower = name.lower()

    for suffix in suffixes:
        if name_lower.endswith(suffix):
            name = name[:len(name) - len(suffix)]
            break

    return name.strip()
