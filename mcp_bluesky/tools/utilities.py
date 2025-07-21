"""Utility functions for Bluesky MCP server tools.

Common helper functions and error handling patterns.
"""

from typing import Dict, Any


def handle_tool_error(operation_name: str, error: Exception) -> Dict[str, str]:
    """Handle tool errors with consistent response format.

    Args:
        operation_name: Name of the operation that failed
        error: The exception that occurred

    Returns:
        Standardized error response
    """
    return {
        "status": "error",
        "message": f"Failed to {operation_name}: {str(error)}"
    }


def create_success_response(message: str, **additional_data: Any) -> Dict[str, Any]:
    """Create a success response with optional additional data.

    Args:
        message: Success message
        **additional_data: Additional fields to include in the response

    Returns:
        Standardized success response
    """
    response = {
        "status": "success",
        "message": message
    }
    response.update(additional_data)
    return response


def validate_limit(limit: Any, min_val: int = 1, max_val: int = 100) -> int:
    """Validate and normalize limit parameter.

    Args:
        limit: Limit value to validate (can be string or int)
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Validated limit as integer
    """
    if isinstance(limit, str):
        limit = int(limit)
    return max(min_val, min(max_val, limit))


def safe_model_dump(obj: Any) -> Any:
    """Safely convert response object to dictionary.

    Args:
        obj: Object to convert (may have model_dump method or be dict already)

    Returns:
        Dictionary representation of the object
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    else:
        return obj