#!/usr/bin/env python
"""Integration tests for Bluesky MCP server repost operations."""
import json
import pytest
import asyncio
import uuid

from server import mcp
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)


@pytest.mark.asyncio
async def test_repost_and_unrepost(mock_auth_client):
    """Test repost and unrepost operations."""

    # Create client session
    async with client_session(mcp._mcp_server) as client:
        # Step 1: Create a test post to repost
        unique_id = str(uuid.uuid4())[:8]
        test_text = f"Test post for repost operations - {unique_id}"
        post_params = {"text": test_text}

        result = await client.call_tool("send_post", post_params)
        post_result = json.loads(result.content[0].text)
        assert post_result.get("status") == "success"

        post_uri = post_result["post_uri"]
        post_cid = post_result["post_cid"]
        print(f"Created test post: {post_uri}")

        # Step 2: Repost the post
        print("\n=== Testing repost ===")
        repost_params = {"uri": post_uri, "cid": post_cid}
        result = await client.call_tool("repost", repost_params)
        repost_result = json.loads(result.content[0].text)
        assert repost_result.get("status") == "success"
        assert repost_result.get("repost_uri") is not None

        repost_uri = repost_result["repost_uri"]
        print(f"Successfully reposted: {repost_uri}")

        # Wait a moment for the repost to propagate
        await asyncio.sleep(2)

        # Step 3: Unrepost
        print("\n=== Testing unrepost ===")
        unrepost_params = {"repost_uri": repost_uri}
        result = await client.call_tool("unrepost", unrepost_params)
        unrepost_result = json.loads(result.content[0].text)
        assert unrepost_result.get("status") == "success"
        print("Successfully unreposted")

        # Wait a moment for the unrepost to propagate
        await asyncio.sleep(2)

        # Step 4: Clean up - delete the test post
        print("\n=== Cleaning up ===")
        delete_params = {"uri": post_uri}
        result = await client.call_tool("delete_post", delete_params)
        delete_result = json.loads(result.content[0].text)
        assert delete_result.get("status") == "success"
        print("Test post deleted")

        print("\nRepost and unrepost tests passed!")


@pytest.mark.asyncio
async def test_get_reposted_by(mock_auth_client):
    """Test get_reposted_by on an existing post."""
    # Create client session
    async with client_session(mcp._mcp_server) as client:
        # Create a test post
        test_text = "Test post for get_reposted_by"
        post_params = {"text": test_text}

        result = await client.call_tool("send_post", post_params)
        post_result = json.loads(result.content[0].text)
        assert post_result.get("status") == "success"

        post_uri = post_result["post_uri"]

        # Try to get reposted by (might be empty)
        get_reposts_params = {"uri": post_uri, "limit": 10}
        result = await client.call_tool("get_reposted_by", get_reposts_params)
        reposts_result = json.loads(result.content[0].text)
        assert reposts_result.get("status") == "success"

        reposts_data = reposts_result["reposts"]
        repost_count = len(reposts_data.get("repostedBy", []))
        print(f"Successfully retrieved reposts. Count: {repost_count}")

        # Clean up
        delete_params = {"uri": post_uri}
        await client.call_tool("delete_post", delete_params)

        print("\nget_reposted_by test completed!")
