"""Bluesky client management.

Handles client creation, authentication, and lifecycle management.
"""

from typing import Optional

from atproto import Client
from mcp.server.fastmcp import Context

from .config import (
    get_bluesky_identifier,
    get_bluesky_app_password,
    get_bluesky_service_url
)
from .types import AppContext


def login() -> Optional[Client]:
    """Login to Bluesky API and return the client.

    Authenticates using environment variables:
    - BLUESKY_IDENTIFIER: The handle (username)
    - BLUESKY_APP_PASSWORD: The app password
    - BLUESKY_SERVICE_URL: The service URL (defaults to "https://bsky.social")

    Returns:
        Authenticated Client instance or None if credentials are not available
    """
    handle = get_bluesky_identifier()
    password = get_bluesky_app_password()
    service_url = get_bluesky_service_url()

    if not handle or not password:
        return None

    # This is helpful for debugging.
    # print(f"LOGIN {handle=} {service_url=}", file=sys.stderr)

    # Create and authenticate client
    client = Client(service_url)
    client.login(handle, password)
    return client


def get_authenticated_client(ctx: Context) -> Client:
    """Get an authenticated client, creating it lazily if needed.

    Args:
        ctx: The MCP context

    Returns:
        Authenticated Bluesky client

    Raises:
        ValueError: If credentials are not available
    """
    # Get the app context (created during app startup)
    app_context: AppContext = ctx.request_context.lifespan_context

    # If we already have a client in the context, return it
    if app_context.bluesky_client is not None:
        return app_context.bluesky_client

    # Otherwise, try to create one
    client = login()
    if client is None:
        raise ValueError(
            "Authentication required but credentials not available. "
            "Please set BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD environment variables."
        )

    # Store it in the context for future use
    app_context.bluesky_client = client
    return client