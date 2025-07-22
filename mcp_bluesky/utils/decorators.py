"""Decorators and base classes for consistent tool behavior.

Provides common decorators for error handling, rate limiting, and validation.
Framework ready for Phase 1 and Phase 2 implementation.
"""

import functools
import asyncio
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from mcp.server.fastmcp import Context

from .validation import InputValidator, ValidationError
from .rate_limiting import get_rate_limiter, RateLimitError
from ..tools.utilities import handle_tool_error, create_success_response


F = TypeVar('F', bound=Callable[..., Any])


def handle_errors(operation_name: str = None):
    """Decorator to handle errors consistently across all tools.
    
    Args:
        operation_name: Name of the operation for error messages
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            op_name = operation_name or func.__name__.replace('_', ' ')
            
            try:
                result = await func(*args, **kwargs)
                
                # Ensure result is a dictionary with status
                if isinstance(result, dict):
                    if 'status' not in result:
                        result['status'] = 'success'
                    return result
                else:
                    # Wrap non-dict results
                    return create_success_response(f"Successfully completed {op_name}", result=result)
                    
            except ValidationError as e:
                return {
                    "status": "error",
                    "message": f"Validation error in {op_name}: {str(e)}",
                    "error_type": "validation"
                }
            except RateLimitError as e:
                return {
                    "status": "error", 
                    "message": f"Rate limit exceeded for {op_name}: {str(e)}",
                    "error_type": "rate_limit",
                    "retry_after": e.retry_after
                }
            except Exception as e:
                return handle_tool_error(op_name, e)
        
        return wrapper
    return decorator


def validate_input(**validators):
    """Decorator to validate input parameters.
    
    Args:
        **validators: Validation functions for specific parameters
        
    Returns:
        Decorator function
        
    Note:
        To be fully implemented in Phase 1.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Basic validation framework - to be enhanced in Phase 1
            validator = InputValidator()
            
            # Apply validators to matching parameters
            for param_name, validation_func in validators.items():
                if param_name in kwargs:
                    try:
                        if validation_func == 'post_content':
                            kwargs[param_name] = validator.validate_post_content(kwargs[param_name])
                        elif validation_func == 'user_handle':
                            kwargs[param_name] = validator.validate_user_handle(kwargs[param_name])
                        # Add more validation types as needed
                    except Exception as e:
                        raise ValidationError(f"Invalid {param_name}: {e}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(category: str = 'general', requests_per_minute: Optional[int] = None):
    """Decorator for rate limiting tool functions.
    
    Args:
        category: Rate limit category
        requests_per_minute: Override default rate limit (optional)
        
    Note:
        To be fully implemented in Phase 2.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Rate limiting logic will be implemented in Phase 2
            # For now, this is a placeholder that calls the original function
            
            rate_limiter = get_rate_limiter()
            
            try:
                # Check rate limit (Phase 2)
                await rate_limiter.check_limit(category)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Record successful request (Phase 2)
                await rate_limiter.record_request(category)
                
                return result
                
            except RateLimitError:
                # Record failure for exponential backoff
                await rate_limiter.record_failure(category)
                raise
            except Exception:
                # Record failure for exponential backoff
                await rate_limiter.record_failure(category)
                raise
        
        wrapper.rate_limit_category = category
        wrapper.rate_limit_rpm = requests_per_minute
        return wrapper
    
    return decorator


def require_auth(func: F) -> F:
    """Decorator to ensure authentication is required.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that checks authentication
    """
    @functools.wraps(func)
    async def wrapper(ctx: Context, *args, **kwargs) -> Any:
        from ..client import get_authenticated_client
        
        try:
            # Try to get authenticated client
            client = get_authenticated_client(ctx)
            if client is None:
                return {
                    "status": "error",
                    "message": "Authentication required but not available",
                    "error_type": "authentication"
                }
                
            return await func(ctx, *args, **kwargs)
            
        except Exception as e:
            if "auth" in str(e).lower():
                return {
                    "status": "error",
                    "message": f"Authentication error: {str(e)}",
                    "error_type": "authentication"
                }
            raise
    
    return wrapper


def log_usage(category: str = None):
    """Decorator to log tool usage for monitoring.
    
    Args:
        category: Usage category for logging
        
    Note:
        To be implemented in Phase 4 with structured logging.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Logging will be implemented in Phase 4
            # For now, just call the original function
            return await func(*args, **kwargs)
        
        wrapper.usage_category = category or func.__name__
        return wrapper
    
    return decorator


def retry_on_failure(max_retries: int = 3, backoff_category: str = 'general'):
    """Decorator to retry failed operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_category: Category for backoff calculation
        
    Note:
        To be fully implemented in Phase 2.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            rate_limiter = get_rate_limiter()
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Wait if exponential backoff is needed
                    await rate_limiter.wait_if_needed(backoff_category)
                    
                    return await func(*args, **kwargs)
                    
                except RateLimitError:
                    # Don't retry rate limit errors immediately
                    raise
                except Exception as e:
                    last_error = e
                    
                    # Don't retry on certain errors
                    if "permanent" in str(e).lower() or "invalid" in str(e).lower():
                        raise
                    
                    if attempt < max_retries:
                        await rate_limiter.record_failure(backoff_category)
                        wait_time = rate_limiter.exponential_backoff(backoff_category, attempt + 1)
                        await asyncio.sleep(wait_time / 2)  # Shorter wait for non-rate-limit errors
                    
            # If we get here, all retries failed
            raise last_error
        
        return wrapper
    return decorator


def comprehensive_tool_decorator(
    operation_name: str = None,
    category: str = 'general',
    require_authentication: bool = True,
    validate_inputs: Optional[Dict[str, str]] = None,
    max_retries: int = 0,
    log_category: str = None
):
    """Comprehensive decorator that combines all tool behaviors.
    
    Args:
        operation_name: Name of the operation
        category: Rate limiting category
        require_authentication: Whether authentication is required
        validate_inputs: Input validation configuration
        max_retries: Number of retry attempts
        log_category: Logging category
        
    Returns:
        Combined decorator function
    """
    def decorator(func: F) -> F:
        # Apply decorators in order
        wrapped_func = func
        
        # 1. Error handling (outermost)
        wrapped_func = handle_errors(operation_name)(wrapped_func)
        
        # 2. Authentication check
        if require_authentication:
            wrapped_func = require_auth(wrapped_func)
        
        # 3. Input validation
        if validate_inputs:
            wrapped_func = validate_input(**validate_inputs)(wrapped_func)
        
        # 4. Rate limiting
        wrapped_func = rate_limit(category)(wrapped_func)
        
        # 5. Retry logic
        if max_retries > 0:
            wrapped_func = retry_on_failure(max_retries, category)(wrapped_func)
        
        # 6. Usage logging (innermost)
        wrapped_func = log_usage(log_category)(wrapped_func)
        
        return wrapped_func
    
    return decorator


class ToolMixin:
    """Mixin class providing common tool functionality.
    
    To be used as a base class for tool implementations.
    """
    
    def __init__(self, category: str = 'general'):
        """Initialize tool mixin.
        
        Args:
            category: Default rate limiting category
        """
        self.category = category
        self.validator = InputValidator()
    
    async def handle_error(self, operation_name: str, error: Exception) -> Dict[str, Any]:
        """Handle errors consistently."""
        return handle_tool_error(operation_name, error)
    
    def create_success(self, message: str, **data) -> Dict[str, Any]:
        """Create success response."""
        return create_success_response(message, **data)
    
    def validate_text(self, text: str, max_length: int = 300) -> str:
        """Validate text input."""
        return self.validator.validate_post_content(text) if max_length == 300 else text
    
    def validate_handle(self, handle: str) -> str:
        """Validate user handle."""
        return self.validator.validate_user_handle(handle)