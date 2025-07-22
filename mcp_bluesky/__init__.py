"""Bluesky MCP Server Package.

A modular MCP server implementation for interacting with the Bluesky social network.

This package provides:
- Tools for Bluesky API operations (auth, posts, profiles, interactions, feeds, media)
- Utilities for validation, rate limiting, and media processing
- Configuration management with environment variables and YAML support
- Comprehensive error handling and logging infrastructure
"""

__version__ = "0.1.0"

# Main API exports
from .client import login, get_authenticated_client
from .config import (
    get_bluesky_identifier,
    get_bluesky_app_password, 
    get_bluesky_service_url,
    has_required_credentials,
    validate_configuration,
    Settings
)

__all__ = [
    "__version__",
    "login",
    "get_authenticated_client",
    "get_bluesky_identifier",
    "get_bluesky_app_password",
    "get_bluesky_service_url", 
    "has_required_credentials",
    "validate_configuration",
    "Settings"
]