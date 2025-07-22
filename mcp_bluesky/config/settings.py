"""Configuration management for Bluesky MCP Server.

Handles environment variables and configuration validation.
Enhanced version with YAML support for Phase 4.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field


# Project root for logging and other paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
LOG_FILE = PROJECT_ROOT / "bluesky-mcp.log"

# Default service URL
DEFAULT_SERVICE_URL = "https://bsky.social"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    posts_per_minute: int = 30
    follows_per_minute: int = 60
    likes_per_minute: int = 100
    reposts_per_minute: int = 60
    general_per_minute: int = 120
    media_per_minute: int = 20
    global_per_minute: int = 300


@dataclass
class MediaConfig:
    """Media processing configuration."""
    max_image_size: int = 1048576  # 1MB
    max_video_size: int = 52428800  # 50MB
    allowed_image_formats: list = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"
    ])
    allowed_video_formats: list = field(default_factory=lambda: [
        ".mp4", ".mov", ".avi", ".webm"
    ])
    auto_compress: bool = True
    jpeg_quality: int = 85
    webp_quality: int = 80
    max_image_dimension: int = 2048


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: str = str(LOG_FILE)
    rotation: str = "1 day"
    retention: str = "30 days"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"


@dataclass
class AuthConfig:
    """Authentication configuration."""
    identifier: Optional[str] = None
    app_password: Optional[str] = None
    service_url: str = DEFAULT_SERVICE_URL

    def __post_init__(self):
        """Load from environment if not provided."""
        if self.identifier is None:
            self.identifier = get_bluesky_identifier()
        if self.app_password is None:
            self.app_password = get_bluesky_app_password()
        if self.service_url == DEFAULT_SERVICE_URL:
            self.service_url = get_bluesky_service_url()


@dataclass
class Settings:
    """Main configuration class for Bluesky MCP Server.

    Supports both environment variables and YAML configuration.
    To be fully implemented in Phase 4.
    """
    auth: AuthConfig = field(default_factory=AuthConfig)
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)
    media: MediaConfig = field(default_factory=MediaConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Development settings
    debug: bool = False
    test_mode: bool = False

    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables."""
        return cls()

    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> 'Settings':
        """Load settings from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Settings instance

        Note:
            To be implemented in Phase 4.
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}

            # Parse configuration sections
            auth_config = AuthConfig(**config_data.get('authentication', {}))
            rate_config = RateLimitConfig(**config_data.get('rate_limits', {}))
            media_config = MediaConfig(**config_data.get('media', {}))
            logging_config = LoggingConfig(**config_data.get('logging', {}))

            return cls(
                auth=auth_config,
                rate_limits=rate_config,
                media=media_config,
                logging=logging_config,
                debug=config_data.get('debug', False),
                test_mode=config_data.get('test_mode', False)
            )

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return status.

        Returns:
            Dictionary with validation results
        """
        issues = []

        # Validate authentication
        if not self.auth.identifier:
            issues.append("Missing BLUESKY_IDENTIFIER")
        if not self.auth.app_password:
            issues.append("Missing BLUESKY_APP_PASSWORD")
        if not self.auth.service_url.startswith(('http://', 'https://')):
            issues.append("Invalid service URL format")

        # Validate rate limits
        if self.rate_limits.posts_per_minute <= 0:
            issues.append("Posts per minute must be positive")
        if self.rate_limits.global_per_minute <= 0:
            issues.append("Global rate limit must be positive")

        # Validate media settings
        if self.media.max_image_size <= 0:
            issues.append("Max image size must be positive")
        if self.media.max_video_size <= 0:
            issues.append("Max video size must be positive")

        # Validate logging
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level not in valid_levels:
            issues.append(f"Invalid log level. Must be one of: {valid_levels}")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'has_credentials': bool(self.auth.identifier and self.auth.app_password)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'authentication': {
                'identifier': self.auth.identifier,
                'has_password': bool(self.auth.app_password),
                'service_url': self.auth.service_url
            },
            'rate_limits': {
                'posts_per_minute': self.rate_limits.posts_per_minute,
                'follows_per_minute': self.rate_limits.follows_per_minute,
                'likes_per_minute': self.rate_limits.likes_per_minute,
                'reposts_per_minute': self.rate_limits.reposts_per_minute,
                'general_per_minute': self.rate_limits.general_per_minute,
                'media_per_minute': self.rate_limits.media_per_minute,
                'global_per_minute': self.rate_limits.global_per_minute
            },
            'media': {
                'max_image_size': self.media.max_image_size,
                'max_video_size': self.media.max_video_size,
                'allowed_image_formats': self.media.allowed_image_formats,
                'allowed_video_formats': self.media.allowed_video_formats,
                'auto_compress': self.media.auto_compress,
                'jpeg_quality': self.media.jpeg_quality,
                'webp_quality': self.media.webp_quality,
                'max_image_dimension': self.media.max_image_dimension
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'rotation': self.logging.rotation,
                'retention': self.logging.retention
            },
            'debug': self.debug,
            'test_mode': self.test_mode
        }

    def create_example_yaml(self, output_path: Union[str, Path]) -> None:
        """Create an example YAML configuration file.

        Args:
            output_path: Path where to save the example configuration
        """
        example_config = """# Bluesky MCP Server Configuration
# Copy this file and customize for your environment

authentication:
  identifier: "${BLUESKY_IDENTIFIER}"  # Your Bluesky handle
  app_password: "${BLUESKY_APP_PASSWORD}"  # Your Bluesky app password
  service_url: "https://bsky.social"

rate_limits:
  posts_per_minute: 30      # Conservative limit for posts
  follows_per_minute: 60    # Follows and unfollows
  likes_per_minute: 100     # Likes and unlikes
  reposts_per_minute: 60    # Reposts and unreposts
  general_per_minute: 120   # General API calls
  media_per_minute: 20      # Media uploads
  global_per_minute: 300    # Total requests across all categories

media:
  max_image_size: 1048576   # 1MB limit for images
  max_video_size: 52428800  # 50MB limit for videos
  allowed_image_formats:
    - ".jpg"
    - ".jpeg"
    - ".png"
    - ".gif"
    - ".webp"
    - ".bmp"
  allowed_video_formats:
    - ".mp4"
    - ".mov"
    - ".avi"
    - ".webm"
  auto_compress: true       # Automatically compress large media
  jpeg_quality: 85          # JPEG compression quality (1-100)
  webp_quality: 80          # WebP compression quality (1-100)
  max_image_dimension: 2048 # Maximum width/height for images

logging:
  level: "INFO"             # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/bluesky_mcp.log"
  rotation: "1 day"         # Log rotation interval
  retention: "30 days"      # Log retention period

# Development settings
debug: false
test_mode: false
"""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(example_config)


# Legacy functions for backward compatibility
def get_bluesky_identifier() -> Optional[str]:
    """Get Bluesky identifier from environment."""
    return os.environ.get("BLUESKY_IDENTIFIER")


def get_bluesky_app_password() -> Optional[str]:
    """Get Bluesky app password from environment."""
    return os.environ.get("BLUESKY_APP_PASSWORD")


def get_bluesky_service_url() -> str:
    """Get Bluesky service URL from environment, with default fallback."""
    return os.environ.get("BLUESKY_SERVICE_URL", DEFAULT_SERVICE_URL)


def has_required_credentials() -> bool:
    """Check if required Bluesky credentials are available."""
    return bool(get_bluesky_identifier() and get_bluesky_app_password())


def validate_configuration() -> dict:
    """Validate configuration and return status."""
    identifier = get_bluesky_identifier()
    password = get_bluesky_app_password()
    service_url = get_bluesky_service_url()

    return {
        "has_identifier": bool(identifier),
        "has_password": bool(password),
        "service_url": service_url,
        "is_configured": bool(identifier and password)
    }


# Global settings instance (lazy loading)
_global_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance.

    Returns:
        Settings instance (created from environment if not exists)
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings.from_env()
    return _global_settings


def load_settings_from_yaml(config_path: Union[str, Path]) -> Settings:
    """Load settings from YAML file and set as global.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Settings instance
    """
    global _global_settings
    _global_settings = Settings.from_yaml(config_path)
    return _global_settings


def reset_settings() -> None:
    """Reset global settings (useful for testing)."""
    global _global_settings
    _global_settings = None