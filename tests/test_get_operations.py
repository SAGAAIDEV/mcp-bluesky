"""Tests for get operations: get_post, get_posts, get_timeline."""

import json
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
        
    def get_timeline(self, algorithm=None, cursor=None, limit=None):
        """Mock get_timeline response."""
        response = Mock()
        feed_data = [
            {
                "post": {
                    "uri": "at://did:plc:test123456789/app.bsky.feed.post/timeline1",
                    "cid": "bafytimeline123",
                    "author": {
                        "did": "did:plc:test123456789",
                        "handle": "test-user.bsky.social",
                        "displayName": "Test User",
                    },
                    "record": {
                        "text": "Timeline post content",
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
        
    def get_post(self, post_rkey, profile_identify=None, cid=None):
        """Mock get_post response."""
        response = Mock()
        response.uri = f"at://did:plc:test123456789/app.bsky.feed.post/{post_rkey}"
        response.cid = "bafytest123456789"
        response.author = {
            "did": "did:plc:test123456789",
            "handle": profile_identify or "test-user.bsky.social",
            "displayName": "Test User",
        }
        response.record = {
            "text": "Test post content",
            "createdAt": "2023-01-01T00:00:00Z",
        }
        response.replyCount = 0
        response.repostCount = 0
        response.likeCount = 0
        response.indexedAt = "2023-01-01T00:00:00Z"
        
        response.model_dump.return_value = {
            "uri": response.uri,
            "cid": response.cid,
            "author": response.author,
            "record": response.record,
            "replyCount": response.replyCount,
            "repostCount": response.repostCount,
            "likeCount": response.likeCount,
            "indexedAt": response.indexedAt,
        }
        return response
        
    def get_posts(self, uris):
        """Mock get_posts response."""
        response = Mock()
        posts = []
        for uri in uris:
            posts.append({
                "uri": uri,
                "cid": f"bafy{hash(uri) % 1000000}",
                "author": {
                    "did": "did:plc:test123456789",
                    "handle": "test-user.bsky.social",
                    "displayName": "Test User",
                },
                "record": {
                    "text": f"Test post content for {uri}",
                    "createdAt": "2023-01-01T00:00:00Z",
                },
                "replyCount": 0,
                "repostCount": 0,
                "likeCount": 0,
                "indexedAt": "2023-01-01T00:00:00Z",
            })
        response.posts = posts
        response.model_dump.return_value = {"posts": posts}
        return response

    def send_post(self, **kwargs):
        """Mock send_post response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.post/test123"
        response.cid = "bafytest123456789"
        return response


@pytest.fixture
def mock_bluesky_client():
    """Fixture that provides a mock Bluesky client."""
    return MockBlueskyClient()


@pytest.fixture
def mock_auth_client(mock_bluesky_client):
    """Fixture that mocks the get_authenticated_client function."""
    # Patch the function where it's imported and used
    with patch('mcp_bluesky.tools.auth.get_authenticated_client', return_value=mock_bluesky_client), \
         patch('mcp_bluesky.tools.profiles.get_authenticated_client', return_value=mock_bluesky_client), \
         patch('mcp_bluesky.tools.posts.get_authenticated_client', return_value=mock_bluesky_client), \
         patch('mcp_bluesky.tools.interactions.get_authenticated_client', return_value=mock_bluesky_client), \
         patch('mcp_bluesky.tools.feeds.get_authenticated_client', return_value=mock_bluesky_client), \
         patch('mcp_bluesky.tools.media.get_authenticated_client', return_value=mock_bluesky_client):
        yield mock_bluesky_client


@pytest.mark.asyncio
async def test_get_operations(mock_auth_client):
    """Test get_post, get_posts, and get_timeline operations with mocks."""

    async with client_session(mcp._mcp_server) as client:
        # Test get_timeline first to get some posts
        print("\n1. Testing get_timeline...")
        timeline_params = {"limit": 5}
        result = await client.call_tool("get_timeline", timeline_params)
        timeline_result = json.loads(result.content[0].text)

        assert timeline_result["status"] == "success"
        assert "timeline" in timeline_result

        # The timeline response should be a dict with 'feed' key
        timeline_data = timeline_result["timeline"]
        assert isinstance(timeline_data, dict)
        assert "feed" in timeline_data

        # Extract post URIs from timeline for further testing
        feed_items = timeline_data["feed"]
        assert len(feed_items) > 0

        # Get the first post URI and extract rkey
        first_post = feed_items[0]["post"]
        post_uri = first_post["uri"]  # Format: at://did:plc:xxx/app.bsky.feed.post/rkey

        # Parse the URI to get author DID and rkey
        uri_parts = post_uri.split("/")
        author_did = uri_parts[2]  # did:plc:xxx
        post_rkey = uri_parts[-1]  # the rkey

        print(f"\n2. Testing get_post with rkey={post_rkey[:8]}... and author={author_did[:20]}...")

        # Test get_post with the extracted post
        post_params = {"post_rkey": post_rkey, "profile_identify": author_did}
        result = await client.call_tool("get_post", post_params)
        post_result = json.loads(result.content[0].text)

        assert post_result["status"] == "success"
        assert "post" in post_result

        # Test get_posts with multiple URIs
        print("\n3. Testing get_posts with multiple URIs...")

        # Get up to 3 post URIs from timeline
        post_uris = [item["post"]["uri"] for item in feed_items[:3]]

        posts_params = {"uris": post_uris}
        result = await client.call_tool("get_posts", posts_params)
        posts_result = json.loads(result.content[0].text)

        assert posts_result["status"] == "success"
        assert "posts" in posts_result

        # The posts response should have a posts key
        posts_data = posts_result["posts"]
        assert isinstance(posts_data, dict)
        assert "posts" in posts_data

        returned_posts = posts_data["posts"]
        assert len(returned_posts) > 0

        print("\n✅ All get operations tests passed!")
        print(f"   - get_timeline returned {len(feed_items)} posts")
        print("   - get_post successfully retrieved post")
        print(f"   - get_posts retrieved {len(returned_posts)} posts")


if __name__ == "__main__":
    asyncio.run(test_get_operations())
