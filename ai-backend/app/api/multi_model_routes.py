"""
Multi-Model API Routes
Endpoints for managing and using multiple AI models
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging

from ..models.ai_models import (
    AIProvider, ModelInfo, AIModelRequest, AIModelResponse,
    AVAILABLE_MODELS, get_models_by_capability, get_models_by_provider,
    get_cheapest_models, get_recommended_model, ModelCapability
)
from ..services.multi_model_service import MultiModelService, ModelUsageStats
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/models", tags=["Multi-Model"])

# Global service instance
multi_model_service = MultiModelService()


class ModelSelectionRequest(BaseModel):
    """Request for model selection"""
    task_type: str
    context_length: Optional[int] = 4000
    prefer_cost_effective: bool = False
    prefer_speed: bool = False
    required_capabilities: Optional[List[str]] = None


class ModelComparisonRequest(BaseModel):
    """Request for model comparison"""
    models: List[str]
    test_prompt: str
    criteria: List[str] = ["quality", "speed", "cost"]


@router.get("/available", response_model=List[ModelInfo])
async def get_available_models():
    """Get list of all available AI models"""
    try:
        return multi_model_service.get_available_models()
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=List[str])
async def get_available_providers():
    """Get list of available AI providers"""
    try:
        available_models = multi_model_service.get_available_models()
        providers = list(set(model.provider.value for model in available_models))
        return sorted(providers)
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provider/{provider}", response_model=List[ModelInfo])
async def get_models_by_provider_endpoint(provider: str):
    """Get all models from a specific provider"""
    try:
        provider_enum = AIProvider(provider)
        models = get_models_by_provider(provider_enum)
        # Filter by available models
        available_model_ids = {m.id for m in multi_model_service.get_available_models()}
        return [m for m in models if m.id in available_model_ids]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    except Exception as e:
        logger.error(f"Error getting models for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capability/{capability}", response_model=List[ModelInfo])
async def get_models_by_capability_endpoint(capability: str):
    """Get all models that support a specific capability"""
    try:
        capability_enum = ModelCapability(capability)
        models = get_models_by_capability(capability_enum)
        # Filter by available models
        available_model_ids = {m.id for m in multi_model_service.get_available_models()}
        return [m for m in models if m.id in available_model_ids]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown capability: {capability}")
    except Exception as e:
        logger.error(f"Error getting models for capability {capability}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cheapest/{capability}", response_model=List[ModelInfo])
async def get_cheapest_models_endpoint(capability: str, limit: int = 5):
    """Get the cheapest models for a specific capability"""
    try:
        capability_enum = ModelCapability(capability)
        models = get_cheapest_models(capability_enum, limit)
        # Filter by available models
        available_model_ids = {m.id for m in multi_model_service.get_available_models()}
        return [m for m in models if m.id in available_model_ids]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown capability: {capability}")
    except Exception as e:
        logger.error(f"Error getting cheapest models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select", response_model=List[str])
async def select_models(request: ModelSelectionRequest):
    """Get recommended models based on requirements"""
    try:
        recommendations = multi_model_service.get_model_recommendations(
            request.task_type,
            request.context_length
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error selecting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=AIModelResponse)
async def generate_with_model(request: AIModelRequest):
    """Generate response using specified model"""
    try:
        response = await multi_model_service.generate_response(request)
        return response
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream")
async def stream_generate_with_model(request: AIModelRequest):
    """Stream response using specified model"""
    try:
        async def generate_stream():
            async for chunk in multi_model_service.stream_response(request):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    except Exception as e:
        logger.error(f"Error streaming response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_models(request: ModelComparisonRequest, background_tasks: BackgroundTasks):
    """Compare multiple models on the same prompt"""
    try:
        results = {}
        
        for model_id in request.models:
            try:
                model_info = multi_model_service.get_model_info(model_id)
                if not model_info:
                    results[model_id] = {"error": "Model not found"}
                    continue
                
                ai_request = AIModelRequest(
                    model_id=model_id,
                    provider=model_info.provider,
                    messages=[{"role": "user", "content": request.test_prompt}],
                    temperature=0.7
                )
                
                import time
                start_time = time.time()
                response = await multi_model_service.generate_response(ai_request, fallback=False)
                end_time = time.time()
                
                results[model_id] = {
                    "response": response.content,
                    "response_time": end_time - start_time,
                    "usage": response.usage,
                    "cost_estimate": (
                        (response.usage.get("total_tokens", 0) / 1000) * model_info.cost_per_1k_tokens
                        if model_info.cost_per_1k_tokens and response.usage
                        else 0
                    ),
                    "provider": model_info.provider.value
                }
                
            except Exception as e:
                results[model_id] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, ModelUsageStats])
async def get_usage_stats():
    """Get usage statistics for all models"""
    try:
        return multi_model_service.get_usage_stats()
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{model_id}", response_model=ModelInfo)
async def get_model_info(model_id: str):
    """Get detailed information about a specific model"""
    try:
        model_info = multi_model_service.get_model_info(model_id)
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        return model_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark")
async def benchmark_models(
    models: List[str],
    test_prompts: List[str],
    background_tasks: BackgroundTasks
):
    """Benchmark multiple models with multiple prompts"""
    try:
        results = {}
        
        for model_id in models:
            model_results = []
            model_info = multi_model_service.get_model_info(model_id)
            
            if not model_info:
                results[model_id] = {"error": "Model not found"}
                continue
            
            for prompt in test_prompts:
                try:
                    ai_request = AIModelRequest(
                        model_id=model_id,
                        provider=model_info.provider,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    
                    import time
                    start_time = time.time()
                    response = await multi_model_service.generate_response(ai_request, fallback=False)
                    end_time = time.time()
                    
                    model_results.append({
                        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                        "response_length": len(response.content),
                        "response_time": end_time - start_time,
                        "tokens_used": response.usage.get("total_tokens", 0) if response.usage else 0,
                        "cost": (
                            (response.usage.get("total_tokens", 0) / 1000) * model_info.cost_per_1k_tokens
                            if model_info.cost_per_1k_tokens and response.usage
                            else 0
                        )
                    })
                    
                except Exception as e:
                    model_results.append({
                        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                        "error": str(e)
                    })
            
            # Calculate averages
            successful_results = [r for r in model_results if "error" not in r]
            if successful_results:
                avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
                avg_tokens = sum(r["tokens_used"] for r in successful_results) / len(successful_results)
                total_cost = sum(r["cost"] for r in successful_results)
                
                results[model_id] = {
                    "individual_results": model_results,
                    "summary": {
                        "avg_response_time": avg_response_time,
                        "avg_tokens_used": avg_tokens,
                        "total_cost": total_cost,
                        "success_rate": len(successful_results) / len(test_prompts),
                        "provider": model_info.provider.value
                    }
                }
            else:
                results[model_id] = {
                    "individual_results": model_results,
                    "summary": {"error": "All prompts failed"}
                }
        
        return results
        
    except Exception as e:
        logger.error(f"Error benchmarking models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for multi-model service"""
    try:
        available_models = multi_model_service.get_available_models()
        return {
            "status": "healthy",
            "available_models": len(available_models),
            "providers": len(multi_model_service.clients),
            "models": [model.id for model in available_models[:5]]  # Show first 5
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

