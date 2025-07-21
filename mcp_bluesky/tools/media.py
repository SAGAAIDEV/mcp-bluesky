"""Media posting tools for Bluesky MCP server.

Tools for posting images and videos to Bluesky.
"""

import base64
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context

from ..client import get_authenticated_client


def send_image(
    ctx: Context,
    text: str,
    image_data: str,
    image_alt: str,
    profile_identify: Optional[str] = None,
    reply_to: Optional[Dict[str, Any]] = None,
    langs: Optional[List[str]] = None,
    facets: Optional[List[Dict[str, Any]]] = None,
) -> Dict:
    """Send a post with a single image.

    Args:
        ctx: MCP context
        text: Text content of the post
        image_data: Base64-encoded image data
        image_alt: Alternative text description for the image
        profile_identify: Optional handle or DID for the post author
        reply_to: Optional reply information dict with keys uri and cid
        langs: Optional list of language codes
        facets: Optional list of facets (mentions, links, etc.)

    Returns:
        Status of the post creation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to decode image data: {str(e)}",
            }

        # Send the post with image
        post_response = bluesky_client.send_image(
            text=text,
            image=image_bytes,
            image_alt=image_alt,
            profile_identify=profile_identify,
            reply_to=reply_to,
            langs=langs,
            facets=facets,
        )

        return {
            "status": "success",
            "message": "Post with image created successfully",
            "post_uri": post_response.uri,
            "post_cid": post_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to create post with image: {str(e)}"
        return {"status": "error", "message": error_msg}


def send_images(
    ctx: Context,
    text: str,
    images_data: List[str],
    image_alts: Optional[List[str]] = None,
    profile_identify: Optional[str] = None,
    reply_to: Optional[Dict[str, Any]] = None,
    langs: Optional[List[str]] = None,
    facets: Optional[List[Dict[str, Any]]] = None,
) -> Dict:
    """Send a post with multiple images (up to 4).

    Args:
        ctx: MCP context
        text: Text content of the post
        images_data: List of base64-encoded image data (max 4)
        image_alts: Optional list of alt text for each image
        profile_identify: Optional handle or DID for the post author
        reply_to: Optional reply information dict with keys uri and cid
        langs: Optional list of language codes
        facets: Optional list of facets (mentions, links, etc.)

    Returns:
        Status of the post creation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # Verify we have 1-4 images
        if not images_data:
            return {
                "status": "error",
                "message": "At least one image is required",
            }

        if len(images_data) > 4:
            return {
                "status": "error",
                "message": "Maximum of 4 images allowed",
            }

        # Decode all images
        images_bytes = []
        for img_data in images_data:
            try:
                image_bytes = base64.b64decode(img_data)
                images_bytes.append(image_bytes)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to decode image data: {str(e)}",
                }

        # Send the post with images
        post_response = bluesky_client.send_images(
            text=text,
            images=images_bytes,
            image_alts=image_alts,
            profile_identify=profile_identify,
            reply_to=reply_to,
            langs=langs,
            facets=facets,
        )

        return {
            "status": "success",
            "message": "Post with images created successfully",
            "post_uri": post_response.uri,
            "post_cid": post_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to create post with images: {str(e)}"
        return {"status": "error", "message": error_msg}


def send_video(
    ctx: Context,
    text: str,
    video_data: str,
    video_alt: Optional[str] = None,
    profile_identify: Optional[str] = None,
    reply_to: Optional[Dict[str, Any]] = None,
    langs: Optional[List[str]] = None,
    facets: Optional[List[Dict[str, Any]]] = None,
) -> Dict:
    """Send a post with a video.

    Args:
        ctx: MCP context
        text: Text content of the post
        video_data: Base64-encoded video data
        video_alt: Optional alternative text description for the video
        profile_identify: Optional handle or DID for the post author
        reply_to: Optional reply information dict with keys uri and cid
        langs: Optional list of language codes
        facets: Optional list of facets (mentions, links, etc.)

    Returns:
        Status of the post creation
    """
    try:
        bluesky_client = get_authenticated_client(ctx)

        # Decode base64 video
        try:
            video_bytes = base64.b64decode(video_data)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to decode video data: {str(e)}",
            }

        # Send the post with video
        post_response = bluesky_client.send_video(
            text=text,
            video=video_bytes,
            video_alt=video_alt,
            profile_identify=profile_identify,
            reply_to=reply_to,
            langs=langs,
            facets=facets,
        )

        return {
            "status": "success",
            "message": "Post with video created successfully",
            "post_uri": post_response.uri,
            "post_cid": post_response.cid,
        }
    except Exception as e:
        error_msg = f"Failed to create post with video: {str(e)}"
        return {"status": "error", "message": error_msg}


def register_media_tools(mcp):
    """Register media tools with the MCP server."""
    mcp.tool()(send_image)
    mcp.tool()(send_images)
    mcp.tool()(send_video)