"""
Input validation and sanitization utilities for PiDash.

Provides comprehensive validation for user inputs, file uploads,
and configuration values to prevent security issues and data corruption.
"""

import re
import os
from typing import Any, Optional, Tuple, List
from src.constants import VALID_ORIENTATIONS, MIN_REFRESH_INTERVAL, MAX_REFRESH_INTERVAL


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
        
    Raises:
        ValidationError: If filename contains dangerous characters
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(f"Filename contains dangerous character: {char}")
    
    if len(filename) > 255:
        raise ValidationError("Filename too long (max 255 characters)")
    
    return filename.strip()


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


def validate_refresh_interval(interval: Any) -> int:
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


def validate_image_settings(settings: dict) -> dict:
    """
    Validate image enhancement settings.
    
    Args:
        settings: Dictionary of image settings
        
    Returns:
        dict: Validated and sanitized settings
        
    Raises:
        ValidationError: If settings are invalid
    """
    if not isinstance(settings, dict):
        raise ValidationError("Image settings must be a dictionary")
    
    validated_settings = {}
    
    # Validate brightness
    if 'brightness' in settings:
        try:
            brightness = float(settings['brightness'])
            if not 0.0 <= brightness <= 2.0:
                raise ValidationError("Brightness must be between 0.0 and 2.0")
            validated_settings['brightness'] = brightness
        except (ValueError, TypeError):
            raise ValidationError("Brightness must be a number")
    
    # Validate contrast
    if 'contrast' in settings:
        try:
            contrast = float(settings['contrast'])
            if not 0.0 <= contrast <= 2.0:
                raise ValidationError("Contrast must be between 0.0 and 2.0")
            validated_settings['contrast'] = contrast
        except (ValueError, TypeError):
            raise ValidationError("Contrast must be a number")
    
    # Validate saturation
    if 'saturation' in settings:
        try:
            saturation = float(settings['saturation'])
            if not 0.0 <= saturation <= 2.0:
                raise ValidationError("Saturation must be between 0.0 and 2.0")
            validated_settings['saturation'] = saturation
        except (ValueError, TypeError):
            raise ValidationError("Saturation must be a number")
    
    # Validate sharpness
    if 'sharpness' in settings:
        try:
            sharpness = float(settings['sharpness'])
            if not 0.0 <= sharpness <= 2.0:
                raise ValidationError("Sharpness must be between 0.0 and 2.0")
            validated_settings['sharpness'] = sharpness
        except (ValueError, TypeError):
            raise ValidationError("Sharpness must be a number")
    
    return validated_settings


def validate_path(path: str, allow_absolute: bool = False) -> str:
    """
    Validate and sanitize a file path.
    
    Args:
        path: Path to validate
        allow_absolute: Whether to allow absolute paths
        
    Returns:
        str: Validated path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError("Path cannot be empty")
    
    path = path.strip()
    
    if '..' in path:
        raise ValidationError("Path traversal not allowed")
    
    if not allow_absolute and os.path.isabs(path):
        raise ValidationError("Absolute paths not allowed")
    
    if len(path) > 4096:
        raise ValidationError("Path too long")
    
    return path


def validate_boolean(value: Any, field_name: str) -> bool:
    """
    Validate and convert a boolean value.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        bool: Validated boolean value
        
    Raises:
        ValidationError: If value cannot be converted to boolean
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    raise ValidationError(f"{field_name} must be a boolean value")


def validate_positive_integer(value: Any, field_name: str, max_value: Optional[int] = None) -> int:
    """
    Validate a positive integer value.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        max_value: Maximum allowed value
        
    Returns:
        int: Validated integer
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a number")
    
    if int_value < 0:
        raise ValidationError(f"{field_name} must be positive")
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(f"{field_name} must not exceed {max_value}")
    
    return int_value


def sanitize_string(value: Any, max_length: int = 1000) -> str:
    """
    Sanitize a string input.
    
    Args:
        value: Value to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized string
        
    Raises:
        ValidationError: If string is invalid
    """
    if value is None:
        return ""
    
    string_value = str(value).strip()
    
    if len(string_value) > max_length:
        raise ValidationError(f"String too long (max {max_length} characters)")
    
    # Remove potentially dangerous characters
    string_value = re.sub(r'[<>"\']', '', string_value)
    
    return string_value
