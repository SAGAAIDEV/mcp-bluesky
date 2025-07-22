"""Media processing utilities for Bluesky MCP Server.

This module provides utilities for processing images and videos for Bluesky posts.
Framework ready for Phase 3 implementation.
"""

import io
import base64
import mimetypes
from typing import Optional, Tuple, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MediaInfo:
    """Information about a media file."""
    filename: str
    mime_type: str
    size: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # For videos
    
    @property
    def is_image(self) -> bool:
        """Check if media is an image."""
        return self.mime_type.startswith('image/')
    
    @property
    def is_video(self) -> bool:
        """Check if media is a video."""
        return self.mime_type.startswith('video/')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'filename': self.filename,
            'mime_type': self.mime_type,
            'size': self.size,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'is_image': self.is_image,
            'is_video': self.is_video
        }


class MediaProcessor:
    """Media processing utilities for Bluesky posts.
    
    Handles validation, compression, and format conversion.
    To be fully implemented in Phase 3.
    """
    
    def __init__(self):
        """Initialize media processor with Bluesky limits."""
        # Bluesky media limits
        self.max_image_size = 1048576  # 1MB for images
        self.max_video_size = 52428800  # 50MB for videos
        
        # Supported formats
        self.allowed_image_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'
        }
        self.allowed_video_formats = {
            '.mp4', '.mov', '.avi', '.webm'
        }
        
        # Compression settings
        self.jpeg_quality = 85
        self.webp_quality = 80
        self.max_image_dimension = 2048
    
    def validate_media_format(self, filename: str, data: bytes) -> bool:
        """Validate media file format and size.
        
        Args:
            filename: Name of the media file
            data: Media file data
            
        Returns:
            True if format and size are valid
            
        Raises:
            ValueError: If format or size is invalid
            
        Note:
            To be fully implemented in Phase 3.
        """
        # Get file extension
        file_ext = Path(filename).suffix.lower()
        
        # Check format
        if file_ext in self.allowed_image_formats:
            if len(data) > self.max_image_size:
                raise ValueError(f"Image size {len(data)} bytes exceeds limit of {self.max_image_size} bytes")
        elif file_ext in self.allowed_video_formats:
            if len(data) > self.max_video_size:
                raise ValueError(f"Video size {len(data)} bytes exceeds limit of {self.max_video_size} bytes")
        else:
            allowed_formats = self.allowed_image_formats.union(self.allowed_video_formats)
            raise ValueError(f"Format {file_ext} not allowed. Supported formats: {sorted(allowed_formats)}")
        
        return True
    
    def get_media_info(self, filename: str, data: bytes) -> MediaInfo:
        """Get information about media file.
        
        Args:
            filename: Name of the media file
            data: Media file data
            
        Returns:
            MediaInfo object with file details
            
        Note:
            To be fully implemented in Phase 3 with PIL/ffmpeg integration.
        """
        # Basic implementation - to be enhanced in Phase 3
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        info = MediaInfo(
            filename=filename,
            mime_type=mime_type,
            size=len(data)
        )
        
        # Placeholder for image/video analysis
        # In Phase 3, this will use PIL for images and ffmpeg for videos
        if info.is_image:
            # TODO: Extract image dimensions using PIL
            pass
        elif info.is_video:
            # TODO: Extract video info using ffmpeg
            pass
        
        return info
    
    def compress_image(self, data: bytes, filename: str, target_size: Optional[int] = None) -> bytes:
        """Compress image to reduce file size.
        
        Args:
            data: Image data
            filename: Image filename (for format detection)
            target_size: Target size in bytes (optional)
            
        Returns:
            Compressed image data
            
        Note:
            To be implemented in Phase 3 with PIL integration.
        """
        # Placeholder implementation - to be enhanced in Phase 3
        # This will use PIL for actual image compression
        
        # For now, just validate and return original data
        self.validate_media_format(filename, data)
        
        # TODO: Implement actual compression using PIL:
        # - Load image with PIL
        # - Resize if dimensions exceed max_image_dimension
        # - Compress with appropriate quality settings
        # - Convert to WebP if needed for better compression
        
        return data
    
    def process_video(self, data: bytes, filename: str) -> bytes:
        """Process video for Bluesky upload.
        
        Args:
            data: Video data
            filename: Video filename
            
        Returns:
            Processed video data
            
        Note:
            To be implemented in Phase 3 with ffmpeg integration.
        """
        # Placeholder implementation - to be enhanced in Phase 3
        self.validate_media_format(filename, data)
        
        # TODO: Implement video processing with ffmpeg:
        # - Validate video format and duration
        # - Compress if size exceeds limits
        # - Convert to MP4 if needed
        
        return data
    
    def encode_media_base64(self, data: bytes) -> str:
        """Encode media data as base64 string.
        
        Args:
            data: Media file data
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(data).decode('utf-8')
    
    def decode_media_base64(self, encoded_data: str) -> bytes:
        """Decode base64 media data.
        
        Args:
            encoded_data: Base64 encoded media data
            
        Returns:
            Decoded media data
            
        Raises:
            ValueError: If base64 data is invalid
        """
        try:
            return base64.b64decode(encoded_data)
        except Exception as e:
            raise ValueError(f"Invalid base64 data: {e}")
    
    def prepare_for_upload(self, data: bytes, filename: str, 
                          compress: bool = True) -> Tuple[bytes, MediaInfo]:
        """Prepare media for Bluesky upload.
        
        Args:
            data: Media file data
            filename: Media filename
            compress: Whether to compress the media
            
        Returns:
            Tuple of (processed_data, media_info)
            
        Note:
            To be fully implemented in Phase 3.
        """
        # Get media information
        media_info = self.get_media_info(filename, data)
        
        # Process based on media type
        if media_info.is_image and compress:
            processed_data = self.compress_image(data, filename)
        elif media_info.is_video:
            processed_data = self.process_video(data, filename)
        else:
            # Just validate
            self.validate_media_format(filename, data)
            processed_data = data
        
        # Update media info if size changed
        if len(processed_data) != len(data):
            media_info.size = len(processed_data)
        
        return processed_data, media_info
    
    def create_alt_text_placeholder(self, media_info: MediaInfo) -> str:
        """Create placeholder alt text for accessibility.
        
        Args:
            media_info: Media information
            
        Returns:
            Placeholder alt text
            
        Note:
            In Phase 3, this could be enhanced with AI-generated descriptions.
        """
        if media_info.is_image:
            return f"Image: {media_info.filename}"
        elif media_info.is_video:
            duration_text = ""
            if media_info.duration:
                duration_text = f" ({media_info.duration:.1f}s)"
            return f"Video: {media_info.filename}{duration_text}"
        else:
            return f"Media: {media_info.filename}"


def validate_file_size(data: bytes, max_size: int, media_type: str = "file") -> None:
    """Validate file size against limits.
    
    Args:
        data: File data
        max_size: Maximum allowed size in bytes
        media_type: Type of media for error message
        
    Raises:
        ValueError: If file exceeds size limit
    """
    if len(data) > max_size:
        size_mb = len(data) / 1024 / 1024
        limit_mb = max_size / 1024 / 1024
        raise ValueError(f"{media_type.title()} size {size_mb:.1f}MB exceeds limit of {limit_mb:.1f}MB")


def get_mime_type(filename: str) -> str:
    """Get MIME type for a file.
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME type string
    """
    mime_type = mimetypes.guess_type(filename)[0]
    if mime_type is None:
        return 'application/octet-stream'
    return mime_type


def is_supported_media_type(filename: str) -> bool:
    """Check if media type is supported by Bluesky.
    
    Args:
        filename: Name of the media file
        
    Returns:
        True if media type is supported
    """
    processor = MediaProcessor()
    file_ext = Path(filename).suffix.lower()
    
    return (file_ext in processor.allowed_image_formats or 
            file_ext in processor.allowed_video_formats)


# Utility functions for common operations
def process_image_upload(image_data: str, filename: str) -> Dict[str, Any]:
    """Process image upload data.
    
    Args:
        image_data: Base64 encoded image data
        filename: Image filename
        
    Returns:
        Dictionary with processed image info and data
        
    Note:
        To be enhanced in Phase 3.
    """
    processor = MediaProcessor()
    
    try:
        # Decode base64 data
        data = processor.decode_media_base64(image_data)
        
        # Process the image
        processed_data, media_info = processor.prepare_for_upload(data, filename)
        
        # Re-encode if processed
        final_data = processor.encode_media_base64(processed_data)
        
        return {
            'status': 'success',
            'data': final_data,
            'info': media_info.to_dict(),
            'alt_text': processor.create_alt_text_placeholder(media_info)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to process image: {e}"
        }


def process_video_upload(video_data: str, filename: str) -> Dict[str, Any]:
    """Process video upload data.
    
    Args:
        video_data: Base64 encoded video data
        filename: Video filename
        
    Returns:
        Dictionary with processed video info and data
        
    Note:
        To be enhanced in Phase 3.
    """
    processor = MediaProcessor()
    
    try:
        # Decode base64 data
        data = processor.decode_media_base64(video_data)
        
        # Process the video
        processed_data, media_info = processor.prepare_for_upload(data, filename)
        
        # Re-encode if processed
        final_data = processor.encode_media_base64(processed_data)
        
        return {
            'status': 'success',
            'data': final_data,
            'info': media_info.to_dict(),
            'alt_text': processor.create_alt_text_placeholder(media_info)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to process video: {e}"
        }