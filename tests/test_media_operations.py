"""Tests for media operations: send_image, send_images, send_video."""

import base64
import json
import pytest
import asyncio

from server import mcp
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)


def encode_file_to_base64(file_path: str) -> str:
    """Encode a file to base64 string."""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


@pytest.mark.asyncio
async def test_media_operations(mock_auth_client):
    """Test send_image, send_images, and send_video operations.
    """

    # Create test media data (mock files)
    # Create a small test image (1x1 pixel PNG)
    test_image_data = base64.b64encode(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
    ).decode('utf-8')
    
    # Create a small test video (minimal MP4 data)
    test_video_data = base64.b64encode(b'\x00\x00\x00\x18ftypmp41\x00\x00\x00\x00mp41').decode('utf-8')

    async with client_session(mcp._mcp_server) as client:
        # Test send_image
        print("\n1. Testing send_image...")

        image_params = {
            "text": "Test post with single image from MCP test suite",
            "image_data": test_image_data,
            "image_alt": "Test image 1 - Google logo",
        }

        result = await client.call_tool("send_image", image_params)
        image_result = json.loads(result.content[0].text)

        assert (
            image_result["status"] == "success"
        ), f"Failed to send image: {image_result.get('message')}"
        assert "post_uri" in image_result
        assert "post_cid" in image_result

        image_post_uri = image_result["post_uri"]
        print(f"Successfully created post with image: {image_post_uri}")

        # Give the API a moment to process
        await asyncio.sleep(2)

        # Test send_images with multiple images
        print("\n2. Testing send_images with 2 images...")

        images_params = {
            "text": "Test post with multiple images from MCP test suite",
            "images_data": [test_image_data, test_image_data],
            "image_alts": [
                "Test image 1 - Google logo",
                "Test image 2 - Wikipedia transparency demo",
            ],
        }

        result = await client.call_tool("send_images", images_params)
        images_result = json.loads(result.content[0].text)

        assert (
            images_result["status"] == "success"
        ), f"Failed to send images: {images_result.get('message')}"
        assert "post_uri" in images_result
        assert "post_cid" in images_result

        images_post_uri = images_result["post_uri"]
        print(f"Successfully created post with multiple images: {images_post_uri}")

        # Give the API a moment to process
        await asyncio.sleep(2)

        # Test send_video
        print("\n3. Testing send_video...")

        video_params = {
            "text": "Test post with video from MCP test suite",
            "video_data": test_video_data,
            "video_alt": "Test video",
        }

        result = await client.call_tool("send_video", video_params)
        video_result = json.loads(result.content[0].text)
        assert video_result["status"] == "success"
        assert "post_uri" in video_result
        assert "post_cid" in video_result

        video_post_uri = video_result["post_uri"]
        print(f"Successfully created post with video: {video_post_uri}")

        # Clean up - delete the test posts
        print("\n4. Cleaning up test posts...")

        # Delete image post
        delete_params = {"uri": image_post_uri}
        result = await client.call_tool("delete_post", delete_params)
        delete_result = json.loads(result.content[0].text)
        assert delete_result["status"] == "success"
        print("Deleted single image test post")

        # Delete images post
        delete_params = {"uri": images_post_uri}
        result = await client.call_tool("delete_post", delete_params)
        delete_result = json.loads(result.content[0].text)
        assert delete_result["status"] == "success"
        print("Deleted multiple images test post")

        # Delete video post
        delete_params = {"uri": video_post_uri}
        result = await client.call_tool("delete_post", delete_params)
        delete_result = json.loads(result.content[0].text)
        assert delete_result["status"] == "success"
        print("Deleted video test post")

        print("\n✅ All media operations tests completed!")
        print("   - send_image successfully posted image")
        print("   - send_images successfully posted multiple images")
        print("   - send_video test completed")
        print("   - All test posts cleaned up")


if __name__ == "__main__":
    asyncio.run(test_media_operations())
