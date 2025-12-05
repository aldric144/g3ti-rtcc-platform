"""
Date/time utilities for the G3TI RTCC-UIP Backend.

This module provides helper functions for working with dates and times
in a consistent manner across the application.

All times are stored and processed in UTC.
"""

from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    """
    Get the current UTC datetime.

    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(UTC)


def parse_datetime(value: str | datetime | None) -> datetime | None:
    """
    Parse a datetime from various formats.

    Supports:
    - ISO 8601 format (with or without timezone)
    - Unix timestamp (as string)
    - datetime objects

    Args:
        value: Value to parse

    Returns:
        datetime or None: Parsed datetime in UTC
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)

    # Try parsing as ISO format
    try:
        # Handle 'Z' suffix
        value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except ValueError:
        pass

    # Try parsing as timestamp
    try:
        timestamp = float(value)
        return datetime.fromtimestamp(timestamp, tz=UTC)
    except ValueError:
        pass

    return None


def format_datetime(dt: datetime | None, format_str: str = "%Y-%m-%dT%H:%M:%SZ") -> str | None:
    """
    Format a datetime to string.

    Args:
        dt: Datetime to format
        format_str: Format string (default: ISO 8601)

    Returns:
        str or None: Formatted datetime string
    """
    if dt is None:
        return None

    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)

    return dt.strftime(format_str)


def datetime_to_timestamp(dt: datetime | None) -> int | None:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: Datetime to convert

    Returns:
        int or None: Unix timestamp in seconds
    """
    if dt is None:
        return None

    return int(dt.timestamp())


def timestamp_to_datetime(timestamp: int | float | None) -> datetime | None:
    """
    Convert Unix timestamp to datetime.

    Args:
        timestamp: Unix timestamp in seconds

    Returns:
        datetime or None: UTC datetime
    """
    if timestamp is None:
        return None

    return datetime.fromtimestamp(timestamp, tz=UTC)


def time_ago(dt: datetime) -> str:
    """
    Get human-readable time difference from now.

    Args:
        dt: Datetime to compare

    Returns:
        str: Human-readable time difference
    """
    now = utc_now()

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    diff = now - dt

    if diff < timedelta(seconds=60):
        return "just now"
    elif diff < timedelta(minutes=60):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(hours=24):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(diff.days / 365)
        return f"{years} year{'s' if years != 1 else ''} ago"


def is_within_range(
    dt: datetime, start: datetime | None = None, end: datetime | None = None
) -> bool:
    """
    Check if datetime is within a range.

    Args:
        dt: Datetime to check
        start: Range start (inclusive)
        end: Range end (inclusive)

    Returns:
        bool: True if within range
    """
    if start is not None and dt < start:
        return False
    if end is not None and dt > end:
        return False
    return True
