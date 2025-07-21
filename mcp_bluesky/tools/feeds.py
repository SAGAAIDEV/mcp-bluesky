"""Feed operations tools for Bluesky MCP server.

Tools for retrieving timelines, author feeds, and post threads.
"""

from typing import Dict, Optional

from mcp.server.fastmcp import Context

from ..client import get_authenticated_client


def get_timeline(
    ctx: Context,
    algorithm: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict:
    """Get posts from your home timeline.

    Args:
        ctx: MCP context
        algorithm: Optional algorithm to use for timeline
        cursor: Optional pagination cursor
        limit: Maximum number of results to return

    Returns:
        Timeline feed with posts
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        timeline_response = bluesky_client.get_timeline(algorithm, cursor, limit)

        # Convert the response to a dictionary
        if hasattr(timeline_response, "model_dump"):
            timeline_data = timeline_response.model_dump()
        else:
            timeline_data = timeline_response

        return {"status": "success", "timeline": timeline_data}
    except Exception as e:
        error_msg = f"Failed to get timeline: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_author_feed(
    ctx: Context,
    actor: str,
    cursor: Optional[str] = None,
    filter: Optional[str] = None,
    limit: Optional[int] = None,
    include_pins: bool = False,
) -> Dict:
    """Get posts from a specific user.

    Args:
        ctx: MCP context
        actor: Handle or DID of the user
        cursor: Optional pagination cursor
        filter: Optional filter for post types
        limit: Maximum number of results to return
        include_pins: Whether to include pinned posts

    Returns:
        Feed with posts from the specified user
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        feed_response = bluesky_client.get_author_feed(
            actor, cursor, filter, limit, include_pins
        )

        # Convert the response to a dictionary
        if hasattr(feed_response, "model_dump"):
            feed_data = feed_response.model_dump()
        else:
            feed_data = feed_response

        return {"status": "success", "feed": feed_data}
    except Exception as e:
        error_msg = f"Failed to get author feed: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_post_thread(
    ctx: Context,
    uri: str,
    depth: Optional[int] = None,
    parent_height: Optional[int] = None,
) -> Dict:
    """Get a full conversation thread.

    Args:
        ctx: MCP context
        uri: URI of the post to get thread for
        depth: How many levels of replies to include
        parent_height: How many parent posts to include

    Returns:
        Thread with the post and its replies/parents
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        thread_response = bluesky_client.get_post_thread(uri, depth, parent_height)

        # Convert the response to a dictionary
        if hasattr(thread_response, "model_dump"):
            thread_data = thread_response.model_dump()
        else:
            thread_data = thread_response

        return {"status": "success", "thread": thread_data}
    except Exception as e:
        error_msg = f"Failed to get post thread: {str(e)}"
        return {"status": "error", "message": error_msg}


def register_feed_tools(mcp):
    """Register feed tools with the MCP server."""
    mcp.tool()(get_timeline)
    mcp.tool()(get_author_feed)
    mcp.tool()(get_post_thread)