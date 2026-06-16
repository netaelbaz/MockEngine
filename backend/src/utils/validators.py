"""Validation utilities for MockEngine."""

import re
import json
from typing import Dict, Any, Optional, List, Tuple


def validate_url_pattern(url_pattern: str) -> bool:
    """
    Validate a URL pattern.

    Supports:
    - Simple path patterns: /api/users, /user/profile
    - Wildcard patterns: /api/*, /user/*
    - Regex patterns (basic)

    Args:
        url_pattern: URL pattern string to validate

    Returns:
        bool: True if pattern is valid, False otherwise
    """
    if not url_pattern or not isinstance(url_pattern, str):
        return False

    # Must start with /
    if not url_pattern.startswith('/'):
        return False

    # Basic validation - allow alphanumeric, /, -, _, *, ?, and regex chars
    # This is a simple validation, not a full regex check
    try:
        # Check if it looks like a reasonable URL pattern
        # Allow common path characters
        valid_pattern = r'^[a-zA-Z0-9_\-/.*?+(){}\[\]|^$]+$'
        return bool(re.match(valid_pattern, url_pattern))
    except re.error:
        return False


def validate_json_string(json_string: str) -> bool:
    """
    Validate if a string is valid JSON.

    Args:
        json_string: String to validate

    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError, ValueError):
        return False


def validate_mock_data(mock_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate mock data structure.

    Args:
        mock_data: Dictionary containing mock response data

    Returns:
        Tuple: (is_valid, error_message)
    """
    if not isinstance(mock_data, dict):
        return False, "Mock data must be a dictionary/object"

    # Could add more specific validation here
    # For now, just check it's a valid JSON-serializable object
    try:
        json.dumps(mock_data)
        return True, None
    except (TypeError, ValueError) as e:
        return False, f"Mock data is not JSON-serializable: {str(e)}"


def validate_status_code(status_code: int) -> bool:
    """
    Validate HTTP status code.

    Args:
        status_code: HTTP status code to validate

    Returns:
        bool: True if valid status code, False otherwise
    """
    return 100 <= status_code <= 599


def validate_http_method(method: str) -> bool:
    """
    Validate HTTP method.

    Args:
        method: HTTP method string

    Returns:
        bool: True if valid HTTP method, False otherwise
    """
    valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE'}
    return method.upper() in valid_methods


def validate_device_id(device_id: str) -> bool:
    """
    Validate device ID format.

    Device IDs should be non-empty strings.

    Args:
        device_id: Device ID string to validate

    Returns:
        bool: True if valid device ID, False otherwise
    """
    if not device_id or not isinstance(device_id, str):
        return False

    # Device ID should be at least 1 character and max 255
    if len(device_id) < 1 or len(device_id) > 255:
        return False

    return True


def validate_internet_mode(internet_mode: str) -> bool:
    """
    Validate internet mode value.

    Args:
        internet_mode: Internet mode string to validate

    Returns:
        bool: True if valid internet mode, False otherwise
    """
    valid_modes = {'wifi', 'cellular', 'none'}
    return internet_mode.lower() in valid_modes


def sanitize_string(input_string: str, max_length: int = 255) -> str:
    """
    Sanitize a string input.

    Args:
        input_string: String to sanitize
        max_length: Maximum length for the string

    Returns:
        str: Sanitized string
    """
    if not isinstance(input_string, str):
        input_string = str(input_string)

    # Strip whitespace
    sanitized = input_string.strip()

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_rule_mode(mode: str) -> bool:
    """
    Validate rule mode.

    Args:
        mode: Rule mode string to validate

    Returns:
        bool: True if valid rule mode, False otherwise
    """
    valid_modes = {'always', 'user_controlled', 'percentage'}
    return mode.lower() in valid_modes
