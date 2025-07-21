"""Bluesky MCP Server.

Modular implementation with tools organized by functionality.
"""

from typing import Dict

from mcp.server.fastmcp import FastMCP

from mcp_bluesky.context import app_lifespan
from mcp_bluesky.tools.auth import register_auth_tools
from mcp_bluesky.tools.profiles import register_profile_tools
from mcp_bluesky.tools.posts import register_post_tools
from mcp_bluesky.tools.interactions import register_interaction_tools
from mcp_bluesky.tools.feeds import register_feed_tools
from mcp_bluesky.tools.media import register_media_tools


# Create the MCP server
mcp = FastMCP("Bluesky", dependencies=[], lifespan=app_lifespan)


# Register all tool modules
register_auth_tools(mcp)
register_profile_tools(mcp)
register_post_tools(mcp)
register_interaction_tools(mcp)
register_feed_tools(mcp)
register_media_tools(mcp)


# Add resource to provide information about available tools
@mcp.resource("info://bluesky-tools")
def get_bluesky_tools_info() -> Dict:
    """Get information about the available Bluesky tools."""
    tools_info = {
        "description": "Bluesky API Tools",
        "version": "0.1.0",
        "auth_requirements": "Most tools require authentication using BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD environment variables",
        "categories": {
            "authentication": ["check_auth_status"],
            "profiles": [
                "get_profile",
                "get_follows", 
                "get_followers",
                "resolve_handle",
                "follow_user",
                "unfollow_user",
                "mute_user",
                "unmute_user"
            ],
            "posts": [
                "send_post",
                "get_post",
                "get_posts",
                "delete_post"
            ],
            "interactions": [
                "like_post",
                "unlike_post",
                "repost",
                "unrepost",
                "get_likes",
                "get_reposted_by"
            ],
            "feeds": [
                "get_timeline",
                "get_author_feed",
                "get_post_thread"
            ],
            "media": [
                "send_image",
                "send_images",
                "send_video"
            ]
        },
    }
    return tools_info


def main():
    """Main entry point for the script."""
    # Stdio is prefered for local execution.
    mcp.run(transport="stdio")


# Main entry point
if __name__ == "__main__":
    main()