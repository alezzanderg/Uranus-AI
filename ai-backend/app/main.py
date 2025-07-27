"""
Uranus-AI Backend - Multi-Model AI Assistant
FastAPI backend supporting multiple AI providers and models
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import get_settings
from .api import chat_routes, code_routes, websocket_routes, multi_model_routes
from .services.multi_model_service import MultiModelService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/uranus-ai.log", mode="a")
    ]
)

logger = logging.getLogger(__name__)

# Global services
multi_model_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global multi_model_service
    
    # Startup
    logger.info("🪐 Starting Uranus-AI Backend...")
    
    try:
        # Initialize multi-model service
        multi_model_service = MultiModelService()
        available_models = multi_model_service.get_available_models()
        logger.info(f"✅ Initialized {len(available_models)} AI models")
        
        # Log available providers
        providers = list(set(model.provider.value for model in available_models))
        logger.info(f"🤖 Available providers: {', '.join(providers)}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Uranus-AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="Uranus-AI Backend",
    description="Multi-Model AI Assistant Backend for Code-OSS Editor",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        global multi_model_service
        if multi_model_service:
            available_models = multi_model_service.get_available_models()
            return {
                "status": "healthy",
                "version": "1.1.0",
                "features": [
                    "Multi-Model Support",
                    "Real-time Chat",
                    "Code Analysis",
                    "WebSocket Streaming",
                    "Model Comparison",
                    "Usage Analytics"
                ],
                "models": {
                    "total": len(available_models),
                    "providers": len(multi_model_service.clients),
                    "available": [model.id for model in available_models[:10]]  # Show first 10
                },
                "capabilities": [
                    "chat",
                    "code_completion",
                    "code_analysis",
                    "function_calling",
                    "vision",
                    "long_context"
                ]
            }
        else:
            return {
                "status": "initializing",
                "version": "1.1.0"
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status with detailed information"""
    try:
        global multi_model_service
        if not multi_model_service:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        available_models = multi_model_service.get_available_models()
        usage_stats = multi_model_service.get_usage_stats()
        
        # Group models by provider
        models_by_provider = {}
        for model in available_models:
            provider = model.provider.value
            if provider not in models_by_provider:
                models_by_provider[provider] = []
            models_by_provider[provider].append({
                "id": model.id,
                "name": model.name,
                "capabilities": [cap.value for cap in model.capabilities],
                "context_length": model.context_length,
                "cost_per_1k_tokens": model.cost_per_1k_tokens
            })
        
        return {
            "status": "operational",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.1.0",
            "models": {
                "total_available": len(available_models),
                "by_provider": models_by_provider,
                "total_requests": sum(stats.total_requests for stats in usage_stats.values()),
                "total_tokens": sum(stats.total_tokens for stats in usage_stats.values())
            },
            "features": {
                "multi_model": True,
                "streaming": True,
                "websocket": True,
                "code_analysis": True,
                "model_comparison": True,
                "auto_fallback": True,
                "usage_tracking": True
            },
            "endpoints": {
                "chat": "/api/v1/chat/message",
                "stream_chat": "/ws",
                "code_analysis": "/api/v1/code/analyze",
                "models": "/api/v1/models/available",
                "model_selection": "/api/v1/models/select",
                "model_comparison": "/api/v1/models/compare"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include routers
app.include_router(chat_routes.router)
app.include_router(code_routes.router)
app.include_router(websocket_routes.router)
app.include_router(multi_model_routes.router)  # New multi-model routes


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Uranus-AI Backend",
        "version": "1.1.0",
        "description": "Multi-Model AI Assistant Backend for Code-OSS Editor",
        "features": [
            "🤖 Multiple AI Models (OpenAI, Claude, Gemini, Grok, DeepSeek, etc.)",
            "💬 Real-time Chat with Context",
            "🔍 Advanced Code Analysis",
            "🔄 Automatic Model Fallback",
            "📊 Usage Analytics and Comparison",
            "⚡ WebSocket Streaming",
            "🎯 Smart Model Selection"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "status": "/api/v1/status",
            "models": "/api/v1/models/available",
            "chat": "/api/v1/chat/message",
            "websocket": "/ws"
        }
    }


if __name__ == "__main__":
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

