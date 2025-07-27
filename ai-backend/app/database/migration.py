"""
Database Migration System for Uranus-AI
Migrates configuration from .env files to PostgreSQL
"""

import os
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .connection import get_db, create_database_if_not_exists
from .config_service import ConfigService
from .models import Base, engine

logger = logging.getLogger(__name__)


def create_tables() -> bool:
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def migrate_env_to_db(env_file_path: str = ".env", db: Session = None) -> Dict[str, Any]:
    """
    Migrate configuration from .env file to PostgreSQL
    """
    if db is None:
        db = next(get_db())
    
    config_service = ConfigService()
    migration_result = {
        "migrated": [],
        "skipped": [],
        "errors": [],
        "api_keys_migrated": []
    }
    
    try:
        # Load environment variables from file
        if os.path.exists(env_file_path):
            load_dotenv(env_file_path)
            logger.info(f"📁 Loading configuration from {env_file_path}")
        else:
            logger.warning(f"⚠️ .env file not found at {env_file_path}")
            return migration_result
        
        # Define mapping of env vars to database config
        env_mappings = {
            # Server Configuration
            "HOST": ("server.host", "server", "Server host address"),
            "PORT": ("server.port", "server", "Server port number"),
            "DEBUG": ("server.debug", "server", "Enable debug mode"),
            "LOG_LEVEL": ("server.log_level", "server", "Logging level"),
            
            # AI Configuration
            "DEFAULT_MODEL": ("ai.default_model", "ai", "Default AI model"),
            "FALLBACK_MODELS": ("ai.fallback_models", "ai", "Fallback models list"),
            "ENABLE_AUTO_FALLBACK": ("ai.enable_fallback", "ai", "Enable automatic fallback"),
            "ENABLE_MODEL_SWITCHING": ("ai.enable_model_switching", "ai", "Enable model switching"),
            "ENABLE_COST_OPTIMIZATION": ("ai.cost_optimization", "ai", "Enable cost optimization"),
            
            # Features
            "ENABLE_STREAMING": ("features.streaming", "features", "Enable streaming responses"),
            "ENABLE_FUNCTION_CALLING": ("features.function_calling", "features", "Enable function calling"),
            "ENABLE_VISION_MODELS": ("features.vision_models", "features", "Enable vision models"),
            "ENABLE_RESPONSE_CACHING": ("features.response_caching", "features", "Enable response caching"),
            
            # Rate Limiting
            "RATE_LIMIT_PER_MINUTE": ("limits.rate_per_minute", "limits", "Rate limit per minute"),
            "RATE_LIMIT_PER_HOUR": ("limits.rate_per_hour", "limits", "Rate limit per hour"),
            "MAX_CONCURRENT_REQUESTS": ("limits.max_concurrent", "limits", "Max concurrent requests"),
            "REQUEST_TIMEOUT_SECONDS": ("limits.request_timeout", "limits", "Request timeout in seconds"),
            
            # Security
            "JWT_SECRET_KEY": ("security.jwt_secret", "security", "JWT secret key", True),
            "ENABLE_API_KEY_AUTH": ("security.api_key_auth", "security", "Enable API key authentication"),
            "API_KEY": ("security.api_key", "security", "API key for authentication", True),
            
            # CORS
            "BACKEND_CORS_ORIGINS": ("server.cors_origins", "server", "CORS allowed origins"),
            
            # Database
            "DATABASE_URL": ("database.url", "database", "Database connection URL", True),
            "REDIS_URL": ("database.redis_url", "database", "Redis connection URL"),
            
            # Caching
            "CACHE_TTL_SECONDS": ("cache.ttl", "cache", "Cache TTL in seconds"),
            
            # Monitoring
            "ENABLE_USAGE_TRACKING": ("monitoring.usage_tracking", "monitoring", "Enable usage tracking"),
            "ENABLE_PERFORMANCE_MONITORING": ("monitoring.performance", "monitoring", "Enable performance monitoring"),
            "ENABLE_ERROR_REPORTING": ("monitoring.error_reporting", "monitoring", "Enable error reporting"),
        }
        
        # API Keys mapping
        api_key_mappings = {
            "OPENAI_API_KEY": "openai",
            "ANTHROPIC_API_KEY": "anthropic", 
            "GOOGLE_API_KEY": "google",
            "XAI_API_KEY": "xai",
            "DEEPSEEK_API_KEY": "deepseek",
            "MISTRAL_API_KEY": "mistral",
            "COHERE_API_KEY": "cohere",
            "AZURE_OPENAI_API_KEY": "azure_openai",
        }
        
        # Migrate regular configurations
        for env_key, mapping in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                db_key, category, description = mapping[:3]
                is_secret = len(mapping) > 3 and mapping[3]
                
                try:
                    success = config_service.set_config(
                        key=db_key,
                        value=value,
                        category=category,
                        description=description,
                        is_secret=is_secret,
                        db=db
                    )
                    
                    if success:
                        migration_result["migrated"].append({
                            "env_key": env_key,
                            "db_key": db_key,
                            "category": category,
                            "is_secret": is_secret
                        })
                        logger.info(f"✅ Migrated {env_key} -> {db_key}")
                    else:
                        migration_result["errors"].append(f"Failed to migrate {env_key}")
                        
                except Exception as e:
                    migration_result["errors"].append(f"Error migrating {env_key}: {str(e)}")
                    logger.error(f"❌ Error migrating {env_key}: {e}")
            else:
                migration_result["skipped"].append(env_key)
        
        # Migrate API keys
        for env_key, provider in api_key_mappings.items():
            api_key = os.getenv(env_key)
            if api_key:
                try:
                    success = config_service.set_api_key(
                        provider=provider,
                        key=api_key,
                        key_name=f"{provider}_api_key",
                        db=db
                    )
                    
                    if success:
                        migration_result["api_keys_migrated"].append({
                            "provider": provider,
                            "env_key": env_key
                        })
                        logger.info(f"🔐 Migrated API key for {provider}")
                    else:
                        migration_result["errors"].append(f"Failed to migrate API key for {provider}")
                        
                except Exception as e:
                    migration_result["errors"].append(f"Error migrating API key for {provider}: {str(e)}")
                    logger.error(f"❌ Error migrating API key for {provider}: {e}")
        
        # Initialize default configurations
        config_service.initialize_default_configs(db)
        
        logger.info(f"🎉 Migration completed: {len(migration_result['migrated'])} configs, {len(migration_result['api_keys_migrated'])} API keys")
        
        return migration_result
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        migration_result["errors"].append(f"Migration failed: {str(e)}")
        return migration_result


def backup_env_file(env_file_path: str = ".env") -> str:
    """Create backup of .env file before migration"""
    try:
        if os.path.exists(env_file_path):
            backup_path = f"{env_file_path}.backup"
            with open(env_file_path, 'r') as original:
                with open(backup_path, 'w') as backup:
                    backup.write(original.read())
            logger.info(f"📋 Created backup: {backup_path}")
            return backup_path
        return ""
    except Exception as e:
        logger.error(f"❌ Failed to create backup: {e}")
        return ""


def full_migration(env_file_path: str = ".env") -> Dict[str, Any]:
    """
    Complete migration process:
    1. Create tables
    2. Backup .env file
    3. Migrate configurations
    4. Verify migration
    """
    logger.info("🚀 Starting full migration process...")
    
    result = {
        "success": False,
        "steps": {},
        "summary": {}
    }
    
    try:
        # Step 1: Create tables
        logger.info("📊 Step 1: Creating database tables...")
        tables_created = create_tables()
        result["steps"]["create_tables"] = tables_created
        
        if not tables_created:
            result["steps"]["error"] = "Failed to create database tables"
            return result
        
        # Step 2: Backup .env file
        logger.info("📋 Step 2: Creating backup of .env file...")
        backup_path = backup_env_file(env_file_path)
        result["steps"]["backup_created"] = backup_path
        
        # Step 3: Migrate configurations
        logger.info("🔄 Step 3: Migrating configurations...")
        migration_result = migrate_env_to_db(env_file_path)
        result["steps"]["migration"] = migration_result
        
        # Step 4: Verify migration
        logger.info("✅ Step 4: Verifying migration...")
        config_service = ConfigService()
        all_configs = config_service.get_all_configs(include_secrets=False)
        result["steps"]["verification"] = {
            "total_configs": len(all_configs),
            "sample_configs": list(all_configs.keys())[:10]
        }
        
        # Summary
        result["summary"] = {
            "total_migrated": len(migration_result["migrated"]),
            "api_keys_migrated": len(migration_result["api_keys_migrated"]),
            "errors": len(migration_result["errors"]),
            "skipped": len(migration_result["skipped"])
        }
        
        result["success"] = len(migration_result["errors"]) == 0
        
        if result["success"]:
            logger.info("🎉 Full migration completed successfully!")
        else:
            logger.warning("⚠️ Migration completed with errors")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Full migration failed: {e}")
        result["steps"]["error"] = str(e)
        return result


def verify_migration() -> Dict[str, Any]:
    """Verify that migration was successful"""
    try:
        config_service = ConfigService()
        
        # Test basic config retrieval
        host = config_service.get_config("server.host", "localhost")
        port = config_service.get_config("server.port", 8000)
        
        # Test API key retrieval
        openai_key = config_service.get_api_key("openai")
        
        # Get all configs
        all_configs = config_service.get_all_configs()
        
        return {
            "status": "success",
            "config_count": len(all_configs),
            "sample_config": {"host": host, "port": port},
            "has_openai_key": openai_key is not None,
            "config_categories": list(set(
                key.split('.')[0] for key in all_configs.keys() if '.' in key
            ))
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Run migration if called directly
    result = full_migration()
    print(f"Migration result: {result}")

