"""Configuration management for Bluesky MCP Server.

Handles environment variables and configuration validation.
"""

import os
from pathlib import Path
from typing import Optional


# Project root for logging and other paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
LOG_FILE = PROJECT_ROOT / "custom-mcp.log"

# Default service URL
DEFAULT_SERVICE_URL = "https://bsky.social"


def get_bluesky_identifier() -> Optional[str]:
    """Get Bluesky identifier from environment."""
    return os.environ.get("BLUESKY_IDENTIFIER")


def get_bluesky_app_password() -> Optional[str]:
    """Get Bluesky app password from environment."""
    return os.environ.get("BLUESKY_APP_PASSWORD")


def get_bluesky_service_url() -> str:
    """Get Bluesky service URL from environment, with default fallback."""
    return os.environ.get("BLUESKY_SERVICE_URL", DEFAULT_SERVICE_URL)


def has_required_credentials() -> bool:
    """Check if required Bluesky credentials are available."""
    return bool(get_bluesky_identifier() and get_bluesky_app_password())


def validate_configuration() -> dict:
    """Validate configuration and return status."""
    identifier = get_bluesky_identifier()
    password = get_bluesky_app_password()
    service_url = get_bluesky_service_url()
    
    return {
        "has_identifier": bool(identifier),
        "has_password": bool(password),
        "service_url": service_url,
        "is_configured": bool(identifier and password)
    }