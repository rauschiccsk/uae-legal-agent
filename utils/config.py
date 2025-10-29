from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Config(BaseModel):
    debug: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    timeout: int = Field(default=30)
    max_retries: int = Field(default=3)

    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('timeout must be positive')
        return v

    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError('max_retries must be non-negative')
        return v