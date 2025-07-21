"""MCP context management utilities.

Handles application context lifecycle and utilities.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from .client import login
from .types import AppContext


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with typed context.

    Args:
        server: The FastMCP server instance

    Yields:
        AppContext with initialized resources
    """
    # Initialize resources - login may return None if credentials not available
    bluesky_client = login()
    try:
        yield AppContext(bluesky_client=bluesky_client)
    finally:
        # Clean up resources if needed
        pass