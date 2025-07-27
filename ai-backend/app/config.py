"""
Configuration management for Uranus-AI Backend
Now uses PostgreSQL for configuration storage with .env fallback
"""

import os
import logging
from typing import List, Optional, Any
from pydantic import BaseSettings, Field
from functools import lru_cache

# Import database components (with fallback if not available)
try:
    from .database.config_service import ConfigService
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    ConfigService = None

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with PostgreSQL integration
    Falls back to environment variables if database is not available
    """
    
    # Core Application
    app_name: str = Field(default="Uranus-AI Backend", description="Application name")
    version: str = Field(default="1.2.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default="logs/uranus-ai.log", description="Log file path")
    
    # Database
    database_url: str = Field(
        default="postgresql://neondb_owner:npg_btfS8wXgFjl7@ep-rapid-sea-adxzz6h8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
        description="PostgreSQL database URL"
    )
    
    # CORS
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "vscode-file://vscode-app", "http://localhost:8080"],
        description="CORS allowed origins"
    )
    
    # AI Configuration (fallback values)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    openai_max_tokens: int = Field(default=2048, description="Max tokens for OpenAI")
    openai_temperature: float = Field(default=0.7, description="Temperature for OpenAI")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", description="Default Anthropic model")
    
    # Google
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    google_model: str = Field(default="gemini-pro", description="Default Google model")
    
    # xAI
    xai_api_key: Optional[str] = Field(default=None, description="xAI API key")
    xai_model: str = Field(default="grok-beta", description="Default xAI model")
    
    # DeepSeek
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API key")
    deepseek_model: str = Field(default="deepseek-coder", description="Default DeepSeek model")
    
    # Mistral
    mistral_api_key: Optional[str] = Field(default=None, description="Mistral API key")
    mistral_model: str = Field(default="mistral-large-latest", description="Default Mistral model")
    
    # Cohere
    cohere_api_key: Optional[str] = Field(default=None, description="Cohere API key")
    cohere_model: str = Field(default="command-r-plus", description="Default Cohere model")
    
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434/v1", description="Ollama base URL")
    ollama_model: str = Field(default="llama2", description="Default Ollama model")
    
    # Multi-Model Configuration
    default_model: str = Field(default="gpt-4", description="Default model to use")
    fallback_models: List[str] = Field(
        default=["gpt-3.5-turbo", "claude-3-haiku", "gemini-pro"],
        description="Fallback models"
    )
    enable_model_switching: bool = Field(default=True, description="Enable model switching")
    enable_auto_fallback: bool = Field(default=True, description="Enable auto fallback")
    enable_cost_optimization: bool = Field(default=False, description="Enable cost optimization")
    
    # Features
    enable_streaming: bool = Field(default=True, description="Enable streaming")
    enable_function_calling: bool = Field(default=True, description="Enable function calling")
    enable_vision_models: bool = Field(default=True, description="Enable vision models")
    enable_response_caching: bool = Field(default=True, description="Enable response caching")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_requests_per_hour: int = Field(default=1000, description="Rate limit per hour")
    max_concurrent_requests: int = Field(default=10, description="Max concurrent requests")
    request_timeout_seconds: int = Field(default=60, description="Request timeout")
    
    # Context and History
    max_context_length: int = Field(default=8000, description="Max context length")
    max_conversation_history: int = Field(default=20, description="Max conversation history")
    
    # Security
    jwt_secret_key: Optional[str] = Field(default=None, description="JWT secret key")
    enable_api_key_auth: bool = Field(default=False, description="Enable API key auth")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    
    # Caching
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL")
    redis_url: Optional[str] = Field(default=None, description="Redis URL")
    
    # Monitoring
    enable_usage_tracking: bool = Field(default=True, description="Enable usage tracking")
    enable_performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    enable_error_reporting: bool = Field(default=True, description="Enable error reporting")
    
    # Database-specific settings
    use_database_config: bool = Field(default=True, description="Use database for configuration")
    migrate_env_on_startup: bool = Field(default=True, description="Migrate .env to database on startup")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize database configuration if available
        if DATABASE_AVAILABLE and self.use_database_config:
            self._load_from_database()
    
    def _load_from_database(self):
        """Load configuration from PostgreSQL database"""
        try:
            config_service = ConfigService()
            
            # Get all configurations from database
            db_configs = config_service.get_all_configs(include_secrets=True)
            
            if db_configs:
                logger.info(f"📊 Loaded {len(db_configs)} configurations from database")
                
                # Map database configs to settings attributes
                config_mapping = {
                    "server.host": "host",
                    "server.port": "port",
                    "server.debug": "debug",
                    "server.log_level": "log_level",
                    "server.cors_origins": "backend_cors_origins",
                    
                    "ai.default_model": "default_model",
                    "ai.fallback_models": "fallback_models",
                    "ai.enable_fallback": "enable_auto_fallback",
                    "ai.enable_model_switching": "enable_model_switching",
                    "ai.cost_optimization": "enable_cost_optimization",
                    
                    "features.streaming": "enable_streaming",
                    "features.function_calling": "enable_function_calling",
                    "features.vision_models": "enable_vision_models",
                    "features.response_caching": "enable_response_caching",
                    
                    "limits.rate_per_minute": "rate_limit_requests_per_minute",
                    "limits.rate_per_hour": "rate_limit_requests_per_hour",
                    "limits.max_concurrent": "max_concurrent_requests",
                    "limits.request_timeout": "request_timeout_seconds",
                    
                    "security.jwt_secret": "jwt_secret_key",
                    "security.api_key_auth": "enable_api_key_auth",
                    "security.api_key": "api_key",
                    
                    "cache.ttl": "cache_ttl_seconds",
                    "database.redis_url": "redis_url",
                    
                    "monitoring.usage_tracking": "enable_usage_tracking",
                    "monitoring.performance": "enable_performance_monitoring",
                    "monitoring.error_reporting": "enable_error_reporting",
                }
                
                # Apply database configurations
                for db_key, attr_name in config_mapping.items():
                    if db_key in db_configs:
                        setattr(self, attr_name, db_configs[db_key])
                
                # Load API keys
                self._load_api_keys_from_database(config_service)
                
            else:
                logger.warning("⚠️ No configurations found in database, using environment variables")
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration from database: {e}")
            logger.info("📁 Falling back to environment variables")
    
    def _load_api_keys_from_database(self, config_service: ConfigService):
        """Load API keys from database"""
        try:
            api_key_mapping = {
                "openai": "openai_api_key",
                "anthropic": "anthropic_api_key",
                "google": "google_api_key",
                "xai": "xai_api_key",
                "deepseek": "deepseek_api_key",
                "mistral": "mistral_api_key",
                "cohere": "cohere_api_key",
            }
            
            for provider, attr_name in api_key_mapping.items():
                api_key = config_service.get_api_key(provider)
                if api_key:
                    setattr(self, attr_name, api_key)
                    logger.debug(f"🔐 Loaded API key for {provider}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load API keys from database: {e}")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        if DATABASE_AVAILABLE and self.use_database_config:
            try:
                config_service = ConfigService()
                return config_service.get_api_key(provider)
            except Exception as e:
                logger.error(f"Failed to get API key for {provider} from database: {e}")
        
        # Fallback to environment variables
        provider_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "xai": self.xai_api_key,
            "deepseek": self.deepseek_api_key,
            "mistral": self.mistral_api_key,
            "cohere": self.cohere_api_key,
        }
        
        return provider_mapping.get(provider)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value from database or fallback to attribute"""
        if DATABASE_AVAILABLE and self.use_database_config:
            try:
                config_service = ConfigService()
                return config_service.get_config(key, default)
            except Exception as e:
                logger.error(f"Failed to get config {key} from database: {e}")
        
        # Fallback to attribute
        attr_name = key.replace(".", "_").lower()
        return getattr(self, attr_name, default)
    
    def set_config_value(self, key: str, value: Any, category: str = "general") -> bool:
        """Set configuration value in database"""
        if DATABASE_AVAILABLE and self.use_database_config:
            try:
                config_service = ConfigService()
                return config_service.set_config(key, value, category)
            except Exception as e:
                logger.error(f"Failed to set config {key} in database: {e}")
                return False
        
        return False
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary"""
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__fields__.keys()
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Backward compatibility
def get_config():
    """Backward compatibility function"""
    return get_settings()


# Initialize settings on import
settings = get_settings()


# Database migration on startup
def migrate_env_to_database():
    """Migrate .env configuration to database on startup"""
    if DATABASE_AVAILABLE and settings.migrate_env_on_startup:
        try:
            from .database.migration import full_migration
            logger.info("🔄 Starting configuration migration to database...")
            result = full_migration()
            
            if result["success"]:
                logger.info("✅ Configuration migration completed successfully")
            else:
                logger.warning("⚠️ Configuration migration completed with errors")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Configuration migration failed: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "reason": "Migration disabled or database not available"}

