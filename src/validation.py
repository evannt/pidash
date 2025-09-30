"""
Input validation and sanitization utilities for PiDash.

Provides comprehensive validation for user inputs, file uploads,
and configuration values to prevent security issues and data corruption.
"""

from src.constants import VALID_ORIENTATIONS, MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_orientation(orientation: str) -> str:
    """
    Validate orientation value.
    
    Args:
        orientation: Orientation string to validate
        
    Returns:
        str: Valid orientation
        
    Raises:
        ValidationError: If orientation is invalid
    """
    if not orientation:
        raise ValidationError("Orientation cannot be empty")
    
    orientation = orientation.lower().strip()
    if orientation not in VALID_ORIENTATIONS:
        raise ValidationError(f"Invalid orientation. Must be one of: {', '.join(VALID_ORIENTATIONS)}")
    
    return orientation


def validate_refresh_interval(interval) -> int:
    """
    Validate refresh interval value.
    
    Args:
        interval: Refresh interval to validate
        
    Returns:
        int: Valid refresh interval in seconds
        
    Raises:
        ValidationError: If interval is invalid
    """
    try:
        interval = int(interval)
    except (ValueError, TypeError):
        raise ValidationError("Refresh interval must be a number")
    
    if interval < MIN_REFRESH_INTERVAL:
        raise ValidationError(f"Refresh interval too small (minimum: {MIN_REFRESH_INTERVAL} seconds)")
    
    if interval > MAX_REFRESH_INTERVAL:
        raise ValidationError(f"Refresh interval too large (maximum: {MAX_REFRESH_INTERVAL} seconds)")
    
    return interval