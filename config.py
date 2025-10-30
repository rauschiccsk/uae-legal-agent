from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """UAE Legal Agent Configuration"""
    
    # Project root
    PROJECT_ROOT: Path = Path(__file__).parent
    
    # Claude API Settings
    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TEMPERATURE: float = 0.7
    
    # ChromaDB Settings
    CHROMA_PERSIST_DIRECTORY: str = "data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "uae_legal_docs"
    
    # Paths (relative to project root)
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"
    DOCUMENTS_DIR: str = "data/documents"
    
    # Application Settings
    APP_LANGUAGE: str = "en"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute path from project root"""
        return self.PROJECT_ROOT / relative_path
    
    @property
    def chroma_persist_path(self) -> Path:
        return self.get_absolute_path(self.CHROMA_PERSIST_DIRECTORY)
    
    @property
    def data_path(self) -> Path:
        return self.get_absolute_path(self.DATA_DIR)
    
    @property
    def logs_path(self) -> Path:
        return self.get_absolute_path(self.LOGS_DIR)
    
    @property
    def documents_path(self) -> Path:
        return self.get_absolute_path(self.DOCUMENTS_DIR)


settings = Settings()