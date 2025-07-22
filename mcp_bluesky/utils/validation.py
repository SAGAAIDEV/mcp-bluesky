"""Input validation framework for Bluesky MCP Server.

This module provides validation functions for various input types.
Framework ready for Phase 1 implementation.
"""

from typing import Any, Optional, List
import re


def validate_text_length(text: str, max_length: int = 300) -> None:
    """Validate text length against Bluesky limits.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed character count (default: 300 for posts)
        
    Raises:
        ValueError: If text exceeds the maximum length
        
    Note:
        To be fully implemented in Phase 1.
    """
    # Basic validation for now - to be enhanced in Phase 1
    if len(text) > max_length:
        raise ValueError(f"Text exceeds {max_length} character limit")


def validate_file_size(data: bytes, max_size: int = 1048576) -> None:
    """Validate file size limits.
    
    Args:
        data: File data as bytes
        max_size: Maximum allowed size in bytes (default: 1MB)
        
    Raises:
        ValueError: If file exceeds the maximum size
        
    Note:
        To be fully implemented in Phase 1.
    """
    # Basic validation for now - to be enhanced in Phase 1
    if len(data) > max_size:
        raise ValueError(f"File size exceeds {max_size} bytes")


def validate_handle(handle: str) -> str:
    """Validate and normalize Bluesky handle format.
    
    Args:
        handle: User handle to validate
        
    Returns:
        Normalized handle
        
    Raises:
        ValueError: If handle format is invalid
        
    Note:
        To be fully implemented in Phase 1.
    """
    # Basic validation for now - to be enhanced in Phase 1
    if not handle:
        raise ValueError("Handle cannot be empty")
    
    # Remove @ prefix if present
    if handle.startswith('@'):
        handle = handle[1:]
    
    # Basic format check - to be enhanced
    if not re.match(r'^[a-zA-Z0-9\.\-_]+$', handle):
        raise ValueError("Invalid handle format")
    
    return handle


def validate_uri(uri: str) -> str:
    """Validate AT Protocol URI format.
    
    Args:
        uri: AT URI to validate
        
    Returns:
        Validated URI
        
    Raises:
        ValueError: If URI format is invalid
        
    Note:
        To be fully implemented in Phase 1.
    """
    # Basic validation for now - to be enhanced in Phase 1
    if not uri:
        raise ValueError("URI cannot be empty")
    
    if not uri.startswith('at://'):
        raise ValueError("URI must start with 'at://'")
    
    return uri


def validate_media_format(filename: str, allowed_formats: Optional[List[str]] = None) -> bool:
    """Validate media file format.
    
    Args:
        filename: Name of the media file
        allowed_formats: List of allowed file extensions
        
    Returns:
        True if format is valid
        
    Raises:
        ValueError: If format is not allowed
        
    Note:
        To be fully implemented in Phase 1.
    """
    if allowed_formats is None:
        allowed_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov']
    
    # Basic validation for now - to be enhanced in Phase 1
    file_ext = filename.lower().split('.')[-1]
    if f'.{file_ext}' not in allowed_formats:
        raise ValueError(f"File format .{file_ext} not allowed. Allowed formats: {allowed_formats}")
    
    return True


def sanitize_input(text: str) -> str:
    """Sanitize input text for safe processing.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
        
    Note:
        To be fully implemented in Phase 1.
    """
    # Basic sanitization for now - to be enhanced in Phase 1
    if not isinstance(text, str):
        text = str(text)
    
    # Remove null bytes and control characters (basic implementation)
    sanitized = text.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
    
    return sanitized.strip()


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Input validation framework class.
    
    Provides centralized validation for various input types.
    To be expanded in Phase 1.
    """
    
    def __init__(self):
        self.max_post_length = 300
        self.max_file_size = 1048576  # 1MB
    
    def validate_post_content(self, content: str) -> str:
        """Validate post content."""
        content = sanitize_input(content)
        validate_text_length(content, self.max_post_length)
        return content
    
    def validate_media_upload(self, data: bytes, filename: str) -> bool:
        """Validate media upload."""
        validate_file_size(data, self.max_file_size)
        validate_media_format(filename)
        return True
    
    def validate_user_handle(self, handle: str) -> str:
        """Validate user handle."""
        return validate_handle(handle)