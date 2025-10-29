"""Tests for configuration management module."""
import os
import pytest
from pydantic import ValidationError
from utils.config import Settings


class TestSettings:
    """Test Settings class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings(_env_file=None)  # Ignore .env file for default values test
        
        assert settings.app_name == "MyApp"
        assert settings.app_env == "development"
        assert settings.debug is False
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.api_prefix == "/api/v1"
        assert settings.database_url == "sqlite:///./app.db"
        assert settings.secret_key == "changeme"
        assert settings.log_level == "INFO"
    
    def test_custom_values(self):
        """Test custom configuration values."""
        settings = Settings(
            app_name="TestApp",
            app_env="production",
            debug=True,
            api_port=9000,
            secret_key="supersecret"
        )
        
        assert settings.app_name == "TestApp"
        assert settings.app_env == "production"
        assert settings.debug is True
        assert settings.api_port == 9000
        assert settings.secret_key == "supersecret"
    
    def test_env_validation_valid(self):
        """Test valid environment values."""
        for env in ["development", "staging", "production"]:
            settings = Settings(app_env=env)
            assert settings.app_env == env
    
    def test_env_validation_invalid(self):
        """Test invalid environment value."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(app_env="invalid")
        
        assert "app_env must be one of" in str(exc_info.value)
    
    def test_log_level_validation_valid(self):
        """Test valid log level values."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level
        
        # Test case insensitivity
        settings = Settings(log_level="debug")
        assert settings.log_level == "DEBUG"
    
    def test_log_level_validation_invalid(self):
        """Test invalid log level value."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(log_level="INVALID")
        
        assert "log_level must be one of" in str(exc_info.value)
    
    def test_port_validation_valid(self):
        """Test valid port values."""
        settings = Settings(api_port=8080)
        assert settings.api_port == 8080
        
        settings = Settings(api_port=1)
        assert settings.api_port == 1
        
        settings = Settings(api_port=65535)
        assert settings.api_port == 65535
    
    def test_port_validation_invalid(self):
        """Test invalid port values."""
        with pytest.raises(ValidationError):
            Settings(api_port=0)
        
        with pytest.raises(ValidationError):
            Settings(api_port=65536)
        
        with pytest.raises(ValidationError):
            Settings(api_port=-1)
    
    def test_is_production(self):
        """Test is_production method."""
        settings = Settings(app_env="production")
        assert settings.is_production() is True
        
        settings = Settings(app_env="development")
        assert settings.is_production() is False
    
    def test_is_development(self):
        """Test is_development method."""
        settings = Settings(app_env="development")
        assert settings.is_development() is True
        
        settings = Settings(app_env="production")
        assert settings.is_development() is False
    
    def test_database_settings(self):
        """Test database configuration."""
        settings = Settings(
            database_url="postgresql://user:pass@localhost/db",
            db_echo=True,
            db_pool_size=10,
            db_max_overflow=20
        )
        
        assert settings.database_url == "postgresql://user:pass@localhost/db"
        assert settings.db_echo is True
        assert settings.db_pool_size == 10
        assert settings.db_max_overflow == 20
    
    def test_redis_settings(self):
        """Test Redis configuration."""
        settings = Settings(
            redis_url="redis://localhost:6379/0",
            redis_ttl=7200
        )
        
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.redis_ttl == 7200
    
    def test_cors_settings(self):
        """Test CORS configuration."""
        settings = Settings(
            cors_origins=["http://localhost:3000", "https://example.com"],
            cors_allow_credentials=False
        )
        
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins
        assert settings.cors_allow_credentials is False
    
    def test_file_upload_settings(self):
        """Test file upload configuration."""
        settings = Settings(
            max_upload_size=5242880,  # 5MB
            upload_dir="/tmp/uploads"
        )
        
        assert settings.max_upload_size == 5242880
        assert settings.upload_dir == "/tmp/uploads"
    
    def test_jwt_settings(self):
        """Test JWT configuration."""
        settings = Settings(
            jwt_algorithm="RS256",
            access_token_expire_minutes=60
        )
        
        assert settings.jwt_algorithm == "RS256"
        assert settings.access_token_expire_minutes == 60
    
    def test_env_file_loading(self, tmp_path, monkeypatch):
        """Test loading from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "APP_NAME=EnvApp\n"
            "API_PORT=9000\n"
            "DEBUG=true\n"
        )
        
        monkeypatch.chdir(tmp_path)
        settings = Settings()
        
        assert settings.app_name == "EnvApp"
        assert settings.api_port == 9000
        assert settings.debug is True
    
    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test case insensitive environment variables."""
        monkeypatch.setenv("app_name", "LowerCase")
        monkeypatch.setenv("API_PORT", "7000")
        
        settings = Settings()
        
        assert settings.app_name == "LowerCase"
        assert settings.api_port == 7000
    
    def test_type_coercion(self):
        """Test automatic type coercion."""
        settings = Settings(
            api_port="8080",  # String to int
            debug="true",  # String to bool
            db_pool_size="15"  # String to int
        )
        
        assert isinstance(settings.api_port, int)
        assert settings.api_port == 8080
        assert isinstance(settings.debug, bool)
        assert settings.debug is True
        assert isinstance(settings.db_pool_size, int)
        assert settings.db_pool_size == 15