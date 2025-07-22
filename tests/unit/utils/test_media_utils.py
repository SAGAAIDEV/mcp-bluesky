"""Unit tests for media processing utilities.

Tests for the media utilities framework implemented in Phase 3.
"""

import pytest
import base64
from pathlib import Path

from mcp_bluesky.utils.media_utils import (
    MediaInfo,
    MediaProcessor,
    validate_file_size,
    get_mime_type,
    is_supported_media_type,
    process_image_upload,
    process_video_upload
)


class TestMediaInfo:
    """Test MediaInfo dataclass."""
    
    def test_media_info_creation(self):
        """Test MediaInfo can be created."""
        info = MediaInfo(
            filename="test.jpg",
            mime_type="image/jpeg",
            size=1024,
            width=800,
            height=600
        )
        
        assert info.filename == "test.jpg"
        assert info.mime_type == "image/jpeg"
        assert info.size == 1024
        assert info.width == 800
        assert info.height == 600
    
    def test_is_image_property(self):
        """Test is_image property."""
        image_info = MediaInfo("test.jpg", "image/jpeg", 1024)
        video_info = MediaInfo("test.mp4", "video/mp4", 2048)
        
        assert image_info.is_image is True
        assert image_info.is_video is False
        assert video_info.is_image is False
        assert video_info.is_video is True
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        info = MediaInfo("test.jpg", "image/jpeg", 1024, width=800)
        result = info.to_dict()
        
        assert isinstance(result, dict)
        assert result['filename'] == "test.jpg"
        assert result['mime_type'] == "image/jpeg"
        assert result['size'] == 1024
        assert result['width'] == 800
        assert result['is_image'] is True
        assert result['is_video'] is False


class TestMediaProcessor:
    """Test MediaProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = MediaProcessor()
    
    def test_processor_initialization(self):
        """Test processor initializes with correct defaults."""
        assert self.processor.max_image_size == 1048576  # 1MB
        assert self.processor.max_video_size == 52428800  # 50MB
        assert '.jpg' in self.processor.allowed_image_formats
        assert '.mp4' in self.processor.allowed_video_formats
        assert self.processor.jpeg_quality == 85
    
    def test_validate_media_format_valid_image(self):
        """Test validation of valid image formats."""
        valid_cases = [
            ("image.jpg", b"x" * 1000),
            ("photo.PNG", b"x" * 2000),
            ("picture.webp", b"x" * 500),
        ]
        
        for filename, data in valid_cases:
            result = self.processor.validate_media_format(filename, data)
            assert result is True
    
    def test_validate_media_format_valid_video(self):
        """Test validation of valid video formats."""
        valid_cases = [
            ("video.mp4", b"x" * 10000),
            ("movie.MOV", b"x" * 20000),
        ]
        
        for filename, data in valid_cases:
            result = self.processor.validate_media_format(filename, data)
            assert result is True
    
    def test_validate_media_format_invalid_format(self):
        """Test validation rejects invalid formats."""
        invalid_cases = [
            ("document.pdf", b"x" * 1000),
            ("archive.zip", b"x" * 2000),
            ("script.exe", b"x" * 500),
        ]
        
        for filename, data in invalid_cases:
            with pytest.raises(ValueError, match="Format .* not allowed"):
                self.processor.validate_media_format(filename, data)
    
    def test_validate_media_format_image_too_large(self):
        """Test validation rejects oversized images."""
        large_data = b"x" * (1048576 + 1)  # Exceeds 1MB
        
        with pytest.raises(ValueError, match="Image size .* exceeds limit"):
            self.processor.validate_media_format("image.jpg", large_data)
    
    def test_validate_media_format_video_too_large(self):
        """Test validation rejects oversized videos."""
        large_data = b"x" * (52428800 + 1)  # Exceeds 50MB
        
        with pytest.raises(ValueError, match="Video size .* exceeds limit"):
            self.processor.validate_media_format("video.mp4", large_data)
    
    def test_get_media_info_image(self):
        """Test getting media info for images."""
        data = b"fake_image_data"
        info = self.processor.get_media_info("test.jpg", data)
        
        assert isinstance(info, MediaInfo)
        assert info.filename == "test.jpg"
        assert info.size == len(data)
        assert info.is_image is True
        assert "image" in info.mime_type
    
    def test_get_media_info_video(self):
        """Test getting media info for videos."""
        data = b"fake_video_data"
        info = self.processor.get_media_info("test.mp4", data)
        
        assert isinstance(info, MediaInfo)
        assert info.filename == "test.mp4"
        assert info.size == len(data)
        assert info.is_video is True
        assert "video" in info.mime_type
    
    def test_compress_image_basic(self):
        """Test basic image compression."""
        data = b"fake_image_data"
        filename = "test.jpg"
        
        # For now, this should just validate and return original data
        result = self.processor.compress_image(data, filename)
        assert result == data  # Placeholder implementation
    
    def test_process_video_basic(self):
        """Test basic video processing."""
        data = b"fake_video_data"
        filename = "test.mp4"
        
        # For now, this should just validate and return original data
        result = self.processor.process_video(data, filename)
        assert result == data  # Placeholder implementation
    
    def test_encode_decode_base64(self):
        """Test base64 encoding and decoding."""
        original_data = b"test data for encoding"
        
        # Encode
        encoded = self.processor.encode_media_base64(original_data)
        assert isinstance(encoded, str)
        
        # Decode
        decoded = self.processor.decode_media_base64(encoded)
        assert decoded == original_data
    
    def test_decode_invalid_base64(self):
        """Test decoding invalid base64 data."""
        invalid_data = "not_valid_base64!!!"
        
        with pytest.raises(ValueError, match="Invalid base64 data"):
            self.processor.decode_media_base64(invalid_data)
    
    def test_prepare_for_upload_image(self):
        """Test preparing image for upload."""
        data = b"fake_image_data"
        filename = "test.jpg"
        
        processed_data, media_info = self.processor.prepare_for_upload(data, filename)
        
        assert isinstance(media_info, MediaInfo)
        assert media_info.filename == filename
        assert media_info.is_image is True
        # For placeholder implementation, data should be unchanged
        assert processed_data == data
    
    def test_prepare_for_upload_video(self):
        """Test preparing video for upload."""
        data = b"fake_video_data"
        filename = "test.mp4"
        
        processed_data, media_info = self.processor.prepare_for_upload(data, filename)
        
        assert isinstance(media_info, MediaInfo)
        assert media_info.filename == filename
        assert media_info.is_video is True
        # For placeholder implementation, data should be unchanged
        assert processed_data == data
    
    def test_create_alt_text_placeholder(self):
        """Test alt text generation."""
        # Image alt text
        image_info = MediaInfo("photo.jpg", "image/jpeg", 1024)
        alt_text = self.processor.create_alt_text_placeholder(image_info)
        assert "Image:" in alt_text
        assert "photo.jpg" in alt_text
        
        # Video alt text
        video_info = MediaInfo("movie.mp4", "video/mp4", 2048, duration=30.0)
        alt_text = self.processor.create_alt_text_placeholder(video_info)
        assert "Video:" in alt_text
        assert "movie.mp4" in alt_text
        # Duration should be included if available
        if video_info.duration:
            assert "30.0s" in alt_text


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_validate_file_size_valid(self):
        """Test valid file size validation."""
        data = b"x" * 1000  # 1KB
        # Should not raise an exception
        validate_file_size(data, max_size=2000, media_type="image")
    
    def test_validate_file_size_invalid(self):
        """Test invalid file size validation."""
        data = b"x" * 2000  # 2KB
        with pytest.raises(ValueError, match="Image size .* exceeds limit"):
            validate_file_size(data, max_size=1000, media_type="image")
    
    def test_get_mime_type(self):
        """Test MIME type detection."""
        test_cases = [
            ("image.jpg", "image/jpeg"),
            ("photo.png", "image/png"),
            ("video.mp4", "video/mp4"),
            ("unknown.xyz", "chemical/x-xyz"),  # System MIME detection for .xyz files
        ]
        
        for filename, expected in test_cases:
            result = get_mime_type(filename)
            assert expected in result or result == expected
    
    def test_is_supported_media_type(self):
        """Test media type support checking."""
        supported_files = [
            "image.jpg",
            "photo.PNG",  # Case insensitive
            "video.mp4",
            "movie.MOV",
        ]
        
        unsupported_files = [
            "document.pdf",
            "archive.zip",
            "audio.mp3",
        ]
        
        for filename in supported_files:
            assert is_supported_media_type(filename) is True
        
        for filename in unsupported_files:
            assert is_supported_media_type(filename) is False


class TestProcessingFunctions:
    """Test high-level processing functions."""
    
    def test_process_image_upload_success(self):
        """Test successful image upload processing."""
        # Create test data
        original_data = b"fake_image_data"
        encoded_data = base64.b64encode(original_data).decode('utf-8')
        
        result = process_image_upload(encoded_data, "test.jpg")
        
        assert result['status'] == 'success'
        assert 'data' in result
        assert 'info' in result
        assert 'alt_text' in result
        
        # Verify info structure
        info = result['info']
        assert info['filename'] == "test.jpg"
        assert info['is_image'] is True
        assert info['size'] == len(original_data)
    
    def test_process_image_upload_invalid_base64(self):
        """Test image upload processing with invalid base64."""
        invalid_data = "not_valid_base64!!!"
        
        result = process_image_upload(invalid_data, "test.jpg")
        
        assert result['status'] == 'error'
        assert 'message' in result
        assert "Failed to process image" in result['message']
    
    def test_process_video_upload_success(self):
        """Test successful video upload processing."""
        # Create test data
        original_data = b"fake_video_data"
        encoded_data = base64.b64encode(original_data).decode('utf-8')
        
        result = process_video_upload(encoded_data, "test.mp4")
        
        assert result['status'] == 'success'
        assert 'data' in result
        assert 'info' in result
        assert 'alt_text' in result
        
        # Verify info structure
        info = result['info']
        assert info['filename'] == "test.mp4"
        assert info['is_video'] is True
        assert info['size'] == len(original_data)
    
    def test_process_video_upload_invalid_format(self):
        """Test video upload processing with invalid format."""
        # Create test data with invalid format
        original_data = b"fake_data"
        encoded_data = base64.b64encode(original_data).decode('utf-8')
        
        result = process_video_upload(encoded_data, "test.pdf")
        
        assert result['status'] == 'error'
        assert 'message' in result
        assert "Failed to process video" in result['message']


# Integration tests
class TestMediaUtilsIntegration:
    """Integration tests for media utilities."""
    
    def test_full_image_processing_pipeline(self):
        """Test complete image processing pipeline."""
        processor = MediaProcessor()
        
        # Create test image data
        test_data = b"fake_jpeg_data_" + b"x" * 1000
        filename = "test_image.jpg"
        
        # Step 1: Validate format
        assert processor.validate_media_format(filename, test_data) is True
        
        # Step 2: Get media info
        media_info = processor.get_media_info(filename, test_data)
        assert media_info.is_image is True
        
        # Step 3: Prepare for upload
        processed_data, final_info = processor.prepare_for_upload(test_data, filename)
        assert len(processed_data) > 0
        
        # Step 4: Create alt text
        alt_text = processor.create_alt_text_placeholder(final_info)
        assert len(alt_text) > 0
        
        # Step 5: Encode for transmission
        encoded = processor.encode_media_base64(processed_data)
        assert len(encoded) > 0
        
        # Step 6: Decode and verify
        decoded = processor.decode_media_base64(encoded)
        assert decoded == processed_data


# Phase 3 TODO: Add tests for:
# - PIL integration for actual image processing
# - FFmpeg integration for video processing
# - Image compression and optimization
# - Video transcoding and compression
# - Metadata extraction (EXIF, video info)
# - Thumbnail generation
# - Progressive image loading
# - Streaming video processing