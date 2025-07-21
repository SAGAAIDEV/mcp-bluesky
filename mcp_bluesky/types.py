"""Type definitions for Bluesky MCP Server.

Common types and interfaces used throughout the application.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from atproto import Client


@dataclass
class AppContext:
    """Application context containing shared resources."""
    bluesky_client: Optional[Client]


# Common response types
ToolResponse = Dict[str, Any]
StatusResponse = Dict[str, Union[str, bool]]

# Common parameter types
HandleType = Optional[str]
PostUriType = str
PostTextType = str
ImageDataType = str  # Base64 encoded
VideoDataType = str  # Base64 encoded

# Feed and timeline types
FeedLimit = Optional[int]
CursorType = Optional[str]