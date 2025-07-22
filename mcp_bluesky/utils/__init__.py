"""Utility modules for Bluesky MCP Server.

This package contains utility modules for various aspects of the server:
- validation: Input validation framework  
- rate_limiting: Rate limiting framework
- media_utils: Media processing utilities
- decorators: Common decorators and base classes
"""

# Import commonly used functions for easy access
from .validation import (
    validate_text_length,
    validate_file_size,
    validate_handle,
    InputValidator,
    ValidationError
)

from .rate_limiting import (
    RateLimitError,
    BlueskyRateLimiter, 
    get_rate_limiter,
    rate_limit
)

from .media_utils import (
    MediaInfo,
    MediaProcessor,
    is_supported_media_type,
    process_image_upload,
    process_video_upload
)

from .decorators import (
    handle_errors,
    validate_input,
    rate_limit,
    require_auth,
    comprehensive_tool_decorator,
    ToolMixin
)

__all__ = [
    # Validation
    'validate_text_length',
    'validate_file_size', 
    'validate_handle',
    'InputValidator',
    'ValidationError',
    
    # Rate Limiting
    'RateLimitError',
    'BlueskyRateLimiter',
    'get_rate_limiter',
    'rate_limit',
    
    # Media Utils
    'MediaInfo',
    'MediaProcessor',
    'is_supported_media_type',
    'process_image_upload',
    'process_video_upload',
    
    # Decorators
    'handle_errors',
    'validate_input', 
    'require_auth',
    'comprehensive_tool_decorator',
    'ToolMixin'
]