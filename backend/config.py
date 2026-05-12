import os
from functools import lru_cache
from typing import List, Union, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Centralized application settings using Pydantic BaseSettings."""
    
    ENVIRONMENT: str = Field(
        default="development", 
        description="Current environment mode (e.g., development, production)"
    )
    
    API_HOST: str = Field(
        default="0.0.0.0", 
        description="Host address the API will bind to"
    )
    
    API_PORT: int = Field(
        default=8000, 
        description="Port number the API will listen on",
        ge=1,
        le=65535
    )
    
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="List of allowed CORS origins"
    )

    # Ollama Configuration
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Base URL for the Ollama API"
    )

    OLLAMA_MODEL: str = Field(
        default="phi3",
        description="Ollama model name to use"
    )

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./chatbot.db",
        description="Database connection URL"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Convert comma-separated string to a list of origins if necessary."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a singleton instance of Settings.
    Validates the presence of .env file in production.
    """
    settings = Settings()
    
    # Custom check for .env in production if needed
    if settings.ENVIRONMENT == "production" and not os.path.exists(".env"):
        # Note: In some production environments, variables are injected directly, 
        # so a missing .env isn't always an error. But per requirement:
        print("WARNING: .env file is missing in production environment!")
        
    return settings
