"""
Geographic utilities for the G3TI RTCC-UIP Backend.

This module provides helper functions for geographic calculations
and coordinate handling.
"""

import math

# Earth's radius in miles
EARTH_RADIUS_MILES = 3958.8
EARTH_RADIUS_KM = 6371.0


def calculate_distance(
    lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "miles"
) -> float:
    """
    Calculate the distance between two points using the Haversine formula.

    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        unit: Distance unit ("miles" or "km")

    Returns:
        float: Distance between points
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    radius = EARTH_RADIUS_MILES if unit == "miles" else EARTH_RADIUS_KM
    return radius * c


def is_within_bounds(lat: float, lon: float, bounds: dict[str, float]) -> bool:
    """
    Check if a point is within geographic bounds.

    Args:
        lat: Latitude to check
        lon: Longitude to check
        bounds: Dict with north, south, east, west bounds

    Returns:
        bool: True if point is within bounds
    """
    north = bounds.get("north", 90)
    south = bounds.get("south", -90)
    east = bounds.get("east", 180)
    west = bounds.get("west", -180)

    return south <= lat <= north and west <= lon <= east


def is_within_radius(
    lat: float, lon: float, center_lat: float, center_lon: float, radius_miles: float
) -> bool:
    """
    Check if a point is within a radius of a center point.

    Args:
        lat: Latitude to check
        lon: Longitude to check
        center_lat: Center latitude
        center_lon: Center longitude
        radius_miles: Radius in miles

    Returns:
        bool: True if point is within radius
    """
    distance = calculate_distance(lat, lon, center_lat, center_lon)
    return distance <= radius_miles


def format_coordinates(lat: float, lon: float, format_type: str = "decimal") -> str:
    """
    Format coordinates for display.

    Args:
        lat: Latitude
        lon: Longitude
        format_type: "decimal" or "dms" (degrees/minutes/seconds)

    Returns:
        str: Formatted coordinates
    """
    if format_type == "decimal":
        return f"{lat:.6f}, {lon:.6f}"

    # DMS format
    def to_dms(value: float, is_lat: bool) -> str:
        direction = ""
        if is_lat:
            direction = "N" if value >= 0 else "S"
        else:
            direction = "E" if value >= 0 else "W"

        value = abs(value)
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = ((value - degrees) * 60 - minutes) * 60

        return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"

    return f"{to_dms(lat, True)} {to_dms(lon, False)}"


def get_bounding_box(lat: float, lon: float, radius_miles: float) -> dict[str, float]:
    """
    Get a bounding box around a point.

    Args:
        lat: Center latitude
        lon: Center longitude
        radius_miles: Radius in miles

    Returns:
        dict: Bounding box with north, south, east, west
    """
    # Approximate degrees per mile
    lat_delta = radius_miles / 69.0
    lon_delta = radius_miles / (69.0 * math.cos(math.radians(lat)))

    return {
        "north": lat + lat_delta,
        "south": lat - lat_delta,
        "east": lon + lon_delta,
        "west": lon - lon_delta,
    }


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate that coordinates are within valid ranges.

    Args:
        lat: Latitude to validate
        lon: Longitude to validate

    Returns:
        bool: True if coordinates are valid
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def get_center_point(coordinates: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Calculate the center point of multiple coordinates.

    Args:
        coordinates: List of (lat, lon) tuples

    Returns:
        tuple: (center_lat, center_lon)
    """
    if not coordinates:
        return (0.0, 0.0)

    total_lat = sum(c[0] for c in coordinates)
    total_lon = sum(c[1] for c in coordinates)
    count = len(coordinates)

    return (total_lat / count, total_lon / count)
