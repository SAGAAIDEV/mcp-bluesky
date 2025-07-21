"""Post interaction tools for Bluesky MCP server.

Tools for liking, unliking, reposting, and other post interactions.
"""

from typing import Dict, Optional, Union

from mcp.server.fastmcp import Context

from ..client import get_authenticated_client


def like_post(
    ctx: Context,
    uri: str,
    cid: str,
) -> Dict:
    """Like a post.

    Args:
        ctx: MCP context
        uri: URI of the post to like
        cid: CID of the post to like

    Returns:
        Status of the like operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        like_response = bluesky_client.like(uri, cid)
        return {
            "status": "success",
            "message": "Post liked successfully",
            "like_uri": like_response.uri,
            "like_cid": like_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to like post: {str(e)}"
        return {"status": "error", "message": error_msg}


def unlike_post(
    ctx: Context,
    like_uri: str,
) -> Dict:
    """Unlike a previously liked post.

    Args:
        ctx: MCP context
        like_uri: URI of the like.

    Returns:
        Status of the unlike operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        bluesky_client.unlike(like_uri)
        return {
            "status": "success",
            "message": "Post unliked successfully",
        }
    except Exception as e:
        error_msg = f"Failed to unlike post: {str(e)}"
        return {"status": "error", "message": error_msg}


def repost(
    ctx: Context,
    uri: str,
    cid: str,
) -> Dict:
    """Repost another user's post.

    Args:
        ctx: MCP context
        uri: URI of the post to repost
        cid: CID of the post to repost

    Returns:
        Status of the repost operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        repost_response = bluesky_client.repost(uri, cid)
        return {
            "status": "success",
            "message": "Post reposted successfully",
            "repost_uri": repost_response.uri,
            "repost_cid": repost_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to repost: {str(e)}"
        return {"status": "error", "message": error_msg}


def unrepost(
    ctx: Context,
    repost_uri: str,
) -> Dict:
    """Remove a repost of another user's post.

    Args:
        ctx: MCP context
        repost_uri: URI of the repost to remove

    Returns:
        Status of the unrepost operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        success = bluesky_client.unrepost(repost_uri)

        if success:
            return {
                "status": "success",
                "message": "Repost removed successfully",
            }
        else:
            return {
                "status": "error",
                "message": "Failed to remove repost",
            }
    except Exception as e:
        error_msg = f"Failed to unrepost: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_likes(
    ctx: Context,
    uri: str,
    cid: Optional[str] = None,
    limit: Union[int, str] = 50,
    cursor: Optional[str] = None,
) -> Dict:
    """Get likes for a post.

    Args:
        ctx: MCP context
        uri: URI of the post to get likes for
        cid: Optional CID of the post (not strictly required)
        limit: Maximum number of results to return (1-100)
        cursor: Optional pagination cursor

    Returns:
        List of likes for the post
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        params = {"uri": uri, "limit": max(1, min(100, limit))}
        if cursor:
            params["cursor"] = cursor

        likes_response = bluesky_client.get_likes(**params)
        likes_data = likes_response.dict()

        return {"status": "success", "likes": likes_data}
    except Exception as e:
        error_msg = f"Failed to get likes: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_reposted_by(
    ctx: Context,
    uri: str,
    cid: Optional[str] = None,
    limit: Union[int, str] = 50,
    cursor: Optional[str] = None,
) -> Dict:
    """Get users who reposted a post.

    Args:
        ctx: MCP context
        uri: URI of the post to get reposts for
        cid: Optional CID of the post (not strictly required)
        limit: Maximum number of results to return (1-100)
        cursor: Optional pagination cursor

    Returns:
        List of users who reposted the post
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # Convert limit to int if it's a string
        if isinstance(limit, str):
            limit = int(limit)
        limit = max(1, min(100, limit))

        # Call get_reposted_by with positional arguments as per the client signature
        reposts_response = bluesky_client.get_reposted_by(uri, cid, cursor, limit)
        reposts_data = reposts_response.dict()

        return {"status": "success", "reposts": reposts_data}
    except Exception as e:
        error_msg = f"Failed to get reposts: {str(e)}"
        return {"status": "error", "message": error_msg}


def register_interaction_tools(mcp):
    """Register interaction tools with the MCP server."""
    mcp.tool()(like_post)
    mcp.tool()(unlike_post)
    mcp.tool()(repost)
    mcp.tool()(unrepost)
    mcp.tool()(get_likes)
    mcp.tool()(get_reposted_by)