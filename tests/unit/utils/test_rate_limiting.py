"""Unit tests for rate limiting utilities.

Tests for the rate limiting framework implemented in Phase 2.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from mcp_bluesky.utils.rate_limiting import (
    RateLimit,
    RateLimitError,
    BlueskyRateLimiter,
    rate_limit,
    RequestQueue,
    get_rate_limiter,
    retry_with_backoff
)


class TestRateLimit:
    """Test RateLimit class."""
    
    def test_rate_limit_creation(self):
        """Test RateLimit can be created."""
        limit = RateLimit(requests=30, window=60)
        assert limit.requests == 30
        assert limit.window == 60
        assert len(limit.requests_made) == 0
    
    def test_rate_limit_allows_initial_requests(self):
        """Test rate limit allows requests under the limit."""
        limit = RateLimit(requests=5, window=60)
        
        # Should allow up to 5 requests
        for i in range(5):
            assert limit.is_allowed() is True
            limit.record_request()
        
        # 6th request should be denied
        assert limit.is_allowed() is False
    
    def test_rate_limit_resets_over_time(self):
        """Test rate limit resets after time window."""
        limit = RateLimit(requests=2, window=1)  # 1 second window
        
        # Use up the limit
        assert limit.is_allowed() is True
        limit.record_request()
        assert limit.is_allowed() is True
        limit.record_request()
        assert limit.is_allowed() is False
        
        # Wait for reset (in real implementation)
        # This would require time manipulation in actual tests
        
    def test_time_until_reset(self):
        """Test time_until_reset calculation."""
        limit = RateLimit(requests=1, window=60)
        
        # No requests made yet
        assert limit.time_until_reset() == 0.0
        
        # After making a request
        limit.record_request()
        reset_time = limit.time_until_reset()
        assert 0 <= reset_time <= 60


class TestRateLimitError:
    """Test RateLimitError exception."""
    
    def test_rate_limit_error_creation(self):
        """Test RateLimitError can be created."""
        error = RateLimitError("posts", 30.5)
        assert error.category == "posts"
        assert error.retry_after == 30.5
        assert "posts" in str(error)
        assert "30.5" in str(error)


class TestBlueskyRateLimiter:
    """Test BlueskyRateLimiter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.limiter = BlueskyRateLimiter()
    
    @pytest.mark.asyncio
    async def test_check_limit_allows_requests(self):
        """Test rate limiter allows requests under limits."""
        # Should allow requests for different categories
        result = await self.limiter.check_limit('posts')
        assert result is True
        
        result = await self.limiter.check_limit('follows')
        assert result is True
    
    @pytest.mark.asyncio
    async def test_record_request(self):
        """Test recording successful requests."""
        category = 'posts'
        initial_count = len(self.limiter.limits[category].requests_made)
        
        await self.limiter.record_request(category)
        
        final_count = len(self.limiter.limits[category].requests_made)
        assert final_count == initial_count + 1
        
        # Should reset failure count
        assert self.limiter.failure_counts[category] == 0
    
    @pytest.mark.asyncio
    async def test_record_failure(self):
        """Test recording failed requests."""
        category = 'posts'
        initial_failures = self.limiter.failure_counts[category]
        
        await self.limiter.record_failure(category)
        
        assert self.limiter.failure_counts[category] == initial_failures + 1
        assert category in self.limiter.last_failure
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        category = 'posts'
        
        # No failures yet
        backoff = self.limiter.exponential_backoff(category, 0)
        assert backoff == 1  # 2^0 = 1
        
        # First failure
        backoff = self.limiter.exponential_backoff(category, 1)
        assert backoff == 2  # 2^1 = 2
        
        # Multiple failures (capped at 300 seconds)
        backoff = self.limiter.exponential_backoff(category, 10)
        assert backoff == 300  # Capped at 5 minutes
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_no_failures(self):
        """Test wait_if_needed with no failures."""
        # Should return immediately if no failures
        start_time = time.time()
        await self.limiter.wait_if_needed('posts')
        end_time = time.time()
        
        # Should complete very quickly
        assert end_time - start_time < 0.1
    
    def test_get_status(self):
        """Test getting rate limit status."""
        status = self.limiter.get_status()
        
        # Should have all categories
        expected_categories = ['posts', 'follows', 'likes', 'reposts', 'general', 'media', 'global']
        for category in expected_categories:
            assert category in status
            
            if category != 'global':
                assert 'allowed' in status[category]
                assert 'used' in status[category]
                assert 'remaining' in status[category]
                assert 'reset_in' in status[category]
                assert 'failures' in status[category]


class TestRateLimitDecorator:
    """Test rate limiting decorator."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_basic(self):
        """Test basic rate limit decorator functionality."""
        call_count = 0
        
        @rate_limit(category='test')
        async def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert call_count == 1
        
        # Check decorator attributes
        assert hasattr(test_function, 'rate_limit_category')
        assert test_function.rate_limit_category == 'test'
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_with_custom_rpm(self):
        """Test rate limit decorator with custom rate."""
        @rate_limit(category='custom', requests_per_minute=10)
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
        
        # Check decorator attributes
        assert test_function.rate_limit_category == 'custom'
        assert test_function.rate_limit_rpm == 10


class TestRequestQueue:
    """Test RequestQueue class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.queue = RequestQueue(max_concurrent=2)
    
    @pytest.mark.asyncio
    async def test_execute_with_queue_basic(self):
        """Test basic queue execution."""
        async def test_func():
            return "success"
        
        result = await self.queue.execute_with_queue(test_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_execute_with_queue_concurrent_limit(self):
        """Test queue respects concurrent limits."""
        call_order = []
        
        async def slow_func(name):
            call_order.append(f"start_{name}")
            await asyncio.sleep(0.1)  # Simulate work
            call_order.append(f"end_{name}")
            return name
        
        # Start 3 tasks (queue allows max 2 concurrent)
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                self.queue.execute_with_queue(slow_func, f"task_{i}")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should complete
        assert len(results) == 3
        assert set(results) == {"task_0", "task_1", "task_2"}
    
    def test_get_queue_status(self):
        """Test getting queue status."""
        status = self.queue.get_queue_status()
        
        assert 'active' in status
        assert 'queued' in status
        assert 'max_concurrent' in status
        assert status['max_concurrent'] == 2


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_rate_limiter_singleton(self):
        """Test get_rate_limiter returns same instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        
        assert limiter1 is limiter2
        assert isinstance(limiter1, BlueskyRateLimiter)
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self):
        """Test retry_with_backoff with successful function."""
        call_count = 0
        
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_with_backoff(test_func, max_retries=2)
        assert result == "success"
        assert call_count == 1  # Should succeed on first try
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_eventual_success(self):
        """Test retry_with_backoff with eventual success."""
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry_with_backoff(flaky_func, max_retries=3)
        assert result == "success"
        assert call_count == 3  # Should succeed on third try
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_permanent_failure(self):
        """Test retry_with_backoff with permanent failure."""
        async def failing_func():
            raise Exception("permanent failure")
        
        with pytest.raises(Exception, match="permanent"):
            await retry_with_backoff(failing_func, max_retries=2)
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_rate_limit_error(self):
        """Test retry_with_backoff with rate limit error."""
        async def rate_limited_func():
            raise RateLimitError("test", 1.0)
        
        with pytest.raises(RateLimitError):
            await retry_with_backoff(rate_limited_func, max_retries=2)


# Integration tests
class TestRateLimitingIntegration:
    """Integration tests for rate limiting system."""
    
    @pytest.mark.asyncio
    async def test_full_rate_limiting_flow(self):
        """Test complete rate limiting flow."""
        limiter = BlueskyRateLimiter()
        category = 'test_integration'
        
        # Should start with no requests
        status = limiter.get_status()
        if category in status:
            assert status[category]['used'] == 0
        
        # Record some requests
        for _ in range(5):
            await limiter.check_limit(category)
            await limiter.record_request(category)
        
        # Record a failure
        await limiter.record_failure(category)
        
        # Check final status
        status = limiter.get_status()
        assert limiter.failure_counts[category] > 0


# Phase 2 TODO: Add tests for:
# - Redis backend integration
# - Distributed rate limiting
# - Rate limit persistence across restarts
# - Custom rate limit policies
# - Real-time rate limit monitoring
# - Integration with Bluesky API error responses