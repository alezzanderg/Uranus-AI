"""
PostgreSQL Database Connection for Uranus-AI
Connects to Neon PostgreSQL for configuration and user data storage
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import urllib.parse

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_btfS8wXgFjl7@ep-rapid-sea-adxzz6h8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# Parse the URL to ensure it's properly formatted
parsed_url = urllib.parse.urlparse(DATABASE_URL)
if parsed_url.scheme == "postgres":
    # Convert postgres:// to postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True for SQL debugging
    connect_args={
        "sslmode": "require",
        "application_name": "uranus-ai"
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test database connection
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def get_db_info() -> dict:
    """
    Get database information
    """
    try:
        with engine.connect() as connection:
            # Get PostgreSQL version
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            # Get database name
            db_result = connection.execute(text("SELECT current_database()"))
            database = db_result.fetchone()[0]
            
            # Get current user
            user_result = connection.execute(text("SELECT current_user"))
            user = user_result.fetchone()[0]
            
            # Get connection count
            conn_result = connection.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            ))
            connections = conn_result.fetchone()[0]
            
            return {
                "status": "connected",
                "version": version,
                "database": database,
                "user": user,
                "connections": connections,
                "url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "hidden"
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def create_database_if_not_exists():
    """
    Create database tables if they don't exist
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False


def drop_all_tables():
    """
    Drop all tables (use with caution!)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False


class DatabaseHealthCheck:
    """
    Database health check utility
    """
    
    @staticmethod
    def check_connection() -> dict:
        """Check basic connection"""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "healthy", "connection": True}
        except Exception as e:
            return {"status": "unhealthy", "connection": False, "error": str(e)}
    
    @staticmethod
    def check_tables() -> dict:
        """Check if required tables exist"""
        try:
            with engine.connect() as conn:
                # Check if our main tables exist
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('configurations', 'user_preferences', 'model_usage', 'chat_history')
                """)
                result = conn.execute(tables_query)
                existing_tables = [row[0] for row in result.fetchall()]
                
                required_tables = ['configurations', 'user_preferences', 'model_usage', 'chat_history']
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                return {
                    "status": "healthy" if not missing_tables else "partial",
                    "existing_tables": existing_tables,
                    "missing_tables": missing_tables
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    def full_health_check() -> dict:
        """Complete health check"""
        connection_check = DatabaseHealthCheck.check_connection()
        tables_check = DatabaseHealthCheck.check_tables()
        db_info = get_db_info()
        
        overall_status = "healthy"
        if connection_check["status"] != "healthy":
            overall_status = "unhealthy"
        elif tables_check["status"] == "error":
            overall_status = "unhealthy"
        elif tables_check["status"] == "partial":
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "connection": connection_check,
            "tables": tables_check,
            "database_info": db_info,
            "timestamp": "2025-07-27T00:00:00Z"
        }

