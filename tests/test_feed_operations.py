"""Tests for feed operations: get_author_feed, get_post_thread."""

import json
import os
import pytest
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
        
    def get_author_feed(self, actor, cursor=None, filter=None, limit=None, include_pins=False):
        """Mock get_author_feed response."""
        response = Mock()
        feed_data = [
            {
                "post": {
                    "uri": f"at://did:plc:test123456789/app.bsky.feed.post/author1",
                    "cid": "bafyauthor123",
                    "author": {
                        "did": "did:plc:test123456789",
                        "handle": actor,
                        "displayName": "Test User",
                    },
                    "record": {
                        "text": "Author feed post content",
                        "createdAt": "2023-01-01T00:00:00Z",
                    },
                    "replyCount": 0,
                    "repostCount": 0,
                    "likeCount": 0,
                    "indexedAt": "2023-01-01T00:00:00Z",
                }
            }
        ]
        response.feed = feed_data
        response.cursor = None
        response.model_dump.return_value = {"feed": feed_data, "cursor": None}
        return response
        
    def get_post_thread(self, uri, depth=None, parent_height=None):
        """Mock get_post_thread response."""
        response = Mock()
        thread_data = {
            "post": {
                "uri": uri,
                "cid": "bafythread123",
                "author": {
                    "did": "did:plc:test123456789",
                    "handle": "test-user.bsky.social",
                    "displayName": "Test User",
                },
                "record": {
                    "text": "Thread post content",
                    "createdAt": "2023-01-01T00:00:00Z",
                },
                "replyCount": 1,
                "repostCount": 0,
                "likeCount": 0,
                "indexedAt": "2023-01-01T00:00:00Z",
            },
            "replies": [
                {
                    "post": {
                        "uri": f"{uri}/reply1",
                        "cid": "bafyreply123",
                        "author": {
                            "did": "did:plc:replier123",
                            "handle": "replier-user.bsky.social",
                            "displayName": "Replier User",
                        },
                        "record": {
                            "text": "Reply content",
                            "createdAt": "2023-01-01T00:00:00Z",
                        },
                        "replyCount": 0,
                        "repostCount": 0,
                        "likeCount": 0,
                        "indexedAt": "2023-01-01T00:00:00Z",
                    }
                }
            ]
        }
        response.thread = thread_data
        response.model_dump.return_value = {"thread": thread_data}
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
async def test_feed_operations(mock_auth_client):
    """Test get_author_feed and get_post_thread operations with mocks."""
    
    async with client_session(mcp._mcp_server) as client:
        # Test get_author_feed with the test user handle
        test_identifier = "test-user.bsky.social"
        print(f"\n1. Testing get_author_feed with handle={test_identifier}...")

        # Test get_author_feed with the user's own handle
        author_feed_params = {"actor": test_identifier, "limit": 5}
        result = await client.call_tool("get_author_feed", author_feed_params)
        author_feed_result = json.loads(result.content[0].text)

        assert author_feed_result["status"] == "success"
        assert "feed" in author_feed_result

        # The feed response should be a dict with 'feed' key
        feed_data = author_feed_result["feed"]
        assert isinstance(feed_data, dict)
        assert "feed" in feed_data

        # Extract posts from feed
        feed_items = feed_data["feed"]
        assert len(feed_items) > 0

        print(f"Found {len(feed_items)} posts in author's feed")

        # Get the first post URI for thread testing
        first_post = feed_items[0]["post"]
        post_uri = first_post["uri"]

        print("\n2. Testing get_post_thread with post URI...")

        # Test get_post_thread
        thread_params = {
            "uri": post_uri,
            "depth": 3,  # Get up to 3 levels of replies
            "parent_height": 2,  # Get up to 2 parent posts
        }
        result = await client.call_tool("get_post_thread", thread_params)
        thread_result = json.loads(result.content[0].text)

        assert thread_result["status"] == "success"
        assert "thread" in thread_result

        # The thread response should be a dict with 'thread' key
        thread_data = thread_result["thread"]
        assert isinstance(thread_data, dict)
        assert "thread" in thread_data

        # Verify we got the thread structure
        thread = thread_data["thread"]
        assert "post" in thread

        print("\n✅ All feed operations tests passed!")
        print(f"   - get_author_feed returned {len(feed_items)} posts for {test_identifier}")
        print("   - get_post_thread successfully retrieved thread structure")


if __name__ == "__main__":
    asyncio.run(test_feed_operations())
