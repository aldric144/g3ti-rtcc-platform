"""
String utilities for the G3TI RTCC-UIP Backend.

This module provides helper functions for string manipulation
and formatting.
"""

import re
import unicodedata


def slugify(value: str, max_length: int = 50) -> str:
    """
    Convert a string to a URL-safe slug.

    Args:
        value: String to convert
        max_length: Maximum length of slug

    Returns:
        str: URL-safe slug
    """
    # Normalize unicode characters
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")

    # Convert to lowercase and replace spaces with hyphens
    value = value.lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "-", value)
    value = value.strip("-")

    return value[:max_length]


def truncate(value: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        value: String to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated string
    """
    if len(value) <= max_length:
        return value

    return value[: max_length - len(suffix)] + suffix


def mask_sensitive(value: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """
    Mask sensitive data, showing only last few characters.

    Args:
        value: Value to mask
        visible_chars: Number of characters to show at end
        mask_char: Character to use for masking

    Returns:
        str: Masked value
    """
    if len(value) <= visible_chars:
        return mask_char * len(value)

    masked_length = len(value) - visible_chars
    return mask_char * masked_length + value[-visible_chars:]


def normalize_whitespace(value: str) -> str:
    """
    Normalize whitespace in a string.

    Replaces multiple spaces with single space and trims.

    Args:
        value: String to normalize

    Returns:
        str: Normalized string
    """
    return " ".join(value.split())


def to_snake_case(value: str) -> str:
    """
    Convert a string to snake_case.

    Args:
        value: String to convert

    Returns:
        str: snake_case string
    """
    # Insert underscore before uppercase letters
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_camel_case(value: str) -> str:
    """
    Convert a string to camelCase.

    Args:
        value: String to convert

    Returns:
        str: camelCase string
    """
    components = value.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_title_case(value: str) -> str:
    """
    Convert a string to Title Case.

    Args:
        value: String to convert

    Returns:
        str: Title Case string
    """
    # Handle snake_case and camelCase
    value = re.sub(r"_", " ", value)
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    return value.title()


def is_valid_email(value: str) -> bool:
    """
    Check if a string is a valid email address.

    Args:
        value: String to check

    Returns:
        bool: True if valid email
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value))


def is_valid_phone(value: str) -> bool:
    """
    Check if a string is a valid phone number.

    Args:
        value: String to check

    Returns:
        bool: True if valid phone number
    """
    # Remove common formatting characters
    cleaned = re.sub(r"[\s\-\(\)\.]", "", value)
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def format_phone(value: str) -> str:
    """
    Format a phone number for display.

    Args:
        value: Phone number to format

    Returns:
        str: Formatted phone number
    """
    # Remove non-digits
    digits = re.sub(r"\D", "", value)

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == "1":
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    return value


def extract_numbers(value: str) -> list[str]:
    """
    Extract all numbers from a string.

    Args:
        value: String to extract from

    Returns:
        list: List of number strings
    """
    return re.findall(r"\d+", value)
