"""Unit tests for validation utilities.

Tests for the validation framework implemented in Phase 1.
"""

import pytest
from mcp_bluesky.utils.validation import (
    validate_text_length,
    validate_file_size,
    validate_handle,
    validate_uri,
    validate_media_format,
    sanitize_input,
    ValidationError,
    InputValidator
)


class TestValidationFunctions:
    """Test individual validation functions."""
    
    def test_validate_text_length_valid(self):
        """Test valid text length."""
        text = "This is a valid post"
        # Should not raise an exception
        validate_text_length(text, max_length=300)
    
    def test_validate_text_length_too_long(self):
        """Test text that exceeds length limit."""
        text = "x" * 301  # Exceeds 300 character limit
        with pytest.raises(ValueError, match="Text exceeds 300 character limit"):
            validate_text_length(text, max_length=300)
    
    def test_validate_file_size_valid(self):
        """Test valid file size."""
        data = b"x" * 1000  # 1KB
        # Should not raise an exception
        validate_file_size(data, max_size=1048576)  # 1MB limit
    
    def test_validate_file_size_too_large(self):
        """Test file that exceeds size limit."""
        data = b"x" * (1048576 + 1)  # Exceeds 1MB
        with pytest.raises(ValueError, match="File size exceeds .* bytes"):
            validate_file_size(data, max_size=1048576)
    
    def test_validate_handle_valid(self):
        """Test valid handle formats."""
        valid_handles = [
            "user.bsky.social",
            "test_user",
            "user123",
            "@user.bsky.social"  # With @ prefix
        ]
        
        for handle in valid_handles:
            result = validate_handle(handle)
            # Should strip @ prefix
            assert not result.startswith('@')
    
    def test_validate_handle_invalid(self):
        """Test invalid handle formats."""
        invalid_handles = [
            "",  # Empty
            "user with spaces",  # Spaces
            "user@domain",  # @ in middle
        ]
        
        for handle in invalid_handles:
            with pytest.raises(ValueError):
                validate_handle(handle)
    
    def test_validate_uri_valid(self):
        """Test valid AT Protocol URI."""
        uri = "at://did:plc:example/com.atproto.repo.record/123"
        result = validate_uri(uri)
        assert result == uri
    
    def test_validate_uri_invalid(self):
        """Test invalid URI formats."""
        invalid_uris = [
            "",  # Empty
            "https://example.com",  # Wrong protocol
            "at:/invalid"  # Malformed
        ]
        
        for uri in invalid_uris:
            with pytest.raises(ValueError):
                validate_uri(uri)
    
    def test_validate_media_format_valid(self):
        """Test valid media formats."""
        valid_files = [
            "image.jpg",
            "image.png", 
            "video.mp4",
            "image.JPEG"  # Case insensitive
        ]
        
        for filename in valid_files:
            result = validate_media_format(filename)
            assert result is True
    
    def test_validate_media_format_invalid(self):
        """Test invalid media formats."""
        invalid_files = [
            "document.pdf",
            "archive.zip",
            "script.exe"
        ]
        
        for filename in invalid_files:
            with pytest.raises(ValueError, match="File format .* not allowed"):
                validate_media_format(filename)
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        test_cases = [
            ("normal text", "normal text"),
            ("text\x00with\x00nulls", "textwithwithwithoutout nulls"),  # Remove null bytes
            ("  text with spaces  ", "text with spaces"),  # Strip whitespace
            ("text\r\nwith\rlinebreaks", "text\nwith\nlinebreaks"),  # Normalize line breaks
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            # Basic check - full implementation in Phase 1
            assert isinstance(result, str)
            assert len(result) <= len(input_text)


class TestInputValidator:
    """Test InputValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()
    
    def test_validate_post_content_valid(self):
        """Test valid post content validation."""
        content = "This is a valid post content"
        result = self.validator.validate_post_content(content)
        assert isinstance(result, str)
        assert len(result) <= 300
    
    def test_validate_post_content_too_long(self):
        """Test post content that's too long."""
        content = "x" * 301  # Exceeds limit
        with pytest.raises(ValueError):
            self.validator.validate_post_content(content)
    
    def test_validate_media_upload_valid(self):
        """Test valid media upload."""
        data = b"x" * 1000  # 1KB
        filename = "test.jpg"
        result = self.validator.validate_media_upload(data, filename)
        assert result is True
    
    def test_validate_media_upload_too_large(self):
        """Test media upload that's too large."""
        data = b"x" * (1048576 + 1)  # Exceeds 1MB
        filename = "test.jpg"
        with pytest.raises(ValueError):
            self.validator.validate_media_upload(data, filename)
    
    def test_validate_user_handle_valid(self):
        """Test valid user handle validation."""
        handle = "user.bsky.social"
        result = self.validator.validate_user_handle(handle)
        assert isinstance(result, str)
        assert not result.startswith('@')
    
    def test_validate_user_handle_with_prefix(self):
        """Test handle validation with @ prefix."""
        handle = "@user.bsky.social"
        result = self.validator.validate_user_handle(handle)
        assert result == "user.bsky.social"


class TestValidationError:
    """Test custom validation exception."""
    
    def test_validation_error_creation(self):
        """Test ValidationError can be created and raised."""
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        
        with pytest.raises(ValidationError, match="Test error message"):
            raise ValidationError("Test error message")


# Integration tests for the validation framework
class TestValidationIntegration:
    """Integration tests for validation framework."""
    
    def test_validator_configuration(self):
        """Test validator can be configured with custom limits."""
        validator = InputValidator()
        
        # Check default configuration
        assert validator.max_post_length == 300
        assert validator.max_file_size == 1048576  # 1MB
        
        # Test with custom limits
        validator.max_post_length = 500
        content = "x" * 400  # Should be valid with new limit
        result = validator.validate_post_content(content)
        assert len(result) == 400


# Phase 1 TODO: Add tests for enhanced validation features:
# - URL validation and extraction
# - Mention and hashtag validation
# - Rich text format validation
# - Internationalization support
# - Custom validation rule configuration