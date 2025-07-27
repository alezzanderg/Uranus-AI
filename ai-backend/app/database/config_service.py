"""
Configuration Service for Uranus-AI
Manages configuration retrieval and storage in PostgreSQL
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import base64

from .models import Configuration, UserPreference, ApiKey, DEFAULT_CONFIGURATIONS, DEFAULT_USER_PREFERENCES
from .connection import get_db

logger = logging.getLogger(__name__)


class ConfigService:
    """
    Service for managing configuration in PostgreSQL
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = "encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            logger.info("🔐 Generated new encryption key")
            return key
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt sensitive value"""
        try:
            encrypted = self.cipher_suite.encrypt(value.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return value
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive value"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_value
    
    def get_config(self, key: str, default: Any = None, db: Session = None) -> Any:
        """Get configuration value"""
        if db is None:
            db = next(get_db())
        
        try:
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                value = config.value
                
                # Decrypt if encrypted
                if config.is_encrypted and value:
                    value = self.decrypt_value(value)
                
                # Try to parse JSON values
                if value and value.startswith(('[', '{')):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        pass
                
                # Convert boolean strings
                if value and value.lower() in ('true', 'false'):
                    return value.lower() == 'true'
                
                # Convert numeric strings
                if value and value.isdigit():
                    return int(value)
                
                return value
            
            return default
            
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def set_config(self, key: str, value: Any, category: str = "general", 
                   description: str = None, is_secret: bool = False, db: Session = None) -> bool:
        """Set configuration value"""
        if db is None:
            db = next(get_db())
        
        try:
            # Convert value to string
            if isinstance(value, (dict, list)):
                str_value = json.dumps(value)
            elif isinstance(value, bool):
                str_value = str(value).lower()
            else:
                str_value = str(value)
            
            # Encrypt if secret
            is_encrypted = False
            if is_secret and str_value:
                str_value = self.encrypt_value(str_value)
                is_encrypted = True
            
            # Check if config exists
            config = db.query(Configuration).filter(Configuration.key == key).first()
            
            if config:
                # Update existing
                config.value = str_value
                config.category = category
                config.is_encrypted = is_encrypted
                config.is_secret = is_secret
                if description:
                    config.description = description
            else:
                # Create new
                config = Configuration(
                    key=key,
                    value=str_value,
                    category=category,
                    description=description,
                    is_encrypted=is_encrypted,
                    is_secret=is_secret
                )
                db.add(config)
            
            db.commit()
            logger.info(f"✅ Config {key} updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            db.rollback()
            return False
    
    def get_all_configs(self, category: str = None, include_secrets: bool = False, 
                       db: Session = None) -> Dict[str, Any]:
        """Get all configurations"""
        if db is None:
            db = next(get_db())
        
        try:
            query = db.query(Configuration)
            
            if category:
                query = query.filter(Configuration.category == category)
            
            if not include_secrets:
                query = query.filter(Configuration.is_secret == False)
            
            configs = query.all()
            result = {}
            
            for config in configs:
                value = config.value
                
                # Decrypt if encrypted and secrets are included
                if config.is_encrypted and include_secrets and value:
                    value = self.decrypt_value(value)
                elif config.is_encrypted and not include_secrets:
                    value = "***HIDDEN***"
                
                # Parse JSON values
                if value and isinstance(value, str) and value.startswith(('[', '{')):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                
                # Convert boolean strings
                if isinstance(value, str) and value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                
                result[config.key] = value
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get all configs: {e}")
            return {}
    
    def delete_config(self, key: str, db: Session = None) -> bool:
        """Delete configuration"""
        if db is None:
            db = next(get_db())
        
        try:
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                db.delete(config)
                db.commit()
                logger.info(f"🗑️ Config {key} deleted")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete config {key}: {e}")
            db.rollback()
            return False
    
    def get_user_preference(self, user_id: str, key: str, default: Any = None, 
                           db: Session = None) -> Any:
        """Get user preference"""
        if db is None:
            db = next(get_db())
        
        try:
            pref = db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == key
            ).first()
            
            return pref.preference_value if pref else default
            
        except Exception as e:
            logger.error(f"Failed to get user preference {key}: {e}")
            return default
    
    def set_user_preference(self, user_id: str, key: str, value: Any, 
                           category: str = "general", db: Session = None) -> bool:
        """Set user preference"""
        if db is None:
            db = next(get_db())
        
        try:
            pref = db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == key
            ).first()
            
            if pref:
                pref.preference_value = value
                pref.category = category
            else:
                pref = UserPreference(
                    user_id=user_id,
                    preference_key=key,
                    preference_value=value,
                    category=category
                )
                db.add(pref)
            
            db.commit()
            logger.info(f"✅ User preference {key} updated for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set user preference {key}: {e}")
            db.rollback()
            return False
    
    def get_api_key(self, provider: str, db: Session = None) -> Optional[str]:
        """Get decrypted API key for provider"""
        if db is None:
            db = next(get_db())
        
        try:
            api_key = db.query(ApiKey).filter(
                ApiKey.provider == provider,
                ApiKey.is_active == True
            ).first()
            
            if api_key:
                # Update usage stats
                api_key.usage_count += 1
                api_key.last_used = func.now()
                db.commit()
                
                return self.decrypt_value(api_key.encrypted_key)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get API key for {provider}: {e}")
            return None
    
    def set_api_key(self, provider: str, key: str, key_name: str = None, 
                    db: Session = None) -> bool:
        """Set encrypted API key for provider"""
        if db is None:
            db = next(get_db())
        
        try:
            encrypted_key = self.encrypt_value(key)
            
            api_key = db.query(ApiKey).filter(ApiKey.provider == provider).first()
            
            if api_key:
                api_key.encrypted_key = encrypted_key
                api_key.key_name = key_name or f"{provider}_key"
                api_key.is_active = True
            else:
                api_key = ApiKey(
                    provider=provider,
                    key_name=key_name or f"{provider}_key",
                    encrypted_key=encrypted_key,
                    is_active=True
                )
                db.add(api_key)
            
            db.commit()
            logger.info(f"🔐 API key for {provider} updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set API key for {provider}: {e}")
            db.rollback()
            return False
    
    def initialize_default_configs(self, db: Session = None) -> bool:
        """Initialize default configurations"""
        if db is None:
            db = next(get_db())
        
        try:
            # Insert default configurations
            for config_data in DEFAULT_CONFIGURATIONS:
                existing = db.query(Configuration).filter(
                    Configuration.key == config_data["key"]
                ).first()
                
                if not existing:
                    config = Configuration(**config_data)
                    db.add(config)
            
            # Insert default user preferences
            for pref_data in DEFAULT_USER_PREFERENCES:
                existing = db.query(UserPreference).filter(
                    UserPreference.user_id == pref_data["user_id"],
                    UserPreference.preference_key == pref_data["preference_key"]
                ).first()
                
                if not existing:
                    pref = UserPreference(**pref_data)
                    db.add(pref)
            
            db.commit()
            logger.info("✅ Default configurations initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize default configs: {e}")
            db.rollback()
            return False
    
    def get_settings_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Get all settings as a dictionary (similar to old .env format)"""
        configs = self.get_all_configs(include_secrets=include_secrets)
        
        # Convert dot notation to uppercase env-style keys
        settings = {}
        for key, value in configs.items():
            env_key = key.replace(".", "_").upper()
            settings[env_key] = value
        
        return settings


# Global instance
config_service = ConfigService()

