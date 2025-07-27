"""
Database Models for Uranus-AI
SQLAlchemy models for PostgreSQL storage
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .connection import Base


class Configuration(Base):
    """
    Configuration table for storing app settings and API keys
    """
    __tablename__ = "configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="general")
    description = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False)
    is_secret = Column(Boolean, default=False)  # For API keys and sensitive data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Configuration(key='{self.key}', category='{self.category}')>"


class UserPreference(Base):
    """
    User preferences and settings
    """
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, default="default_user")
    preference_key = Column(String(255), nullable=False)
    preference_value = Column(JSON, nullable=True)
    category = Column(String(100), nullable=False, default="ui")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserPreference(user_id='{self.user_id}', key='{self.preference_key}')>"


class ModelUsage(Base):
    """
    Track AI model usage statistics
    """
    __tablename__ = "model_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    user_id = Column(String(255), nullable=False, default="default_user")
    request_type = Column(String(50), nullable=False)  # chat, code_analysis, completion
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    response_time = Column(Float, default=0.0)  # in seconds
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelUsage(model_id='{self.model_id}', provider='{self.provider}')>"


class ChatHistory(Base):
    """
    Store chat conversation history
    """
    __tablename__ = "chat_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, default="default_user")
    model_id = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    metadata = Column(JSON, nullable=True)  # Context, file references, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ChatHistory(conversation_id='{self.conversation_id}', role='{self.role}')>"


class ApiKey(Base):
    """
    Encrypted API keys storage
    """
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(100), nullable=False, unique=True)
    key_name = Column(String(255), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ApiKey(provider='{self.provider}', active={self.is_active})>"


class SystemLog(Base):
    """
    System logs and events
    """
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    component = Column(String(100), nullable=False)  # backend, frontend, database
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    user_id = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SystemLog(level='{self.level}', component='{self.component}')>"


class FeatureFlag(Base):
    """
    Feature flags for A/B testing and gradual rollouts
    """
    __tablename__ = "feature_flags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flag_name = Column(String(255), nullable=False, unique=True)
    is_enabled = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    target_users = Column(JSON, nullable=True)  # List of user IDs or criteria
    rollout_percentage = Column(Integer, default=0)  # 0-100
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FeatureFlag(name='{self.flag_name}', enabled={self.is_enabled})>"


class ModelConfiguration(Base):
    """
    Model-specific configurations and parameters
    """
    __tablename__ = "model_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    configuration = Column(JSON, nullable=False)  # Model parameters
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(255), nullable=False, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ModelConfiguration(model_id='{self.model_id}', provider='{self.provider}')>"


# Default configurations that should be inserted on first run
DEFAULT_CONFIGURATIONS = [
    # Server Configuration
    {
        "key": "server.host",
        "value": "0.0.0.0",
        "category": "server",
        "description": "Server host address"
    },
    {
        "key": "server.port",
        "value": "8000",
        "category": "server",
        "description": "Server port number"
    },
    {
        "key": "server.debug",
        "value": "false",
        "category": "server",
        "description": "Enable debug mode"
    },
    
    # AI Configuration
    {
        "key": "ai.default_model",
        "value": "gpt-4",
        "category": "ai",
        "description": "Default AI model to use"
    },
    {
        "key": "ai.enable_fallback",
        "value": "true",
        "category": "ai",
        "description": "Enable automatic model fallback"
    },
    {
        "key": "ai.fallback_models",
        "value": '["gpt-3.5-turbo", "claude-3-haiku", "gemini-pro"]',
        "category": "ai",
        "description": "Fallback models in order of preference"
    },
    
    # Features
    {
        "key": "features.multi_model",
        "value": "true",
        "category": "features",
        "description": "Enable multi-model support"
    },
    {
        "key": "features.streaming",
        "value": "true",
        "category": "features",
        "description": "Enable streaming responses"
    },
    {
        "key": "features.cost_optimization",
        "value": "false",
        "category": "features",
        "description": "Enable automatic cost optimization"
    },
    
    # Security
    {
        "key": "security.enable_encryption",
        "value": "true",
        "category": "security",
        "description": "Encrypt sensitive data"
    },
    {
        "key": "security.session_timeout",
        "value": "3600",
        "category": "security",
        "description": "Session timeout in seconds"
    }
]


# Default user preferences
DEFAULT_USER_PREFERENCES = [
    {
        "user_id": "default_user",
        "preference_key": "theme",
        "preference_value": {"theme": "dark", "accent_color": "#007ACC"},
        "category": "ui"
    },
    {
        "user_id": "default_user", 
        "preference_key": "ai_assistant",
        "preference_value": {
            "auto_suggestions": True,
            "context_awareness": True,
            "preferred_model": "gpt-4"
        },
        "category": "ai"
    },
    {
        "user_id": "default_user",
        "preference_key": "editor",
        "preference_value": {
            "font_size": 14,
            "word_wrap": True,
            "minimap": True
        },
        "category": "editor"
    }
]

