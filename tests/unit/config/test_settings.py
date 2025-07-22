"""Unit tests for configuration settings.

Tests for the enhanced configuration system implemented in Phase 4.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from mcp_bluesky.config.settings import (
    Settings,
    AuthConfig,
    RateLimitConfig,
    MediaConfig,
    LoggingConfig,
    get_bluesky_identifier,
    get_bluesky_app_password,
    get_bluesky_service_url,
    has_required_credentials,
    validate_configuration,
    get_settings,
    load_settings_from_yaml,
    reset_settings,
    DEFAULT_SERVICE_URL
)


class TestAuthConfig:
    """Test AuthConfig dataclass."""
    
    def test_auth_config_creation(self):
        """Test AuthConfig can be created."""
        config = AuthConfig(
            identifier="test.bsky.social",
            app_password="test-password",
            service_url="https://test.bsky.social"
        )
        
        assert config.identifier == "test.bsky.social"
        assert config.app_password == "test-password"
        assert config.service_url == "https://test.bsky.social"
    
    @patch.dict(os.environ, {
        'BLUESKY_IDENTIFIER': 'env.bsky.social',
        'BLUESKY_APP_PASSWORD': 'env-password',
        'BLUESKY_SERVICE_URL': 'https://env.bsky.social'
    })
    def test_auth_config_from_env(self):
        """Test AuthConfig loads from environment."""
        config = AuthConfig()
        
        assert config.identifier == "env.bsky.social"
        assert config.app_password == "env-password"
        assert config.service_url == "https://env.bsky.social"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_auth_config_defaults(self):
        """Test AuthConfig uses defaults when env vars not set."""
        config = AuthConfig()
        
        assert config.identifier is None
        assert config.app_password is None
        assert config.service_url == DEFAULT_SERVICE_URL


class TestRateLimitConfig:
    """Test RateLimitConfig dataclass."""
    
    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default values."""
        config = RateLimitConfig()
        
        assert config.posts_per_minute == 30
        assert config.follows_per_minute == 60
        assert config.likes_per_minute == 100
        assert config.general_per_minute == 120
        assert config.global_per_minute == 300
    
    def test_rate_limit_config_custom(self):
        """Test RateLimitConfig with custom values."""
        config = RateLimitConfig(
            posts_per_minute=20,
            general_per_minute=100
        )
        
        assert config.posts_per_minute == 20
        assert config.general_per_minute == 100
        # Other values should use defaults
        assert config.follows_per_minute == 60


class TestMediaConfig:
    """Test MediaConfig dataclass."""
    
    def test_media_config_defaults(self):
        """Test MediaConfig default values."""
        config = MediaConfig()
        
        assert config.max_image_size == 1048576  # 1MB
        assert config.max_video_size == 52428800  # 50MB
        assert config.auto_compress is True
        assert config.jpeg_quality == 85
        assert ".jpg" in config.allowed_image_formats
        assert ".mp4" in config.allowed_video_formats
    
    def test_media_config_custom(self):
        """Test MediaConfig with custom values."""
        config = MediaConfig(
            max_image_size=2097152,  # 2MB
            auto_compress=False,
            jpeg_quality=95
        )
        
        assert config.max_image_size == 2097152
        assert config.auto_compress is False
        assert config.jpeg_quality == 95


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.rotation == "1 day"
        assert config.retention == "30 days"
        assert "{time:" in config.format  # Check format string structure


class TestSettings:
    """Test Settings main configuration class."""
    
    def test_settings_creation(self):
        """Test Settings can be created with defaults."""
        settings = Settings()
        
        assert isinstance(settings.auth, AuthConfig)
        assert isinstance(settings.rate_limits, RateLimitConfig)
        assert isinstance(settings.media, MediaConfig)
        assert isinstance(settings.logging, LoggingConfig)
        assert settings.debug is False
        assert settings.test_mode is False
    
    @patch.dict(os.environ, {
        'BLUESKY_IDENTIFIER': 'test.bsky.social',
        'BLUESKY_APP_PASSWORD': 'test-password'
    })
    def test_settings_from_env(self):
        """Test Settings.from_env() method."""
        settings = Settings.from_env()
        
        assert settings.auth.identifier == "test.bsky.social"
        assert settings.auth.app_password == "test-password"
    
    def test_settings_validate_valid(self):
        """Test validation of valid settings."""
        settings = Settings()
        settings.auth.identifier = "test.bsky.social"
        settings.auth.app_password = "test-password"
        
        result = settings.validate()
        
        assert result['is_valid'] is True
        assert result['has_credentials'] is True
        assert len(result['issues']) == 0
    
    def test_settings_validate_missing_credentials(self):
        """Test validation with missing credentials."""
        settings = Settings()
        # Leave credentials as None
        
        result = settings.validate()
        
        assert result['is_valid'] is False
        assert result['has_credentials'] is False
        assert any("BLUESKY_IDENTIFIER" in issue for issue in result['issues'])
        assert any("BLUESKY_APP_PASSWORD" in issue for issue in result['issues'])
    
    def test_settings_validate_invalid_service_url(self):
        """Test validation with invalid service URL."""
        settings = Settings()
        settings.auth.identifier = "test.bsky.social"
        settings.auth.app_password = "test-password"
        settings.auth.service_url = "invalid-url"
        
        result = settings.validate()
        
        assert result['is_valid'] is False
        assert any("service URL" in issue for issue in result['issues'])
    
    def test_settings_validate_invalid_rate_limits(self):
        """Test validation with invalid rate limits."""
        settings = Settings()
        settings.auth.identifier = "test.bsky.social"
        settings.auth.app_password = "test-password"
        settings.rate_limits.posts_per_minute = 0  # Invalid
        
        result = settings.validate()
        
        assert result['is_valid'] is False
        assert any("Posts per minute" in issue for issue in result['issues'])
    
    def test_settings_validate_invalid_log_level(self):
        """Test validation with invalid log level."""
        settings = Settings()
        settings.auth.identifier = "test.bsky.social"
        settings.auth.app_password = "test-password"
        settings.logging.level = "INVALID"
        
        result = settings.validate()
        
        assert result['is_valid'] is False
        assert any("log level" in issue for issue in result['issues'])
    
    def test_settings_to_dict(self):
        """Test settings conversion to dictionary."""
        settings = Settings()
        settings.auth.identifier = "test.bsky.social"
        
        result = settings.to_dict()
        
        assert isinstance(result, dict)
        assert 'authentication' in result
        assert 'rate_limits' in result
        assert 'media' in result
        assert 'logging' in result
        assert result['authentication']['identifier'] == "test.bsky.social"
        assert result['authentication']['has_password'] is False  # No password set
    
    def test_create_example_yaml(self):
        """Test creating example YAML configuration."""
        settings = Settings()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            settings.create_example_yaml(temp_path)
            
            # Verify file was created and has content
            with open(temp_path, 'r') as f:
                content = f.read()
            
            assert "authentication:" in content
            assert "rate_limits:" in content
            assert "media:" in content
            assert "logging:" in content
            assert "BLUESKY_IDENTIFIER" in content
            
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestYAMLConfiguration:
    """Test YAML configuration loading."""
    
    def test_from_yaml_valid_config(self):
        """Test loading valid YAML configuration."""
        yaml_content = """
authentication:
  identifier: "yaml.bsky.social"
  app_password: "yaml-password"
  service_url: "https://yaml.bsky.social"

rate_limits:
  posts_per_minute: 20
  general_per_minute: 100

media:
  max_image_size: 2097152
  auto_compress: false

logging:
  level: "DEBUG"

debug: true
test_mode: true
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            settings = Settings.from_yaml(temp_path)
            
            assert settings.auth.identifier == "yaml.bsky.social"
            assert settings.auth.app_password == "yaml-password"
            assert settings.rate_limits.posts_per_minute == 20
            assert settings.media.max_image_size == 2097152
            assert settings.media.auto_compress is False
            assert settings.logging.level == "DEBUG"
            assert settings.debug is True
            assert settings.test_mode is True
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_from_yaml_missing_file(self):
        """Test loading from non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            Settings.from_yaml("non_existent_file.yaml")
    
    def test_from_yaml_invalid_yaml(self):
        """Test loading invalid YAML configuration."""
        invalid_yaml = """
invalid: yaml: content:
  - this is not valid YAML
    - because of indentation
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid YAML"):
                Settings.from_yaml(temp_path)
                
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_from_yaml_partial_config(self):
        """Test loading YAML with only partial configuration."""
        partial_yaml = """
authentication:
  identifier: "partial.bsky.social"

rate_limits:
  posts_per_minute: 15
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(partial_yaml)
            temp_path = f.name
        
        try:
            settings = Settings.from_yaml(temp_path)
            
            # Specified values should be loaded
            assert settings.auth.identifier == "partial.bsky.social"
            assert settings.rate_limits.posts_per_minute == 15
            
            # Unspecified values should use defaults
            assert settings.rate_limits.follows_per_minute == 60  # Default
            assert settings.media.max_image_size == 1048576  # Default
            
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestLegacyFunctions:
    """Test legacy compatibility functions."""
    
    @patch.dict(os.environ, {'BLUESKY_IDENTIFIER': 'legacy.bsky.social'})
    def test_get_bluesky_identifier(self):
        """Test legacy get_bluesky_identifier function."""
        result = get_bluesky_identifier()
        assert result == "legacy.bsky.social"
    
    @patch.dict(os.environ, {'BLUESKY_APP_PASSWORD': 'legacy-password'})
    def test_get_bluesky_app_password(self):
        """Test legacy get_bluesky_app_password function."""
        result = get_bluesky_app_password()
        assert result == "legacy-password"
    
    @patch.dict(os.environ, {'BLUESKY_SERVICE_URL': 'https://legacy.bsky.social'})
    def test_get_bluesky_service_url(self):
        """Test legacy get_bluesky_service_url function."""
        result = get_bluesky_service_url()
        assert result == "https://legacy.bsky.social"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_bluesky_service_url_default(self):
        """Test legacy get_bluesky_service_url returns default."""
        result = get_bluesky_service_url()
        assert result == DEFAULT_SERVICE_URL
    
    @patch.dict(os.environ, {
        'BLUESKY_IDENTIFIER': 'test.bsky.social',
        'BLUESKY_APP_PASSWORD': 'test-password'
    })
    def test_has_required_credentials_true(self):
        """Test has_required_credentials returns True when credentials exist."""
        assert has_required_credentials() is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_has_required_credentials_false(self):
        """Test has_required_credentials returns False when credentials missing."""
        assert has_required_credentials() is False
    
    @patch.dict(os.environ, {
        'BLUESKY_IDENTIFIER': 'test.bsky.social',
        'BLUESKY_APP_PASSWORD': 'test-password'
    })
    def test_validate_configuration(self):
        """Test legacy validate_configuration function."""
        result = validate_configuration()
        
        assert result['has_identifier'] is True
        assert result['has_password'] is True
        assert result['is_configured'] is True
        assert result['service_url'] == DEFAULT_SERVICE_URL


class TestGlobalSettings:
    """Test global settings management."""
    
    def setup_method(self):
        """Reset global settings before each test."""
        reset_settings()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_settings()
    
    @patch.dict(os.environ, {'BLUESKY_IDENTIFIER': 'global.bsky.social'})
    def test_get_settings_singleton(self):
        """Test get_settings returns same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
        assert settings1.auth.identifier == "global.bsky.social"
    
    def test_load_settings_from_yaml(self):
        """Test loading settings from YAML file sets global instance."""
        yaml_content = """
authentication:
  identifier: "yaml_global.bsky.social"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            settings = load_settings_from_yaml(temp_path)
            global_settings = get_settings()
            
            # Should be the same instance
            assert settings is global_settings
            assert settings.auth.identifier == "yaml_global.bsky.social"
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_reset_settings(self):
        """Test resetting global settings."""
        # Get initial settings
        settings1 = get_settings()
        
        # Reset
        reset_settings()
        
        # Get settings again - should be new instance
        settings2 = get_settings()
        assert settings1 is not settings2


# Integration tests
class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    @patch.dict(os.environ, {
        'BLUESKY_IDENTIFIER': 'integration.bsky.social',
        'BLUESKY_APP_PASSWORD': 'integration-password'
    })
    def test_full_configuration_flow(self):
        """Test complete configuration loading and validation flow."""
        # Create settings from environment
        settings = Settings.from_env()
        
        # Validate
        validation = settings.validate()
        assert validation['is_valid'] is True
        
        # Convert to dict
        config_dict = settings.to_dict()
        assert config_dict['authentication']['identifier'] == "integration.bsky.social"
        
        # Test global settings
        reset_settings()
        global_settings = get_settings()
        assert global_settings.auth.identifier == "integration.bsky.social"


# Phase 4 TODO: Add tests for:
# - YAML validation and schema checking
# - Configuration file watching and hot reloading
# - Environment variable interpolation in YAML
# - Configuration profiles (dev, staging, prod)
# - Secrets management integration
# - Configuration migration utilities