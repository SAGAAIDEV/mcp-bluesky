"""Rate limiting framework for Bluesky MCP Server.

This module provides rate limiting functionality to prevent API violations.
Framework ready for Phase 2 implementation.
"""

import asyncio
import time
from typing import Dict, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class RateLimit:
    """Rate limit configuration for a specific category."""
    requests: int  # Number of requests allowed
    window: int    # Time window in seconds
    requests_made: deque = field(default_factory=deque)  # Timestamps of requests
    
    def is_allowed(self) -> bool:
        """Check if a new request is allowed within the rate limit."""
        now = time.time()
        
        # Remove old requests outside the time window
        while self.requests_made and now - self.requests_made[0] > self.window:
            self.requests_made.popleft()
        
        # Check if we're under the limit
        return len(self.requests_made) < self.requests
    
    def record_request(self) -> None:
        """Record a new request."""
        self.requests_made.append(time.time())
    
    def time_until_reset(self) -> float:
        """Get time in seconds until the rate limit resets."""
        if not self.requests_made:
            return 0.0
        
        oldest_request = self.requests_made[0]
        reset_time = oldest_request + self.window
        return max(0.0, reset_time - time.time())


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, category: str, retry_after: float):
        self.category = category
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {category}. Retry after {retry_after:.1f} seconds")


class BlueskyRateLimiter:
    """Rate limiter for Bluesky API calls.
    
    Implements multi-tier rate limiting with exponential backoff.
    To be fully implemented in Phase 2.
    """
    
    def __init__(self):
        """Initialize rate limiter with default Bluesky API limits."""
        # Conservative limits based on Bluesky API documentation
        self.limits = {
            'posts': RateLimit(requests=30, window=60),      # 30 posts per minute
            'follows': RateLimit(requests=60, window=60),    # 60 follows per minute
            'likes': RateLimit(requests=100, window=60),     # 100 likes per minute
            'reposts': RateLimit(requests=60, window=60),    # 60 reposts per minute
            'general': RateLimit(requests=120, window=60),   # 120 general requests per minute
            'media': RateLimit(requests=20, window=60),      # 20 media uploads per minute
        }
        
        # Global rate limit for all requests
        self.global_limit = RateLimit(requests=300, window=60)  # 300 total requests per minute
        
        # Failure tracking for exponential backoff
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.last_failure: Dict[str, float] = defaultdict(float)
    
    async def check_limit(self, category: str) -> bool:
        """Check if request is allowed for the given category.
        
        Args:
            category: Rate limit category (posts, follows, likes, etc.)
            
        Returns:
            True if request is allowed, False otherwise
            
        Raises:
            RateLimitError: If rate limit is exceeded
            
        Note:
            To be fully implemented in Phase 2.
        """
        # Check global limit first
        if not self.global_limit.is_allowed():
            retry_after = self.global_limit.time_until_reset()
            raise RateLimitError("global", retry_after)
        
        # Check category-specific limit
        limit = self.limits.get(category, self.limits['general'])
        if not limit.is_allowed():
            retry_after = limit.time_until_reset()
            raise RateLimitError(category, retry_after)
        
        return True
    
    async def record_request(self, category: str) -> None:
        """Record a successful request.
        
        Args:
            category: Rate limit category
        """
        self.global_limit.record_request()
        limit = self.limits.get(category, self.limits['general'])
        limit.record_request()
        
        # Reset failure count on successful request
        if category in self.failure_counts:
            self.failure_counts[category] = 0
    
    async def record_failure(self, category: str) -> None:
        """Record a failed request for exponential backoff.
        
        Args:
            category: Rate limit category
        """
        self.failure_counts[category] += 1
        self.last_failure[category] = time.time()
    
    def exponential_backoff(self, category: str, attempt: int = None) -> float:
        """Calculate exponential backoff delay.
        
        Args:
            category: Rate limit category
            attempt: Specific attempt number (optional)
            
        Returns:
            Delay in seconds (max 5 minutes)
            
        Note:
            To be fully implemented in Phase 2.
        """
        if attempt is None:
            attempt = self.failure_counts.get(category, 0)
        
        # Exponential backoff: 2^attempt seconds, max 5 minutes
        delay = min(2 ** attempt, 300)
        return delay
    
    async def wait_if_needed(self, category: str) -> None:
        """Wait if exponential backoff is required.
        
        Args:
            category: Rate limit category
        """
        if category not in self.failure_counts or self.failure_counts[category] == 0:
            return
        
        last_failure_time = self.last_failure.get(category, 0)
        backoff_delay = self.exponential_backoff(category)
        time_since_failure = time.time() - last_failure_time
        
        if time_since_failure < backoff_delay:
            wait_time = backoff_delay - time_since_failure
            await asyncio.sleep(wait_time)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limit status for all categories.
        
        Returns:
            Dictionary with rate limit status for each category
        """
        status = {}
        
        for category, limit in self.limits.items():
            status[category] = {
                'allowed': limit.requests,
                'used': len(limit.requests_made),
                'remaining': limit.requests - len(limit.requests_made),
                'reset_in': limit.time_until_reset(),
                'failures': self.failure_counts.get(category, 0)
            }
        
        # Add global status
        status['global'] = {
            'allowed': self.global_limit.requests,
            'used': len(self.global_limit.requests_made),
            'remaining': self.global_limit.requests - len(self.global_limit.requests_made),
            'reset_in': self.global_limit.time_until_reset()
        }
        
        return status


def rate_limit(category: str = 'general', requests_per_minute: int = None):
    """Decorator for rate limiting tool functions.
    
    Args:
        category: Rate limit category
        requests_per_minute: Override default rate limit (optional)
        
    Note:
        To be fully implemented in Phase 2.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Rate limiting logic will be implemented in Phase 2
            # For now, this is a placeholder that calls the original function
            return await func(*args, **kwargs)
        
        wrapper.rate_limit_category = category
        wrapper.rate_limit_rpm = requests_per_minute
        return wrapper
    
    return decorator


class RequestQueue:
    """Request queue for managing concurrent API calls.
    
    To be implemented in Phase 2 for production enhancement.
    """
    
    def __init__(self, max_concurrent: int = 5):
        """Initialize request queue.
        
        Args:
            max_concurrent: Maximum number of concurrent requests
        """
        self.queue: deque = deque()
        self.active = 0
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_with_queue(self, func, *args, **kwargs):
        """Execute function with queue management.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Note:
            To be fully implemented in Phase 2.
        """
        async with self.semaphore:
            try:
                self.active += 1
                return await func(*args, **kwargs)
            finally:
                self.active -= 1
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue status."""
        return {
            'active': self.active,
            'queued': len(self.queue),
            'max_concurrent': self.max_concurrent
        }


# Global rate limiter instance (to be used in Phase 2)
_global_rate_limiter: Optional[BlueskyRateLimiter] = None


def get_rate_limiter() -> BlueskyRateLimiter:
    """Get global rate limiter instance."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = BlueskyRateLimiter()
    return _global_rate_limiter


async def retry_with_backoff(func, category: str = 'general', max_retries: int = 3):
    """Retry function with exponential backoff.
    
    Args:
        func: Async function to retry
        category: Rate limit category
        max_retries: Maximum number of retry attempts
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries failed
        
    Note:
        To be fully implemented in Phase 2.
    """
    rate_limiter = get_rate_limiter()
    
    for attempt in range(max_retries + 1):
        try:
            await rate_limiter.wait_if_needed(category)
            await rate_limiter.check_limit(category)
            
            result = await func()
            await rate_limiter.record_request(category)
            return result
            
        except RateLimitError:
            if attempt == max_retries:
                raise
            await rate_limiter.record_failure(category)
            wait_time = rate_limiter.exponential_backoff(category, attempt + 1)
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            # Don't retry on permanent errors
            if attempt == max_retries or "permanent" in str(e).lower():
                raise
            await rate_limiter.record_failure(category)
            wait_time = rate_limiter.exponential_backoff(category, attempt + 1)
            await asyncio.sleep(wait_time / 2)  # Shorter wait for non-rate-limit errors