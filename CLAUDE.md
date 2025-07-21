# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Bluesky MCP (Model Context Protocol) server that provides tools for interacting with the Bluesky social network via the atproto client. The server uses a modular architecture with a main entry point (`server.py`) and organized modules in the `mcp_bluesky/` package that expose various Bluesky API operations as MCP tools.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Running the Server
```bash
# Run the server locally
uv run mcp-bluesky

# Run the server file directly
uv run server.py
```

### Testing
```bash
# Run all tests (requires BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD env vars)
uv run pytest

# Run specific test file
uv run pytest tests/test_post.py
```

### Code Quality
```bash
# Format code with black
uv run black .

# Lint with ruff
uv run ruff check .

# Type check with mypy
uv run mypy .
```

### Debug with MCP Inspector
```bash
# Basic MCP development mode
mcp dev server.py

# With editable installation
mcp dev server.py --with-editable .
```

## Architecture

### Core Components

- **server.py**: Main entry point that orchestrates the modular architecture
- **mcp_bluesky/**: Core package containing the modular implementation
- **FastMCP Framework**: Uses the FastMCP library for MCP server implementation
- **atproto Client**: Bluesky API client for all social network operations
- **Authentication**: Uses environment variables for Bluesky credentials

### Modular Architecture

**Core Modules:**
- **mcp_bluesky/config.py**: Environment configuration management
- **mcp_bluesky/client.py**: Bluesky client creation and authentication
- **mcp_bluesky/types.py**: Type definitions and data classes
- **mcp_bluesky/context.py**: MCP context lifecycle management

**Tool Modules:**
- **mcp_bluesky/tools/auth.py**: Authentication status tools
- **mcp_bluesky/tools/profiles.py**: Profile and social operations
- **mcp_bluesky/tools/posts.py**: Post creation and management
- **mcp_bluesky/tools/interactions.py**: Likes, reposts, and social interactions
- **mcp_bluesky/tools/feeds.py**: Timeline and feed operations
- **mcp_bluesky/tools/media.py**: Image and video posting
- **mcp_bluesky/tools/utilities.py**: Common helper functions

### Key Design Patterns

1. **Modular Architecture**: Tools organized by functionality with clear separation of concerns
2. **Lazy Authentication**: Client authentication occurs on first use via `get_authenticated_client()`
3. **Context Management**: Uses FastMCP's context system for request lifecycle management
4. **Error Handling**: Consistent error response format with status/message structure
5. **Dependency Injection**: Clean separation between configuration, client management, and tool logic

### Environment Configuration

Required environment variables:
- `BLUESKY_IDENTIFIER`: Your Bluesky handle (e.g., "user.bsky.social")
- `BLUESKY_APP_PASSWORD`: Your Bluesky app password
- `BLUESKY_SERVICE_URL`: Optional, defaults to "https://bsky.social"

### Tool Categories

The server provides MCP tools organized into functional categories:

1. **Authentication**: `check_auth_status`
2. **Profile Operations**: `get_profile`, `get_follows`, `get_followers`, `follow_user`, `unfollow_user`, `mute_user`, `unmute_user`, `resolve_handle`
3. **Feed Operations**: `get_timeline`, `get_author_feed`, `get_post_thread`
4. **Post Management**: `send_post`, `get_post`, `get_posts`, `delete_post`
5. **Media Posts**: `send_image`, `send_images`, `send_video`
6. **Post Interactions**: `like_post`, `unlike_post`, `get_likes`, `repost`, `unrepost`, `get_reposted_by`

### Testing Strategy

- **Mock-based Tests**: Comprehensive unit tests using mock Bluesky clients in `tests/conftest.py`
- **Integration Tests**: Some tests run against actual Bluesky API for end-to-end verification
- **Modular Test Structure**: Tests organized by functionality matching the tool module structure
- **Test Coverage**: 39 tests covering all tool categories and error scenarios
- **Mock Patches**: Tests patch `get_authenticated_client` in each tool module for proper isolation
- Tests require valid Bluesky credentials for integration tests (BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD env vars)

### Installation Methods

The server supports multiple installation methods:
1. Direct installation via uvx from git repository
2. Local development with `uv run`
3. MCP client integration with stdio transport

## Important Notes

- All MCP tools return a consistent response format with "status" and "message" fields
- Media operations (images/videos) expect base64-encoded data
- The server maintains a single authenticated client instance per session
- Posts are created with real data - use test accounts for development
- **Backward Compatibility**: The main `server.py` entry point is preserved, so existing installations and configurations continue to work without changes

## Project Management

- This project uses Jira for issue tracking. Project space shortcut is MCP.
- When creating new branches in this project follow this pattern - "type/mcp-XXX-branch-title", where:
  - `type` is `feat` or `fix`, depending on what the issue is about
  - `XXX` is the Jira number of the issue
  - Branch title should be based on Jira issue title, often it will be the same, but it can be more concise
