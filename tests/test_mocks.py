#!/usr/bin/env python
"""Mock-based tests for Bluesky MCP server tools."""

import json
import base64
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, List
import pytest

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
        
    def get_profile(self, handle: str) -> Mock:
        """Mock get_profile response."""
        response = Mock()
        response.dict.return_value = {
            "did": "did:plc:test123456789",
            "handle": handle,
            "displayName": "Test User",
            "description": "A test user profile",
            "avatar": "https://example.com/avatar.jpg",
            "followersCount": 100,
            "followsCount": 50,
            "postsCount": 25,
            "indexedAt": "2023-01-01T00:00:00Z",
            "createdAt": "2023-01-01T00:00:00Z",
        }
        return response
        
    def get_follows(self, actor: str, cursor: Optional[str] = None, limit: int = 50) -> Mock:
        """Mock get_follows response."""
        response = Mock()
        response.dict.return_value = {
            "subject": {
                "did": "did:plc:test123456789",
                "handle": actor,
                "displayName": "Test User",
            },
            "follows": [
                {
                    "did": "did:plc:followed123",
                    "handle": "followed-user.bsky.social",
                    "displayName": "Followed User",
                    "createdAt": "2023-01-01T00:00:00Z",
                }
            ],
            "cursor": None,
        }
        return response
        
    def get_followers(self, actor: str, cursor: Optional[str] = None, limit: int = 50) -> Mock:
        """Mock get_followers response."""
        response = Mock()
        response.dict.return_value = {
            "subject": {
                "did": "did:plc:test123456789",
                "handle": actor,
                "displayName": "Test User",
            },
            "followers": [
                {
                    "did": "did:plc:follower123",
                    "handle": "follower-user.bsky.social",
                    "displayName": "Follower User",
                    "createdAt": "2023-01-01T00:00:00Z",
                }
            ],
            "cursor": None,
        }
        return response
        
    def send_post(self, **kwargs) -> Mock:
        """Mock send_post response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.post/test123"
        response.cid = "bafytest123456789"
        response.dict.return_value = {
            "uri": "at://did:plc:test123456789/app.bsky.feed.post/test123",
            "cid": "bafytest123456789",
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
            "validationStatus": "valid",
        }
        return response
        
    def delete_post(self, uri: str) -> Mock:
        """Mock delete_post response."""
        response = Mock()
        response.dict.return_value = {
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def like(self, uri: str, cid: str) -> Mock:
        """Mock like response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.like/test123"
        response.cid = "bafylike123456789"
        response.dict.return_value = {
            "uri": "at://did:plc:test123456789/app.bsky.feed.like/test123",
            "cid": "bafylike123456789",
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def unlike(self, like_uri: str) -> Mock:
        """Mock unlike response."""
        response = Mock()
        response.dict.return_value = {
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def repost(self, uri: str, cid: str) -> Mock:
        """Mock repost response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.repost/test123"
        response.cid = "bafyrepost123456789"
        response.dict.return_value = {
            "uri": "at://did:plc:test123456789/app.bsky.feed.repost/test123",
            "cid": "bafyrepost123456789",
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def unrepost(self, repost_uri: str) -> Mock:
        """Mock unrepost response."""
        response = Mock()
        response.dict.return_value = {
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def get_likes(self, uri: str, cid: Optional[str] = None, cursor: Optional[str] = None, limit: int = 50) -> Mock:
        """Mock get_likes response."""
        response = Mock()
        response.dict.return_value = {
            "uri": uri,
            "cid": "bafytest123456789",
            "likes": [
                {
                    "createdAt": "2023-01-01T00:00:00Z",
                    "indexedAt": "2023-01-01T00:00:00Z",
                    "actor": {
                        "did": "did:plc:liker123",
                        "handle": "liker-user.bsky.social",
                        "displayName": "Liker User",
                    },
                }
            ],
            "cursor": None,
        }
        return response
        
    def get_reposted_by(self, uri: str, cid: Optional[str] = None, cursor: Optional[str] = None, limit: int = 50) -> Mock:
        """Mock get_reposted_by response."""
        response = Mock()
        response.dict.return_value = {
            "uri": uri,
            "repostedBy": [
                {
                    "did": "did:plc:reposter123",
                    "handle": "reposter-user.bsky.social",
                    "displayName": "Reposter User",
                    "createdAt": "2023-01-01T00:00:00Z",
                }
            ],
            "cursor": None,
        }
        return response
        
    def get_post(self, post_rkey: str, profile_identify: Optional[str] = None, cid: Optional[str] = None) -> Mock:
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
        
        # Add model_dump method for server compatibility
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
        
    def get_posts(self, uris: List[str]) -> Mock:
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
        
    def get_timeline(self, algorithm: Optional[str] = None, cursor: Optional[str] = None, limit: Optional[int] = None) -> Mock:
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
        
    def get_author_feed(self, actor: str, cursor: Optional[str] = None, filter: Optional[str] = None, limit: Optional[int] = None, include_pins: bool = False) -> Mock:
        """Mock get_author_feed response."""
        response = Mock()
        feed_data = [
            {
                "post": {
                    "uri": "at://did:plc:test123456789/app.bsky.feed.post/author1",
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
        
    def get_post_thread(self, uri: str, depth: Optional[int] = None, parent_height: Optional[int] = None) -> Mock:
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
        
    def resolve_handle(self, handle: str) -> Mock:
        """Mock resolve_handle response."""
        response = Mock()
        response.did = f"did:plc:{handle.replace('.', '').replace('-', '')}123"
        response.model_dump.return_value = {"did": response.did}
        return response
        
    def mute(self, actor: str) -> bool:
        """Mock mute response."""
        return True
        
    def unmute(self, actor: str) -> bool:
        """Mock unmute response."""
        return True
        
    def follow(self, subject: str) -> Mock:
        """Mock follow response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.graph.follow/test123"
        response.cid = "bafyfollow123456789"
        response.dict.return_value = {
            "uri": "at://did:plc:test123456789/app.bsky.graph.follow/test123",
            "cid": "bafyfollow123456789",
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def unfollow(self, follow_uri: str) -> Mock:
        """Mock unfollow response."""
        response = Mock()
        response.dict.return_value = {
            "commit": {
                "cid": "bafycommit123456789",
                "rev": "test-revision",
            },
        }
        return response
        
    def upload_blob(self, data: bytes, encoding: str = "image/jpeg") -> Mock:
        """Mock upload_blob response."""
        response = Mock()
        response.dict.return_value = {
            "blob": {
                "type": "blob",
                "ref": {
                    "link": "bafyblob123456789"
                },
                "mimeType": encoding,
                "size": len(data),
            }
        }
        return response
        
    def send_image(self, text: str, image: bytes, image_alt: str, **kwargs) -> Mock:
        """Mock send_image response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.post/test123"
        response.cid = "bafytest123456789"
        return response
        
    def send_images(self, text: str, images: List[bytes], image_alts: Optional[List[str]] = None, **kwargs) -> Mock:
        """Mock send_images response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.feed.post/test123"
        response.cid = "bafytest123456789"
        return response
        
    def send_video(self, text: str, video: bytes, video_alt: Optional[str] = None, **kwargs) -> Mock:
        """Mock send_video response."""
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


# Test cases for all MCP tools

@pytest.mark.asyncio
async def test_check_auth_status_authenticated(mock_auth_client):
    """Test check_auth_status with authenticated client."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("check_auth_status", {})
        response = result.content[0].text.strip('"')  # Remove JSON quotes
        assert response == "Authenticated to https://bsky.social"


@pytest.mark.asyncio
async def test_check_auth_status_unauthenticated():
    """Test check_auth_status without authentication."""
    with patch('mcp_bluesky.tools.auth.get_authenticated_client', side_effect=ValueError("No credentials")):
        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool("check_auth_status", {})
            response = result.content[0].text.strip('"')  # Remove JSON quotes
            assert response == "Not authenticated: No credentials"


@pytest.mark.asyncio
async def test_get_profile_self(mock_auth_client):
    """Test get_profile without handle (self)."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_profile", {})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["profile"]["handle"] == "test-user.bsky.social"
        assert response["profile"]["displayName"] == "Test User"


@pytest.mark.asyncio
async def test_get_profile_other_user(mock_auth_client):
    """Test get_profile with specific handle."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_profile", {"handle": "other-user.bsky.social"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["profile"]["handle"] == "other-user.bsky.social"


@pytest.mark.asyncio
async def test_get_follows(mock_auth_client):
    """Test get_follows."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_follows", {"limit": 10})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "follows" in response
        assert len(response["follows"]["follows"]) == 1
        assert response["follows"]["follows"][0]["handle"] == "followed-user.bsky.social"


@pytest.mark.asyncio
async def test_get_followers(mock_auth_client):
    """Test get_followers."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_followers", {"limit": 10})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "followers" in response
        assert len(response["followers"]["followers"]) == 1
        assert response["followers"]["followers"][0]["handle"] == "follower-user.bsky.social"


@pytest.mark.asyncio
async def test_send_post(mock_auth_client):
    """Test send_post."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("send_post", {"text": "Test post content"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["post_uri"] == "at://did:plc:test123456789/app.bsky.feed.post/test123"
        assert response["post_cid"] == "bafytest123456789"


@pytest.mark.asyncio
async def test_delete_post(mock_auth_client):
    """Test delete_post."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("delete_post", {"uri": "at://did:plc:test123456789/app.bsky.feed.post/test123"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "message" in response


@pytest.mark.asyncio
async def test_like_post(mock_auth_client):
    """Test like_post."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("like_post", {
            "uri": "at://did:plc:test123456789/app.bsky.feed.post/test123",
            "cid": "bafytest123456789"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["like_uri"] == "at://did:plc:test123456789/app.bsky.feed.like/test123"


@pytest.mark.asyncio
async def test_unlike_post(mock_auth_client):
    """Test unlike_post."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("unlike_post", {
            "like_uri": "at://did:plc:test123456789/app.bsky.feed.like/test123"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "message" in response


@pytest.mark.asyncio
async def test_repost(mock_auth_client):
    """Test repost."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("repost", {
            "uri": "at://did:plc:test123456789/app.bsky.feed.post/test123",
            "cid": "bafytest123456789"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["repost_uri"] == "at://did:plc:test123456789/app.bsky.feed.repost/test123"


@pytest.mark.asyncio
async def test_unrepost(mock_auth_client):
    """Test unrepost."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("unrepost", {
            "repost_uri": "at://did:plc:test123456789/app.bsky.feed.repost/test123"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "message" in response


@pytest.mark.asyncio
async def test_get_likes(mock_auth_client):
    """Test get_likes."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_likes", {
            "uri": "at://did:plc:test123456789/app.bsky.feed.post/test123"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "likes" in response
        assert len(response["likes"]["likes"]) == 1
        assert response["likes"]["likes"][0]["actor"]["handle"] == "liker-user.bsky.social"


@pytest.mark.asyncio
async def test_get_reposted_by(mock_auth_client):
    """Test get_reposted_by."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_reposted_by", {
            "uri": "at://did:plc:test123456789/app.bsky.feed.post/test123"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "reposts" in response
        assert len(response["reposts"]["repostedBy"]) == 1
        assert response["reposts"]["repostedBy"][0]["handle"] == "reposter-user.bsky.social"


@pytest.mark.asyncio
async def test_get_post(mock_auth_client):
    """Test get_post."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_post", {
            "post_rkey": "test123",
            "profile_identify": "test-user.bsky.social"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "post" in response
        assert response["post"]["uri"] == "at://did:plc:test123456789/app.bsky.feed.post/test123"
        assert response["post"]["record"]["text"] == "Test post content"


@pytest.mark.asyncio
async def test_get_posts(mock_auth_client):
    """Test get_posts."""
    uris = [
        "at://did:plc:test123456789/app.bsky.feed.post/test123",
        "at://did:plc:test123456789/app.bsky.feed.post/test456"
    ]
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_posts", {"uris": uris})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "posts" in response
        assert len(response["posts"]["posts"]) == 2


@pytest.mark.asyncio
async def test_get_timeline(mock_auth_client):
    """Test get_timeline."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_timeline", {"limit": 10})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "timeline" in response
        assert len(response["timeline"]["feed"]) == 1
        assert response["timeline"]["feed"][0]["post"]["record"]["text"] == "Timeline post content"


@pytest.mark.asyncio
async def test_get_author_feed(mock_auth_client):
    """Test get_author_feed."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_author_feed", {
            "actor": "test-user.bsky.social",
            "limit": 10
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "feed" in response
        assert len(response["feed"]["feed"]) == 1
        assert response["feed"]["feed"][0]["post"]["record"]["text"] == "Author feed post content"


@pytest.mark.asyncio
async def test_get_post_thread(mock_auth_client):
    """Test get_post_thread."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("get_post_thread", {
            "uri": "at://did:plc:test123456789/app.bsky.feed.post/test123"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "thread" in response
        assert response["thread"]["thread"]["post"]["record"]["text"] == "Thread post content"
        assert len(response["thread"]["thread"]["replies"]) == 1


@pytest.mark.asyncio
async def test_resolve_handle(mock_auth_client):
    """Test resolve_handle."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("resolve_handle", {"handle": "test-user.bsky.social"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "did" in response
        assert response["did"] == "did:plc:testuserbskysocial123"


@pytest.mark.asyncio
async def test_mute_user(mock_auth_client):
    """Test mute_user."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("mute_user", {"actor": "other-user.bsky.social"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "message" in response


@pytest.mark.asyncio
async def test_unmute_user(mock_auth_client):
    """Test unmute_user."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("unmute_user", {"actor": "other-user.bsky.social"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "message" in response


@pytest.mark.asyncio
async def test_follow_user(mock_auth_client):
    """Test follow_user."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("follow_user", {"handle": "other-user.bsky.social"})
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["follow_uri"] == "at://did:plc:test123456789/app.bsky.graph.follow/test123"


@pytest.mark.asyncio
async def test_unfollow_user(mock_auth_client):
    """Test unfollow_user."""
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("unfollow_user", {
            "follow_uri": "at://did:plc:test123456789/app.bsky.graph.follow/test123"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert "message" in response


@pytest.mark.asyncio
async def test_send_image(mock_auth_client):
    """Test send_image."""
    # Create a small test image (1x1 pixel PNG)
    test_image_data = base64.b64encode(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
    ).decode('utf-8')
    
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("send_image", {
            "text": "Test image post",
            "image_data": test_image_data,
            "image_alt": "Test image"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["post_uri"] == "at://did:plc:test123456789/app.bsky.feed.post/test123"


@pytest.mark.asyncio
async def test_send_images(mock_auth_client):
    """Test send_images."""
    # Create a small test image (1x1 pixel PNG)
    test_image_data = base64.b64encode(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
    ).decode('utf-8')
    
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("send_images", {
            "text": "Test multiple images post",
            "images_data": [test_image_data, test_image_data],
            "image_alts": ["Test image 1", "Test image 2"]
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["post_uri"] == "at://did:plc:test123456789/app.bsky.feed.post/test123"


@pytest.mark.asyncio
async def test_send_video(mock_auth_client):
    """Test send_video."""
    # Create a small test video (minimal MP4 data)
    test_video_data = base64.b64encode(b'\x00\x00\x00\x18ftypmp41\x00\x00\x00\x00mp41').decode('utf-8')
    
    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("send_video", {
            "text": "Test video post",
            "video_data": test_video_data,
            "video_alt": "Test video"
        })
        response = json.loads(result.content[0].text)
        assert response["status"] == "success"
        assert response["post_uri"] == "at://did:plc:test123456789/app.bsky.feed.post/test123"


# Error handling tests

@pytest.mark.asyncio
async def test_get_profile_error():
    """Test get_profile with authentication error."""
    with patch('mcp_bluesky.tools.auth.get_authenticated_client', side_effect=ValueError("No credentials")):
        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool("get_profile", {})
            response = json.loads(result.content[0].text)
            assert response["status"] == "error"
            assert "Failed to get profile" in response["message"]


@pytest.mark.asyncio
async def test_send_post_error():
    """Test send_post with authentication error."""
    with patch('mcp_bluesky.tools.auth.get_authenticated_client', side_effect=ValueError("No credentials")):
        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool("send_post", {"text": "Test post"})
            response = json.loads(result.content[0].text)
            assert response["status"] == "error"
            assert "Failed to send post" in response["message"]


@pytest.mark.asyncio
async def test_bluesky_api_error():
    """Test handling of Bluesky API errors."""
    # Create a mock client that raises an exception
    mock_client = MagicMock()
    mock_client.get_profile.side_effect = Exception("API Error")
    
    with patch('mcp_bluesky.tools.profiles.get_authenticated_client', return_value=mock_client):
        async with client_session(mcp._mcp_server) as client:
            result = await client.call_tool("get_profile", {})
            response = json.loads(result.content[0].text)
            assert response["status"] == "error"
            assert "Failed to get profile" in response["message"]