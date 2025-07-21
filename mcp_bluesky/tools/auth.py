"""Authentication tools for Bluesky MCP server.

Tools for checking authentication status and managing credentials.
"""

from mcp.server.fastmcp import Context

from ..client import get_authenticated_client


def check_auth_status(ctx: Context) -> str:
    """Check if the current session is authenticated.

    Authentication happens automatically using environment variables:
    - BLUESKY_IDENTIFIER: Required - your Bluesky handle
    - BLUESKY_APP_PASSWORD: Required - your app password
    - BLUESKY_SERVICE_URL: Optional - defaults to https://bsky.social

    Returns:
        Authentication status
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        return f"Authenticated to {bluesky_client._base_url}"
    except ValueError as e:
        return f"Not authenticated: {str(e)}"


def register_auth_tools(mcp):
    """Register authentication tools with the MCP server."""
    mcp.tool()(check_auth_status)