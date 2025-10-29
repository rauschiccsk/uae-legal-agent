"""Configuration management using Pydantic settings."""
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4", description="Model to use")
    max_tokens: int = Field(default=150000, description="Maximum tokens")
    
    # Database Configuration
    database_url: Optional[str] = Field(
        default=None,
        description="Database connection URL"
    )
    
    # Application Configuration
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v_upper
    
    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max tokens is positive."""
        if v <= 0:
            raise ValueError("max_tokens must be positive")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


def load_settings() -> Settings:
    """Load and return application settings."""
    return Settings()