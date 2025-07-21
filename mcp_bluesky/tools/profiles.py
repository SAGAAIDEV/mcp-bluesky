"""Profile operations tools for Bluesky MCP server.

Tools for managing user profiles, follows, followers, and user interactions.
"""

from typing import Dict, Optional, Union

from mcp.server.fastmcp import Context

from ..client import get_authenticated_client


def get_profile(ctx: Context, handle: Optional[str] = None) -> Dict:
    """Get a user profile.

    Args:
        ctx: MCP context
        handle: Optional handle to get profile for. If None, gets the authenticated user

    Returns:
        Profile data
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # If no handle provided, get authenticated user's profile
        if not handle:
            handle = bluesky_client.me.handle

        profile_response = bluesky_client.get_profile(handle)
        profile = profile_response.dict()
        return {"status": "success", "profile": profile}
    except Exception as e:
        error_msg = f"Failed to get profile: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_follows(
    ctx: Context,
    handle: Optional[str] = None,
    limit: Union[int, str] = 50,
    cursor: Optional[str] = None,
) -> Dict:
    """Get users followed by an account.

    Args:
        ctx: MCP context
        handle: Optional handle to get follows for. If None, gets the authenticated user
        limit: Maximum number of results to return (1-100)
        cursor: Optional pagination cursor

    Returns:
        List of followed accounts
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # If no handle provided, get authenticated user's follows
        if not handle:
            handle = bluesky_client.me.handle

        # Convert limit to int if it's a string
        if isinstance(limit, str):
            limit = int(limit)
        limit = max(1, min(100, limit))

        # Call get_follows directly with positional arguments as per the client signature
        follows_response = bluesky_client.get_follows(handle, cursor, limit)
        follows_data = follows_response.dict()

        return {"status": "success", "follows": follows_data}
    except Exception as e:
        error_msg = f"Failed to get follows: {str(e)}"
        return {"status": "error", "message": error_msg}


def get_followers(
    ctx: Context,
    handle: Optional[str] = None,
    limit: Union[int, str] = 50,
    cursor: Optional[str] = None,
) -> Dict:
    """Get users who follow an account.

    Args:
        ctx: MCP context
        handle: Optional handle to get followers for. If None, gets the authenticated user
        limit: Maximum number of results to return (1-100)
        cursor: Optional pagination cursor

    Returns:
        List of follower accounts
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # If no handle provided, get authenticated user's followers
        if not handle:
            handle = bluesky_client.me.handle

        # Convert limit to int if it's a string
        if isinstance(limit, str):
            limit = int(limit)
        limit = max(1, min(100, limit))

        # Call get_followers directly with positional arguments as per the client signature
        followers_response = bluesky_client.get_followers(handle, cursor, limit)
        followers_data = followers_response.dict()

        return {"status": "success", "followers": followers_data}
    except Exception as e:
        error_msg = f"Failed to get followers: {str(e)}"
        return {"status": "error", "message": error_msg}


def resolve_handle(
    ctx: Context,
    handle: str,
) -> Dict:
    """Resolve a handle to a DID.

    Args:
        ctx: MCP context
        handle: User handle to resolve (e.g. "user.bsky.social")

    Returns:
        Resolved DID information
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        resolved = bluesky_client.resolve_handle(handle)

        # Convert the response to a dictionary
        if hasattr(resolved, "model_dump"):
            resolved_data = resolved.model_dump()
        else:
            resolved_data = resolved

        return {
            "status": "success",
            "handle": handle,
            "did": resolved_data.get("did"),
        }
    except Exception as e:
        error_msg = f"Failed to resolve handle: {str(e)}"
        return {"status": "error", "message": error_msg}


def follow_user(
    ctx: Context,
    handle: str,
) -> Dict:
    """Follow a user.

    Args:
        ctx: MCP context
        handle: Handle of the user to follow

    Returns:
        Status of the follow operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # First resolve the handle to a DID
        resolved = bluesky_client.resolve_handle(handle)
        did = resolved.did

        # Now follow the user - follow method expects the DID as subject parameter
        follow_response = bluesky_client.follow(did)

        return {
            "status": "success",
            "message": f"Now following {handle}",
            "follow_uri": follow_response.uri,
            "follow_cid": follow_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to follow user: {str(e)}"
        return {"status": "error", "message": error_msg}


def unfollow_user(
    ctx: Context,
    follow_uri: str,
) -> Dict:
    """Unfollow a user.

    Args:
        ctx: MCP context
        follow_uri: URI of the follow record to delete

    Returns:
        Status of the unfollow operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # The unfollow method returns a boolean
        success = bluesky_client.unfollow(follow_uri)

        if success:
            return {
                "status": "success",
                "message": "Successfully unfollowed user",
            }
        else:
            return {
                "status": "error",
                "message": "Failed to unfollow user",
            }
    except Exception as e:
        error_msg = f"Failed to unfollow user: {str(e)}"
        return {"status": "error", "message": error_msg}


def mute_user(
    ctx: Context,
    actor: str,
) -> Dict:
    """Mute a user.

    Args:
        ctx: MCP context
        actor: Handle or DID of the user to mute

    Returns:
        Status of the mute operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # The mute method returns a boolean
        success = bluesky_client.mute(actor)

        if success:
            return {
                "status": "success",
                "message": f"Muted user {actor}",
            }
        else:
            return {
                "status": "error",
                "message": "Failed to mute user",
            }
    except Exception as e:
        error_msg = f"Failed to mute user: {str(e)}"
        return {"status": "error", "message": error_msg}


def unmute_user(
    ctx: Context,
    actor: str,
) -> Dict:
    """Unmute a previously muted user.

    Args:
        ctx: MCP context
        actor: Handle or DID of the user to unmute

    Returns:
        Status of the unmute operation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # The unmute method returns a boolean
        success = bluesky_client.unmute(actor)

        if success:
            return {
                "status": "success",
                "message": f"Unmuted user {actor}",
            }
        else:
            return {
                "status": "error",
                "message": "Failed to unmute user",
            }
    except Exception as e:
        error_msg = f"Failed to unmute user: {str(e)}"
        return {"status": "error", "message": error_msg}


def register_profile_tools(mcp):
    """Register profile tools with the MCP server."""
    mcp.tool()(get_profile)
    mcp.tool()(get_follows)
    mcp.tool()(get_followers)
    mcp.tool()(resolve_handle)
    mcp.tool()(follow_user)
    mcp.tool()(unfollow_user)
    mcp.tool()(mute_user)
    mcp.tool()(unmute_user)