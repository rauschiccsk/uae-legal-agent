"""Configuration management module using Pydantic BaseSettings."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Centralized application settings."""

    # Application
    app_name: str = Field(default="UAE Legal Agent", description="Application name")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Debug mode")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")

    # Database
    database_url: str = Field(default="sqlite:///./app.db", description="Database connection URL")
    db_echo: bool = Field(default=False, description="Echo SQL queries")
    db_pool_size: int = Field(default=5, description="Database connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")

    # Security
    secret_key: str = Field(default="changeme", description="Secret key for encryption")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")

    # Redis
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    redis_ttl: int = Field(default=3600, description="Redis cache TTL in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # CORS
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")

    # File Upload
    max_upload_size: int = Field(default=10485760, description="Max upload size in bytes (10MB)")
    upload_dir: str = Field(default="./uploads", description="Upload directory")

    # Claude API Settings
    anthropic_api_key: str = Field(default="", description="Anthropic API key for Claude")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    claude_max_tokens: int = Field(default=4096, description="Maximum tokens for Claude response")
    claude_temperature: float = Field(default=0.7, description="Claude temperature (0.0-1.0)")

    # Document Processing
    data_dir: str = Field(default="./data", description="Directory for legal documents")
    vector_store_path: str = Field(default="./vector_store", description="Path for vector store")
    chunk_size: int = Field(default=1000, description="Document chunk size for processing")
    chunk_overlap: int = Field(default=200, description="Overlap between document chunks")

    # RAG Settings
    embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model for RAG")
    top_k_results: int = Field(default=5, description="Number of top results to retrieve")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity score for results")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v):
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

    @field_validator("api_port")
    @classmethod
    def validate_port(cls, v):
        """Validate port range."""
        if not 1 <= v <= 65535:
            raise ValueError("api_port must be between 1 and 65535")
        return v

    @field_validator("claude_temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate Claude temperature range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("claude_temperature must be between 0.0 and 1.0")
        return v

    @field_validator("similarity_threshold")
    @classmethod
    def validate_similarity(cls, v):
        """Validate similarity threshold range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        return v

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"


# Global settings instance
settings = Settings()