"""
Validation Engine - Comprehensive validation rules for all admin modules
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import re

from .base_admin import GeoPoint, GeoPolygon


class ValidationResult(BaseModel):
    """Result of a validation check"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidationEngine:
    """Centralized validation engine for all admin modules"""
    
    # GPS coordinate validation
    @staticmethod
    def validate_coordinates(lat: float, lng: float) -> ValidationResult:
        """Validate GPS coordinates"""
        errors = []
        
        if lat < -90 or lat > 90:
            errors.append(f"Latitude {lat} is out of range. Must be between -90 and 90.")
        
        if lng < -180 or lng > 180:
            errors.append(f"Longitude {lng} is out of range. Must be between -180 and 180.")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    # URL validation
    @staticmethod
    def validate_stream_url(url: str) -> ValidationResult:
        """Validate RTSP/HTTP stream URL"""
        errors = []
        warnings = []
        
        if not url:
            return ValidationResult(is_valid=True)
        
        # Check URL format
        url_pattern = r'^(rtsp|http|https)://[^\s]+$'
        if not re.match(url_pattern, url):
            errors.append("Invalid URL format. Must start with rtsp://, http://, or https://")
        
        # Check for common issues
        if 'localhost' in url.lower() or '127.0.0.1' in url:
            warnings.append("URL contains localhost - may not be accessible from other systems")
        
        if '@' in url and ':' in url.split('@')[0]:
            warnings.append("URL appears to contain credentials - consider using secure authentication")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Polygon validation
    @staticmethod
    def validate_polygon(points: List[GeoPoint]) -> ValidationResult:
        """Validate a geographic polygon"""
        errors = []
        warnings = []
        
        if len(points) < 3:
            errors.append("Polygon must have at least 3 points")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check if polygon is closed
        first = points[0]
        last = points[-1]
        if first.lat != last.lat or first.lng != last.lng:
            warnings.append("Polygon is not closed - first and last points should match")
        
        # Validate each point
        for i, point in enumerate(points):
            coord_result = ValidationEngine.validate_coordinates(point.lat, point.lng)
            if not coord_result.is_valid:
                errors.extend([f"Point {i+1}: {e}" for e in coord_result.errors])
        
        # Check for self-intersection (simplified check)
        if len(points) > 4:
            # Basic check for obviously invalid polygons
            pass
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Polygon overlap validation
    @staticmethod
    def validate_no_overlap(new_polygon: List[GeoPoint], existing_polygons: List[List[GeoPoint]]) -> ValidationResult:
        """Check if a new polygon overlaps with existing polygons"""
        errors = []
        warnings = []
        
        # Simplified overlap check using bounding boxes
        def get_bounds(polygon: List[GeoPoint]) -> Tuple[float, float, float, float]:
            lats = [p.lat for p in polygon]
            lngs = [p.lng for p in polygon]
            return min(lats), max(lats), min(lngs), max(lngs)
        
        new_bounds = get_bounds(new_polygon)
        
        for i, existing in enumerate(existing_polygons):
            existing_bounds = get_bounds(existing)
            
            # Check bounding box overlap
            if not (new_bounds[1] < existing_bounds[0] or  # new max lat < existing min lat
                    new_bounds[0] > existing_bounds[1] or  # new min lat > existing max lat
                    new_bounds[3] < existing_bounds[2] or  # new max lng < existing min lng
                    new_bounds[2] > existing_bounds[3]):   # new min lng > existing max lng
                warnings.append(f"Polygon may overlap with existing polygon {i+1}")
        
        return ValidationResult(is_valid=True, errors=errors, warnings=warnings)
    
    # Camera validation
    @staticmethod
    def validate_camera(data: Dict[str, Any]) -> ValidationResult:
        """Validate camera data"""
        errors = []
        warnings = []
        
        # Validate coordinates
        if 'lat' in data and 'lng' in data:
            coord_result = ValidationEngine.validate_coordinates(data['lat'], data['lng'])
            errors.extend(coord_result.errors)
        
        # Validate stream URL
        if 'stream_url' in data and data['stream_url']:
            url_result = ValidationEngine.validate_stream_url(data['stream_url'])
            errors.extend(url_result.errors)
            warnings.extend(url_result.warnings)
        
        # Validate fallback URL
        if 'fallback_url' in data and data['fallback_url']:
            url_result = ValidationEngine.validate_stream_url(data['fallback_url'])
            errors.extend([f"Fallback URL: {e}" for e in url_result.errors])
            warnings.extend([f"Fallback URL: {w}" for w in url_result.warnings])
        
        # Validate name
        if 'name' in data:
            if len(data['name']) < 1:
                errors.append("Camera name is required")
            elif len(data['name']) > 200:
                errors.append("Camera name must be 200 characters or less")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Drone/Robot telemetry validation
    @staticmethod
    def validate_telemetry(data: Dict[str, Any]) -> ValidationResult:
        """Validate drone/robot telemetry data"""
        errors = []
        warnings = []
        
        # Validate battery
        if 'battery_level' in data:
            battery = data['battery_level']
            if battery < 0 or battery > 100:
                errors.append("Battery level must be between 0 and 100")
            elif battery < 20:
                warnings.append("Battery level is critically low")
            elif battery < 40:
                warnings.append("Battery level is low")
        
        # Validate battery count
        if 'battery_count' in data:
            if data['battery_count'] < 1:
                errors.append("Battery count must be at least 1")
        
        # Validate max flight time
        if 'max_flight_time' in data:
            if data['max_flight_time'] < 1 or data['max_flight_time'] > 120:
                errors.append("Max flight time must be between 1 and 120 minutes")
        
        # Validate coordinates if present
        if 'current_lat' in data and 'current_lng' in data:
            if data['current_lat'] is not None and data['current_lng'] is not None:
                coord_result = ValidationEngine.validate_coordinates(data['current_lat'], data['current_lng'])
                errors.extend(coord_result.errors)
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Sector validation
    @staticmethod
    def validate_sector(data: Dict[str, Any], existing_sectors: Optional[List[Dict]] = None) -> ValidationResult:
        """Validate sector data"""
        errors = []
        warnings = []
        
        # Validate polygon
        if 'polygon' in data and data['polygon']:
            polygon_result = ValidationEngine.validate_polygon(data['polygon'])
            errors.extend(polygon_result.errors)
            warnings.extend(polygon_result.warnings)
            
            # Check for overlap with existing sectors
            if existing_sectors and polygon_result.is_valid:
                existing_polygons = [s['polygon'] for s in existing_sectors if 'polygon' in s]
                overlap_result = ValidationEngine.validate_no_overlap(data['polygon'], existing_polygons)
                warnings.extend(overlap_result.warnings)
        
        # Validate sector ID format
        if 'sector_id' in data:
            if not re.match(r'^[A-Z0-9\-]+$', data['sector_id']):
                warnings.append("Sector ID should use uppercase letters, numbers, and hyphens only")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Fire preplan validation
    @staticmethod
    def validate_fire_preplan(data: Dict[str, Any]) -> ValidationResult:
        """Validate fire preplan data"""
        errors = []
        warnings = []
        
        # Validate required fields
        if not data.get('building_name'):
            errors.append("Building name is required")
        
        if not data.get('address'):
            errors.append("Address is required")
        
        # Validate PDF URL if provided
        if 'pdf_url' in data and data['pdf_url']:
            if not data['pdf_url'].lower().endswith('.pdf'):
                warnings.append("PDF URL should end with .pdf extension")
        
        # Validate coordinates if provided
        if 'lat' in data and 'lng' in data:
            if data['lat'] is not None and data['lng'] is not None:
                coord_result = ValidationEngine.validate_coordinates(data['lat'], data['lng'])
                errors.extend(coord_result.errors)
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # DV Risk Home validation - CRITICAL SECURITY
    @staticmethod
    def validate_dv_risk_home(data: Dict[str, Any]) -> ValidationResult:
        """Validate DV risk home data - enforces address redaction"""
        errors = []
        warnings = []
        
        # CRITICAL: Check for address-like data in sector field
        if 'sector' in data:
            sector = data['sector'].lower()
            address_indicators = ['st', 'street', 'ave', 'avenue', 'blvd', 'boulevard', 
                                  'rd', 'road', 'dr', 'drive', 'ln', 'lane', 'way', 'ct', 'court']
            
            for indicator in address_indicators:
                if indicator in sector and any(c.isdigit() for c in sector):
                    errors.append("SECURITY VIOLATION: Full addresses are not allowed. Use sector ID only (e.g., SECTOR-1)")
                    break
        
        # Check for PII in notes
        if 'notes' in data and data['notes']:
            notes = data['notes'].lower()
            # Check for phone numbers
            if re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', notes):
                warnings.append("Notes may contain phone number - ensure this is necessary")
            # Check for SSN patterns
            if re.search(r'\d{3}[-.\s]?\d{2}[-.\s]?\d{4}', notes):
                errors.append("SECURITY VIOLATION: Notes appear to contain SSN - remove immediately")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # School validation
    @staticmethod
    def validate_school(data: Dict[str, Any]) -> ValidationResult:
        """Validate school data"""
        errors = []
        warnings = []
        
        # Validate required fields
        if not data.get('school_name'):
            errors.append("School name is required")
        
        if not data.get('address'):
            errors.append("Address is required")
        
        # Validate perimeter polygon if provided
        if 'perimeter' in data and data['perimeter']:
            polygon_result = ValidationEngine.validate_polygon(data['perimeter'])
            errors.extend([f"Perimeter: {e}" for e in polygon_result.errors])
            warnings.extend([f"Perimeter: {w}" for w in polygon_result.warnings])
        
        # Validate access points
        if 'access_points' in data and data['access_points']:
            for i, ap in enumerate(data['access_points']):
                if 'lat' in ap and 'lng' in ap:
                    coord_result = ValidationEngine.validate_coordinates(ap['lat'], ap['lng'])
                    errors.extend([f"Access point {i+1}: {e}" for e in coord_result.errors])
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Event validation
    @staticmethod
    def validate_event(data: Dict[str, Any]) -> ValidationResult:
        """Validate event data"""
        errors = []
        warnings = []
        
        # Validate required fields
        if not data.get('event_name'):
            errors.append("Event name is required")
        
        # Validate boundary polygon
        if 'boundary' in data and data['boundary']:
            polygon_result = ValidationEngine.validate_polygon(data['boundary'])
            errors.extend([f"Boundary: {e}" for e in polygon_result.errors])
            warnings.extend([f"Boundary: {w}" for w in polygon_result.warnings])
        else:
            errors.append("Event boundary polygon is required")
        
        # Validate time range
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] and data['end_time']:
                if data['end_time'] <= data['start_time']:
                    errors.append("End time must be after start time")
        else:
            errors.append("Start time and end time are required")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # API Connection validation
    @staticmethod
    def validate_api_connection(data: Dict[str, Any]) -> ValidationResult:
        """Validate API connection data"""
        errors = []
        warnings = []
        
        # Validate URL
        if 'url' in data and data['url']:
            if not data['url'].startswith(('http://', 'https://')):
                errors.append("URL must start with http:// or https://")
            
            if 'http://' in data['url'] and 'localhost' not in data['url'].lower():
                warnings.append("Using HTTP instead of HTTPS - connection may not be secure")
        else:
            errors.append("API URL is required")
        
        # Validate API name
        if not data.get('api_name'):
            errors.append("API name is required")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    # Generic validation dispatcher
    @staticmethod
    def validate(entity_type: str, data: Dict[str, Any], **kwargs) -> ValidationResult:
        """Dispatch validation to appropriate validator"""
        validators = {
            'camera': ValidationEngine.validate_camera,
            'drone': ValidationEngine.validate_telemetry,
            'robot': ValidationEngine.validate_telemetry,
            'sector': lambda d: ValidationEngine.validate_sector(d, kwargs.get('existing_sectors')),
            'fire_preplan': ValidationEngine.validate_fire_preplan,
            'dv_risk_home': ValidationEngine.validate_dv_risk_home,
            'school': ValidationEngine.validate_school,
            'event': ValidationEngine.validate_event,
            'api_connection': ValidationEngine.validate_api_connection,
        }
        
        validator = validators.get(entity_type)
        if validator:
            return validator(data)
        
        return ValidationResult(is_valid=True)
