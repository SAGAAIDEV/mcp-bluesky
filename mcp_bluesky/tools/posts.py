"""Post management tools for Bluesky MCP server.

Tools for sending, retrieving, and deleting posts.
"""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context

from ..client import get_authenticated_client


def send_post(
    ctx: Context,
    text: str,
    profile_identify: Optional[str] = None,
    reply_to: Optional[Dict[str, Any]] = None,
    embed: Optional[Dict[str, Any]] = None,
    langs: Optional[List[str]] = None,
    facets: Optional[List[Dict[str, Any]]] = None,
) -> Dict:
    """Send a post to Bluesky.

    Args:
        ctx: MCP context
        text: Text content of the post
        profile_identify: Optional handle or DID. Where to send post. If not provided, sends to current profile
        reply_to: Optional reply reference with 'root' and 'parent' containing 'uri' and 'cid'
        embed: Optional embed object (images, external links, records, or video)
        langs: Optional list of language codes used in the post (defaults to ['en'])
        facets: Optional list of rich text facets (mentions, links, etc.)

    Returns:
        Status of the post creation with uri and cid of the created post
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # Prepare parameters for send_post
        kwargs: Dict[str, Any] = {"text": text}

        # Add optional parameters if provided
        if profile_identify:
            kwargs["profile_identify"] = profile_identify

        if reply_to:
            kwargs["reply_to"] = reply_to

        if embed:
            kwargs["embed"] = embed

        if langs:
            kwargs["langs"] = langs

        if facets:
            kwargs["facets"] = facets

        # Create the post using the native send_post method
        post_response = bluesky_client.send_post(**kwargs)

        return {
            "status": "success",
            "message": "Post sent successfully",
            "post_uri": post_response.uri,
            "post_cid": post_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to send post: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_post(
    ctx: Context,
    post_rkey: str,
    profile_identify: Optional[str] = None,
    cid: Optional[str] = None,
) -> Dict:
    """Get a specific post.

    Args:
        ctx: MCP context
        post_rkey: The record key of the post
        profile_identify: Handle or DID of the post author
        cid: Optional CID of the post

    Returns:
        The requested post
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        post_response = bluesky_client.get_post(post_rkey, profile_identify, cid)

        # Convert the response to a dictionary
        if hasattr(post_response, "model_dump"):
            post_data = post_response.model_dump()
        else:
            post_data = post_response

        return {"status": "success", "post": post_data}
    except Exception as e:
        error_msg = f"Failed to get post: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_posts(
    ctx: Context,
    uris: List[str],
) -> Dict:
    """Get multiple posts by their URIs.

    Args:
        ctx: MCP context
        uris: List of post URIs to retrieve

    Returns:
        List of requested posts
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        posts_response = bluesky_client.get_posts(uris)

        # Convert the response to a dictionary
        if hasattr(posts_response, "model_dump"):
            posts_data = posts_response.model_dump()
        else:
            posts_data = posts_response

        return {"status": "success", "posts": posts_data}
    except Exception as e:
        error_msg = f"Failed to get posts: {str(e)}"
        return {"status": "error", "message": error_msg}


def delete_post(
    ctx: Context,
    uri: str,
) -> Dict:
    """Delete a post created by the authenticated user.

    Args:
        ctx: MCP context
        uri: URI of the post to delete

    Returns:
        Status of the delete operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)
        # Delete the post
        bluesky_client.delete_post(uri)

        return {
            "status": "success",
            "message": "Post deleted successfully",
        }
    except Exception as e:
        error_msg = f"Failed to delete post: {str(e)}"
        return {"status": "error", "message": error_msg}


def register_post_tools(mcp):
    """Register post tools with the MCP server."""
    mcp.tool()(send_post)
    mcp.tool()(get_post)
    mcp.tool()(get_posts)
    mcp.tool()(delete_post)