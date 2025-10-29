"""Configuration management for UAE Legal Agent.

This module provides configuration management using Pydantic for validation
and python-dotenv for environment variable loading.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration with validation.
    
    Loads configuration from environment variables with optional .env file support.
    All settings have sensible defaults for development.
    """
    
    # API Configuration
    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API key for Claude access"
    )
    
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model identifier to use"
    )
    
    # Application Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode for verbose logging"
    )
    
    # Directory Configuration
    data_dir: Path = Field(
        default=Path("./data"),
        description="Directory containing legal documents"
    )
    
    vector_store_path: Path = Field(
        default=Path("./vector_store"),
        description="Path to vector store directory"
    )
    
    # RAG Configuration
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Size of text chunks for document processing"
    )
    
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=1000,
        description="Overlap between consecutive chunks"
    )
    
    top_k_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of top results to retrieve from vector search"
    )
    
    @field_validator("anthropic_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is not empty."""
        if not v or not v.strip():
            raise ValueError("ANTHROPIC_API_KEY cannot be empty")
        return v.strip()
    
    @field_validator("claude_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate Claude model identifier format."""
        if not v.startswith("claude-"):
            raise ValueError("Model must start with 'claude-'")
        return v
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Ensure chunk overlap is less than chunk size."""
        chunk_size = info.data.get("chunk_size", 1000)
        if v >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v
    
    @field_validator("data_dir", "vector_store_path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """Ensure paths are absolute and create if needed."""
        path = Path(v).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    def __str__(self) -> str:
        """String representation (hides API key)."""
        return (
            f"Config(model={self.claude_model}, "
            f"debug={self.debug}, "
            f"data_dir={self.data_dir}, "
            f"api_key={'*' * 8})"
        )


def load_config(env_file: Optional[str] = None) -> Config:
    """Load configuration from environment variables.
    
    Args:
        env_file: Optional path to .env file. If None, uses default .env
        
    Returns:
        Validated Config instance
        
    Raises:
        ValidationError: If configuration is invalid
    """
    if env_file:
        return Config(_env_file=env_file)
    return Config()


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance (singleton pattern).
    
    Returns:
        Config: Application configuration
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(env_file: Optional[str] = None) -> Config:
    """Reload configuration from environment.
    
    Useful for testing or when environment changes.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        New Config instance
    """
    global _config
    _config = load_config(env_file)
    return _config