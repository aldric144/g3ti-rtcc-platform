"""
Utility modules for the G3TI RTCC-UIP Backend.

This module provides common utilities including:
- Date/time helpers
- String manipulation
- Validation helpers
- Geo utilities
- Formatting functions
"""

from app.utils.datetime_utils import (
    datetime_to_timestamp,
    format_datetime,
    parse_datetime,
    timestamp_to_datetime,
    utc_now,
)
from app.utils.geo_utils import (
    calculate_distance,
    format_coordinates,
    is_within_bounds,
)
from app.utils.string_utils import (
    mask_sensitive,
    normalize_whitespace,
    slugify,
    truncate,
)

__all__ = [
    "utc_now",
    "parse_datetime",
    "format_datetime",
    "datetime_to_timestamp",
    "timestamp_to_datetime",
    "slugify",
    "truncate",
    "mask_sensitive",
    "normalize_whitespace",
    "calculate_distance",
    "is_within_bounds",
    "format_coordinates",
]
