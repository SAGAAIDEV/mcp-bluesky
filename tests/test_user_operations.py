"""Tests for user operations: resolve_handle, mute_user, unmute_user."""

import json
import pytest
import asyncio

from server import mcp
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)


@pytest.mark.asyncio
async def test_user_operations(mock_auth_client):
    """Test resolve_handle, mute_user, and unmute_user operations.
    """

    async with client_session(mcp._mcp_server) as client:
        # Test resolve_handle
        test_handle = "test-user.bsky.social"
        print(f"\n1. Testing resolve_handle with handle={test_handle}...")

        resolve_params = {"handle": test_handle}
        result = await client.call_tool("resolve_handle", resolve_params)
        resolve_result = json.loads(result.content[0].text)

        assert (
            resolve_result["status"] == "success"
        ), f"Failed to resolve handle: {resolve_result.get('message')}"
        assert "did" in resolve_result
        assert resolve_result["did"] is not None
        assert resolve_result["did"].startswith("did:plc:")

        user_did = resolve_result["did"]
        print(f"Resolved {test_handle} to DID: {user_did}")

        # For mute/unmute tests, we'll use a test account that we can safely mute/unmute
        # We'll use the Bluesky team account as a safe test target
        test_handle = "bsky.app"

        print(f"\n2. Testing mute_user with handle={test_handle}...")

        # First mute the user
        mute_params = {"actor": test_handle}
        result = await client.call_tool("mute_user", mute_params)
        mute_result = json.loads(result.content[0].text)

        assert (
            mute_result["status"] == "success"
        ), f"Failed to mute user: {mute_result.get('message')}"
        print(f"Successfully muted {test_handle}")

        # Give the API a moment to process
        await asyncio.sleep(1)

        print(f"\n3. Testing unmute_user with handle={test_handle}...")

        # Now unmute the user
        unmute_params = {"actor": test_handle}
        result = await client.call_tool("unmute_user", unmute_params)
        unmute_result = json.loads(result.content[0].text)

        assert (
            unmute_result["status"] == "success"
        ), f"Failed to unmute user: {unmute_result.get('message')}"
        print(f"Successfully unmuted {test_handle}")

        # Test with DID instead of handle
        print("\n4. Testing mute/unmute with DID...")

        # Resolve test account's DID
        resolve_params = {"handle": test_handle}
        result = await client.call_tool("resolve_handle", resolve_params)
        resolve_result = json.loads(result.content[0].text)
        test_did = resolve_result["did"]

        # Mute using DID
        mute_params = {"actor": test_did}
        result = await client.call_tool("mute_user", mute_params)
        mute_result = json.loads(result.content[0].text)
        assert mute_result["status"] == "success"

        await asyncio.sleep(1)

        # Unmute using DID
        unmute_params = {"actor": test_did}
        result = await client.call_tool("unmute_user", unmute_params)
        unmute_result = json.loads(result.content[0].text)
        assert unmute_result["status"] == "success"

        print("\n✅ All user operations tests passed!")
        print("   - resolve_handle successfully resolved handles to DIDs")
        print("   - mute_user successfully muted users by handle and DID")
        print("   - unmute_user successfully unmuted users by handle and DID")


if __name__ == "__main__":
    asyncio.run(test_user_operations())
