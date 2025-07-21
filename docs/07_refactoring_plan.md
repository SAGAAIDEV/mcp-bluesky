# Refactoring Plan: Bluesky MCP Server

## Overview
Transform the monolithic `server.py` (1100+ lines) into a modular, maintainable architecture with logical separation of concerns.

## Current State Analysis

### Issues with Current Architecture
- Single file with 1100+ lines of code
- All MCP tools mixed together without logical grouping
- Client management scattered throughout
- Configuration handling mixed with business logic
- Difficult to navigate and maintain
- Testing requires importing entire server module

### Tool Categories Identified
1. **Authentication**: `check_auth_status`
2. **Profile Operations**: `get_profile`, `get_follows`, `get_followers`, `follow_user`, `unfollow_user`, `mute_user`, `unmute_user`, `resolve_handle`
3. **Feed Operations**: `get_timeline`, `get_author_feed`, `get_post_thread`
4. **Post Management**: `send_post`, `get_post`, `get_posts`, `delete_post`
5. **Media Posts**: `send_image`, `send_images`, `send_video`
6. **Post Interactions**: `like_post`, `unlike_post`, `get_likes`, `repost`, `unrepost`, `get_reposted_by`

## Proposed Architecture

### 1. Core Module Structure
```
mcp_bluesky/
├── __init__.py              # Package initialization
├── server.py                # Main server entry point (minimal)
├── client.py                # Bluesky client management
├── config.py                # Configuration and environment handling
├── context.py               # MCP context management
├── types.py                 # Type definitions and data classes
└── tools/                   # Tool implementations
    ├── __init__.py
    ├── auth.py              # Authentication tools
    ├── profiles.py          # Profile operations
    ├── posts.py             # Post management
    ├── interactions.py      # Likes, reposts, follows
    ├── feeds.py             # Timeline and feed operations
    ├── media.py             # Image/video posting
    └── utilities.py         # Utility functions
```

### 2. Module Responsibilities

#### `mcp_bluesky/client.py`
- Bluesky client initialization and management
- Authentication logic (`login`, `get_authenticated_client`)
- Client lifecycle management
- Connection handling

#### `mcp_bluesky/config.py`
- Environment variable handling
- Configuration validation
- Default values and constants
- Service URL management

#### `mcp_bluesky/context.py`
- MCP context management
- Application context lifecycle
- Context utilities and helpers

#### `mcp_bluesky/types.py`
- Type definitions for all data structures
- Response models
- Common interfaces
- Type aliases

#### `mcp_bluesky/tools/auth.py`
- `check_auth_status` tool
- Authentication utilities
- Credential validation

#### `mcp_bluesky/tools/profiles.py`
- `get_profile` tool
- `get_follows` tool
- `get_followers` tool
- `resolve_handle` tool
- Profile-related utilities

#### `mcp_bluesky/tools/posts.py`
- `send_post` tool
- `get_post` tool
- `get_posts` tool
- `delete_post` tool
- Post management utilities

#### `mcp_bluesky/tools/interactions.py`
- `like_post`, `unlike_post` tools
- `get_likes` tool
- `repost`, `unrepost` tools
- `get_reposted_by` tool
- `follow_user`, `unfollow_user` tools
- `mute_user`, `unmute_user` tools
- Social interaction utilities

#### `mcp_bluesky/tools/feeds.py`
- `get_timeline` tool
- `get_author_feed` tool
- `get_post_thread` tool
- Feed processing utilities

#### `mcp_bluesky/tools/media.py`
- `send_image` tool
- `send_images` tool
- `send_video` tool
- Media processing utilities
- Base64 encoding/decoding

#### `mcp_bluesky/tools/utilities.py`
- Common utility functions
- Error handling helpers
- Response formatting
- Shared business logic

### 3. Key Improvements

#### Separation of Concerns
- Client management isolated in `client.py`
- Tool categories logically grouped by functionality
- Configuration centralized in `config.py`
- Type safety improved with dedicated `types.py`
- Context management separated from business logic

#### Maintainability
- Each tool category in separate modules (~100-200 lines each)
- Consistent error handling patterns across modules
- Shared utilities and helper functions
- Clear module boundaries and dependencies
- Easier to locate and modify specific functionality

#### Testability
- Tools can be tested independently
- Client mocking simplified through dependency injection
- Configuration injection for testing scenarios
- Modular imports in test files
- Isolated unit tests for each module

#### Developer Experience
- Clear navigation between related functionality
- Easier to add new tools in appropriate modules
- Better IDE support with smaller, focused files
- Consistent coding patterns across modules
- Improved code completion and navigation

### 4. Migration Strategy

#### Phase 1: Infrastructure Setup
1. Create package structure with `__init__.py`
2. Extract configuration management to `config.py`
3. Create client management module in `client.py`
4. Set up type definitions in `types.py`
5. Create context management utilities in `context.py`

#### Phase 2: Tool Extraction
1. Extract authentication tools to `tools/auth.py`
2. Extract profile operations to `tools/profiles.py`
3. Extract post management to `tools/posts.py`
4. Extract interaction tools to `tools/interactions.py`
5. Extract feed operations to `tools/feeds.py`
6. Extract media operations to `tools/media.py`
7. Create utility functions in `tools/utilities.py`

#### Phase 3: Integration
1. Update main `server.py` to import from modules
2. Update test imports to use new module structure
3. Update `pyproject.toml` configuration for package structure
4. Verify all functionality works with integration tests
5. Update MCP tool registrations

#### Phase 4: Cleanup and Documentation
1. Remove unused imports and dead code
2. Add proper docstrings to all modules
3. Ensure consistent error handling patterns
4. Update README and documentation
5. Add type hints where missing

### 5. Implementation Details

#### Error Handling Pattern
```python
# Consistent error response format across all tools
def handle_tool_error(operation_name: str, error: Exception) -> Dict:
    return {
        "status": "error",
        "message": f"Failed to {operation_name}: {str(error)}"
    }
```

#### Tool Registration Pattern
```python
# Each tool module exports its tools for registration
from .tools.auth import register_auth_tools
from .tools.profiles import register_profile_tools
# ... other imports

def register_all_tools(mcp_server):
    register_auth_tools(mcp_server)
    register_profile_tools(mcp_server)
    # ... other registrations
```

#### Client Dependency Injection
```python
# Client provided through dependency injection
def get_profile_tool(client_provider: Callable[[], Client]):
    @mcp.tool()
    def get_profile(ctx: Context, handle: Optional[str] = None) -> Dict:
        client = client_provider()
        # ... implementation
```

### 6. Benefits

#### Code Quality
- Reduced file complexity (1100+ lines → 10-15 files of 50-200 lines)
- Improved readability and navigation
- Better separation of concerns
- Consistent patterns across modules
- Enhanced type safety

#### Maintainability
- Easier to add new tools in appropriate modules
- Independent testing of components
- Clear boundaries between functionality
- Simplified debugging and troubleshooting
- Better error isolation

#### Team Collaboration
- Multiple developers can work on different tools simultaneously
- Reduced merge conflicts
- Clear ownership of functionality areas
- Better code review process
- Improved onboarding for new team members

#### Performance
- Faster import times for specific functionality
- Better memory usage with selective imports
- Improved development experience with smaller files
- Faster test execution for individual modules

### 7. Backward Compatibility

This refactoring maintains 100% backward compatibility:
- All existing MCP tools continue to work unchanged
- API interfaces remain identical
- Environment variable handling unchanged
- Test suite continues to pass without modification
- Client code requires no changes

### 8. Future Enhancements

With the new modular structure, future enhancements become easier:
- Add new tool categories by creating new modules
- Implement caching at the client level
- Add middleware for logging and monitoring
- Support multiple authentication methods
- Add configuration validation
- Implement rate limiting per tool category

## Conclusion

This refactoring transforms a monolithic codebase into a well-organized, maintainable architecture that will significantly improve developer experience and code quality while maintaining full backward compatibility. The modular structure sets the foundation for future enhancements and makes the codebase much more approachable for new contributors.