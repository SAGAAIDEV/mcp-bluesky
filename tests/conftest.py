"""Shared test configuration and fixtures."""
import pytest
from unittest.mock import Mock, patch
from typing import List, Optional


class MockBlueskyClient:
    """Mock Bluesky client that simulates atproto client behavior."""
    
    def __init__(self):
        self.me = Mock()
        self.me.handle = "test-user.bsky.social"
        self.me.did = "did:plc:test123456789"
        self._base_url = "https://bsky.social"
        self.created_posts = []
        self.likes = {}
        self.reposts = {}
        self.follows = {}
        self.did_to_handle = {}  # Map DIDs to handles
        self.muted_users = set()
        
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
        
        # Build follows list from tracked follows and static ones
        follows_list = [
            {
                "did": "did:plc:followed123",
                "handle": "followed-user.bsky.social",
                "displayName": "Followed User",
                "createdAt": "2023-01-01T00:00:00Z",
            }
        ]
        
        # Add dynamically followed users
        for subject_did, follow_uri in self.follows.items():
            # subject_did is the DID, we need to map it back to handle
            handle = self.did_to_handle.get(subject_did, subject_did)
            follows_list.append({
                "did": subject_did,
                "handle": handle,
                "displayName": "Test User",
                "createdAt": "2023-01-01T00:00:00Z",
            })
        
        response.dict.return_value = {
            "subject": {
                "did": "did:plc:test123456789",
                "handle": actor,
                "displayName": "Test User",
            },
            "follows": follows_list,
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
        self.created_posts.append(response.uri)
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
        if uri in self.created_posts:
            self.created_posts.remove(uri)
        return response
        
    def like(self, uri: str, cid: str) -> Mock:
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
        
        # Add to reposts tracking
        if uri not in self.reposts:
            self.reposts[uri] = []
        self.reposts[uri].append({
            "did": "did:plc:test123456789",
            "handle": "test-user.bsky.social",
            "displayName": "Test User",
            "createdAt": "2023-01-01T00:00:00Z",
        })
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
            "likes": self.likes.get(uri, []),
            "cursor": None,
        }
        return response
        
    def get_reposted_by(self, uri: str, cid: Optional[str] = None, cursor: Optional[str] = None, limit: int = 50) -> Mock:
        """Mock get_reposted_by response."""
        response = Mock()
        response.dict.return_value = {
            "uri": uri,
            "repostedBy": self.reposts.get(uri, []),
            "cursor": None,
        }
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
        # Store the mapping from DID to handle
        self.did_to_handle[response.did] = handle
        return response
        
    def mute(self, actor: str) -> bool:
        """Mock mute response."""
        self.muted_users.add(actor)
        return True
        
    def unmute(self, actor: str) -> bool:
        """Mock unmute response."""
        self.muted_users.discard(actor)
        return True
        
    def follow(self, subject: str) -> Mock:
        """Mock follow response."""
        response = Mock()
        response.uri = "at://did:plc:test123456789/app.bsky.graph.follow/test123"
        response.cid = "bafyfollow123456789"
        # Store the follow using the DID as key, but map back to handle
        self.follows[subject] = response.uri
        return response
        
    def unfollow(self, follow_uri: str) -> bool:
        """Mock unfollow response."""
        for subject, uri in list(self.follows.items()):
            if uri == follow_uri:
                del self.follows[subject]
                break
        return True
        
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


@pytest.fixture
def mock_bluesky_client():
    """Fixture that provides a mock Bluesky client."""
    return MockBlueskyClient()


@pytest.fixture
def mock_auth_client(mock_bluesky_client):
    """Fixture that mocks the get_authenticated_client function."""
    with patch('server.get_authenticated_client', return_value=mock_bluesky_client):
        yield mock_bluesky_client