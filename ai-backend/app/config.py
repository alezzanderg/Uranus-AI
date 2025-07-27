"""
Configuration settings for the AI Assistant Backend.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_name: str = "AI Assistant Backend"
    version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # CORS Configuration
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "vscode-file://vscode-app"
    ]
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            if isinstance(v, str):
                return json.loads(v)
            return v
        raise ValueError(v)
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2048
    openai_temperature: float = 0.7
    
    # Database Configuration
    database_url: str = "sqlite:///./ai_assistant.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting Configuration
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "ai_assistant.log"
    
    # Context Configuration
    max_context_length: int = 8000
    max_file_size_mb: int = 1
    max_conversation_history: int = 50
    
    # WebSocket Configuration
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the current settings instance."""
    return settings

