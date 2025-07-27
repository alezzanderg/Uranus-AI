"""
Database module for Uranus-AI
PostgreSQL integration with Neon for configuration and user data
"""

from .connection import get_db, engine, SessionLocal
from .models import Base, Configuration, UserPreference, ModelUsage, ChatHistory
from .config_service import ConfigService
from .migration import migrate_env_to_db, create_tables

__all__ = [
    'get_db',
    'engine', 
    'SessionLocal',
    'Base',
    'Configuration',
    'UserPreference', 
    'ModelUsage',
    'ChatHistory',
    'ConfigService',
    'migrate_env_to_db',
    'create_tables'
]

