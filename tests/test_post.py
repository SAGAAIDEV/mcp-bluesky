#!/usr/bin/env python
"""Integration tests for Bluesky MCP server post operations."""
import json
import os
import pytest
import uuid
import asyncio
from unittest.mock import Mock, patch

from server import mcp
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)


class MockBlueskyClient:
    """Mock Bluesky client that simulates atproto client behavior."""
    
    def __init__(self):
        self.me = Mock()
        self.me.handle = "test-user.bsky.social"
        self.me.did = "did:plc:test123456789"
        self._base_url = "https://bsky.social"
        self.created_posts = []  # Track created posts
        self.likes = {}  # Track likes by post URI
        
    def send_post(self, **kwargs):
        """Mock send_post response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.post/test123"
        response.cid = "bafytest123456789"
        self.created_posts.append(response.uri)
        return response
        
    def get_likes(self, uri, cid=None, cursor=None, limit=50):
        """Mock get_likes response."""
        response = Mock()
        likes_data = {
            "uri": uri,
            "cid": "bafytest123456789",
            "likes": self.likes.get(uri, []),
            "cursor": None,
        }
        response.dict.return_value = likes_data
        return response
        
    def like(self, uri, cid):
        """Mock like response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.like/test123"
        response.cid = "bafylike123456789"
        
        # Add to likes tracking
        if uri not in self.likes:
            self.likes[uri] = []
        self.likes[uri].append({
            "createdAt": "2023-01-01T00:00:00Z",
            "indexedAt": "2023-01-01T00:00:00Z",
            "actor": {
                "did": "did:plc:test123456789",
                "handle": "test-user.bsky.social",
                "displayName": "Test User",
            },
        })
        return response
        
    def delete_post(self, uri):
        """Mock delete_post response."""
        response = Mock()
        response.dict.return_value = {
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        if uri in self.created_posts:
            self.created_posts.remove(uri)
        return response


@pytest.fixture
def mock_bluesky_client():
    """Fixture that provides a mock Bluesky client."""
    return MockBlueskyClient()


@pytest.fixture
def mock_auth_client(mock_bluesky_client):
    """Fixture that mocks the get_authenticated_client function."""
    with patch('server.get_authenticated_client', return_value=mock_bluesky_client):
        yield mock_bluesky_client


@pytest.mark.asyncio
async def test_create_and_delete_post(mock_auth_client):
    """Test creating a post and then deleting it with mocks."""
    
    # Create client session
    async with client_session(mcp._mcp_server) as client:
        # Create a post with a unique identifier to avoid duplicate posts
        unique_id = str(uuid.uuid4())[:8]
        test_text = f"Test post from Bluesky MCP test suite - {unique_id}"
        create_params = {"text": test_text}

        # Call the send_post tool
        result = await client.call_tool("send_post", create_params)
        post_result = json.loads(result.content[0].text)
        assert post_result.get("status") == "success"

        post_uri = post_result["post_uri"]
        post_cid = post_result["post_cid"]

        # Get likes for the post (should be empty)
        get_likes_params = {"uri": post_uri}
        result = await client.call_tool("get_likes", get_likes_params)
        likes_result = json.loads(result.content[0].text)
        assert likes_result.get("status") == "success"

        # Verify initial like count is 0 or likes array is empty
        likes_data = likes_result.get("likes", {})
        initial_likes = len(likes_data.get("likes", []))
        assert initial_likes == 0

        # Like the post
        like_params = {"uri": post_uri, "cid": post_cid}
        result = await client.call_tool("like_post", like_params)
        like_result = json.loads(result.content[0].text)
        assert like_result.get("status") == "success"

        # Get likes for the post (should now have 1 like)
        get_likes_params = {"uri": post_uri}
        result = await client.call_tool("get_likes", get_likes_params)
        likes_result = json.loads(result.content[0].text)
        assert likes_result.get("status") == "success"

        # Like count should be 1
        likes_data = likes_result.get("likes", {})
        like_count = len(likes_data.get("likes", []))
        assert like_count == 1

        # Delete the post we just created
        delete_params = {"uri": post_uri}
        result = await client.call_tool("delete_post", delete_params)
        delete_result = json.loads(result.content[0].text)
        assert delete_result.get("status") == "success"
