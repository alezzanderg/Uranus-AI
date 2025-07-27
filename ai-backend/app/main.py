"""
Main application file for the AI Assistant Backend.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from .config import settings
from .api import chat_routes, code_routes, websocket_routes


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

if settings.log_file:
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days"
    )


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Backend service for AI Assistant integrated into Code-OSS editor",
    debug=settings.debug
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(chat_routes.router)
app.include_router(code_routes.router)
app.include_router(websocket_routes.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "running",
        "endpoints": {
            "chat": "/api/v1/chat",
            "code": "/api/v1/code",
            "websocket": "/ws",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": "2025-07-27T00:00:00Z"
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint with detailed information."""
    return {
        "api_version": "v1",
        "services": {
            "chat": "available",
            "code_analysis": "available",
            "code_completion": "available",
            "websocket": "available"
        },
        "models": {
            "openai_model": settings.openai_model,
            "max_tokens": settings.openai_max_tokens,
            "temperature": settings.openai_temperature
        },
        "configuration": {
            "max_context_length": settings.max_context_length,
            "max_conversation_history": settings.max_conversation_history,
            "rate_limit_per_minute": settings.rate_limit_requests_per_minute
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.debug else None
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.backend_cors_origins}")
    
    # Validate OpenAI API key
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured. AI features may not work properly.")
    else:
        logger.info("OpenAI API key configured")
    
    logger.info("AI Assistant Backend started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down AI Assistant Backend")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower()
    )

