"""
Configuration management
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "8000"))
    
    # API Server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8002"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./legal_agent.db")
    
    # RAG
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "paraphrase-multilingual-mpnet-base-v2")
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/embeddings")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    class Config:
        env_file = ".env"


settings = Settings()
