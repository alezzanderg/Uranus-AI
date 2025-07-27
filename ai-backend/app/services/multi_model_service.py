"""
Multi-Model AI Service
Handles multiple AI providers and models with automatic fallback and optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any
from dataclasses import dataclass
import json
import time

import openai
import anthropic
import google.generativeai as genai
from openai import AsyncOpenAI

from ..models.ai_models import (
    AIProvider, ModelInfo, AIModelRequest, AIModelResponse,
    ModelConfiguration, MultiModelConfig, AVAILABLE_MODELS
)
from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ModelUsageStats:
    """Track usage statistics for models"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    error_count: int = 0
    last_used: Optional[float] = None


class MultiModelService:
    """Service to handle multiple AI models and providers"""
    
    def __init__(self):
        self.settings = get_settings()
        self.clients: Dict[AIProvider, Any] = {}
        self.usage_stats: Dict[str, ModelUsageStats] = {}
        self.config: Optional[MultiModelConfig] = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize clients for different AI providers"""
        try:
            # OpenAI
            if self.settings.OPENAI_API_KEY:
                self.clients[AIProvider.OPENAI] = AsyncOpenAI(
                    api_key=self.settings.OPENAI_API_KEY,
                    base_url=self.settings.OPENAI_API_BASE
                )
                logger.info("OpenAI client initialized")
            
            # Anthropic Claude
            if hasattr(self.settings, 'ANTHROPIC_API_KEY') and self.settings.ANTHROPIC_API_KEY:
                self.clients[AIProvider.ANTHROPIC] = anthropic.AsyncAnthropic(
                    api_key=self.settings.ANTHROPIC_API_KEY
                )
                logger.info("Anthropic client initialized")
            
            # Google Gemini
            if hasattr(self.settings, 'GOOGLE_API_KEY') and self.settings.GOOGLE_API_KEY:
                genai.configure(api_key=self.settings.GOOGLE_API_KEY)
                self.clients[AIProvider.GOOGLE] = genai
                logger.info("Google Gemini client initialized")
            
            # xAI Grok
            if hasattr(self.settings, 'XAI_API_KEY') and self.settings.XAI_API_KEY:
                self.clients[AIProvider.XAI] = AsyncOpenAI(
                    api_key=self.settings.XAI_API_KEY,
                    base_url="https://api.x.ai/v1"
                )
                logger.info("xAI Grok client initialized")
            
            # DeepSeek
            if hasattr(self.settings, 'DEEPSEEK_API_KEY') and self.settings.DEEPSEEK_API_KEY:
                self.clients[AIProvider.DEEPSEEK] = AsyncOpenAI(
                    api_key=self.settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com"
                )
                logger.info("DeepSeek client initialized")
            
            # Ollama (local)
            if hasattr(self.settings, 'OLLAMA_BASE_URL') and self.settings.OLLAMA_BASE_URL:
                self.clients[AIProvider.OLLAMA] = AsyncOpenAI(
                    api_key="ollama",  # Ollama doesn't require real API key
                    base_url=self.settings.OLLAMA_BASE_URL
                )
                logger.info("Ollama client initialized")
            
            # Mistral
            if hasattr(self.settings, 'MISTRAL_API_KEY') and self.settings.MISTRAL_API_KEY:
                self.clients[AIProvider.MISTRAL] = AsyncOpenAI(
                    api_key=self.settings.MISTRAL_API_KEY,
                    base_url="https://api.mistral.ai/v1"
                )
                logger.info("Mistral client initialized")
            
            # Cohere
            if hasattr(self.settings, 'COHERE_API_KEY') and self.settings.COHERE_API_KEY:
                self.clients[AIProvider.COHERE] = AsyncOpenAI(
                    api_key=self.settings.COHERE_API_KEY,
                    base_url="https://api.cohere.ai/v1"
                )
                logger.info("Cohere client initialized")
                
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models based on configured clients"""
        available = []
        for model_id, model_info in AVAILABLE_MODELS.items():
            if model_info.provider in self.clients:
                available.append(model_info)
        return available
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return AVAILABLE_MODELS.get(model_id)
    
    async def generate_response(
        self, 
        request: AIModelRequest,
        fallback: bool = True
    ) -> AIModelResponse:
        """Generate response using specified model with optional fallback"""
        start_time = time.time()
        
        try:
            # Try primary model
            response = await self._call_model(request)
            self._update_usage_stats(request.model_id, start_time, response)
            return response
            
        except Exception as e:
            logger.error(f"Error with model {request.model_id}: {e}")
            
            if fallback and self.config and self.config.fallback_models:
                # Try fallback models
                for fallback_model_id in self.config.fallback_models:
                    if fallback_model_id != request.model_id:
                        try:
                            fallback_request = request.copy()
                            fallback_request.model_id = fallback_model_id
                            fallback_request.provider = AVAILABLE_MODELS[fallback_model_id].provider
                            
                            response = await self._call_model(fallback_request)
                            self._update_usage_stats(fallback_model_id, start_time, response)
                            logger.info(f"Fallback to {fallback_model_id} successful")
                            return response
                            
                        except Exception as fallback_error:
                            logger.error(f"Fallback model {fallback_model_id} failed: {fallback_error}")
                            continue
            
            # If all models fail
            self._update_error_stats(request.model_id)
            raise Exception(f"All models failed. Last error: {e}")
    
    async def stream_response(
        self, 
        request: AIModelRequest
    ) -> AsyncGenerator[str, None]:
        """Stream response from AI model"""
        try:
            async for chunk in self._stream_model(request):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming error with model {request.model_id}: {e}")
            yield f"Error: {str(e)}"
    
    async def _call_model(self, request: AIModelRequest) -> AIModelResponse:
        """Call specific AI model"""
        model_info = AVAILABLE_MODELS.get(request.model_id)
        if not model_info:
            raise ValueError(f"Unknown model: {request.model_id}")
        
        client = self.clients.get(model_info.provider)
        if not client:
            raise ValueError(f"Client not configured for provider: {model_info.provider}")
        
        if model_info.provider == AIProvider.OPENAI:
            return await self._call_openai(client, request, model_info)
        elif model_info.provider == AIProvider.ANTHROPIC:
            return await self._call_anthropic(client, request, model_info)
        elif model_info.provider == AIProvider.GOOGLE:
            return await self._call_google(client, request, model_info)
        elif model_info.provider in [AIProvider.XAI, AIProvider.DEEPSEEK, AIProvider.OLLAMA, AIProvider.MISTRAL]:
            # These use OpenAI-compatible APIs
            return await self._call_openai_compatible(client, request, model_info)
        else:
            raise ValueError(f"Unsupported provider: {model_info.provider}")
    
    async def _call_openai(
        self, 
        client: AsyncOpenAI, 
        request: AIModelRequest, 
        model_info: ModelInfo
    ) -> AIModelResponse:
        """Call OpenAI API"""
        response = await client.chat.completions.create(
            model=request.model_id,
            messages=request.messages,
            max_tokens=request.max_tokens or model_info.max_tokens,
            temperature=request.temperature,
            stream=False
        )
        
        return AIModelResponse(
            content=response.choices[0].message.content,
            model_id=request.model_id,
            provider=model_info.provider,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason
        )
    
    async def _call_anthropic(
        self, 
        client: anthropic.AsyncAnthropic, 
        request: AIModelRequest, 
        model_info: ModelInfo
    ) -> AIModelResponse:
        """Call Anthropic Claude API"""
        # Convert OpenAI format to Anthropic format
        system_message = ""
        messages = []
        
        for msg in request.messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        response = await client.messages.create(
            model=request.model_id,
            max_tokens=request.max_tokens or model_info.max_tokens,
            temperature=request.temperature,
            system=system_message if system_message else None,
            messages=messages
        )
        
        return AIModelResponse(
            content=response.content[0].text,
            model_id=request.model_id,
            provider=model_info.provider,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason
        )
    
    async def _call_google(
        self, 
        client, 
        request: AIModelRequest, 
        model_info: ModelInfo
    ) -> AIModelResponse:
        """Call Google Gemini API"""
        model = genai.GenerativeModel(request.model_id)
        
        # Convert messages to Gemini format
        prompt = ""
        for msg in request.messages:
            role = "Human" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant:"
        
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=request.max_tokens or model_info.max_tokens,
                temperature=request.temperature
            )
        )
        
        return AIModelResponse(
            content=response.text,
            model_id=request.model_id,
            provider=model_info.provider,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            },
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else None
        )
    
    async def _call_openai_compatible(
        self, 
        client: AsyncOpenAI, 
        request: AIModelRequest, 
        model_info: ModelInfo
    ) -> AIModelResponse:
        """Call OpenAI-compatible APIs (xAI, DeepSeek, Ollama, etc.)"""
        response = await client.chat.completions.create(
            model=request.model_id,
            messages=request.messages,
            max_tokens=request.max_tokens or model_info.max_tokens,
            temperature=request.temperature,
            stream=False
        )
        
        return AIModelResponse(
            content=response.choices[0].message.content,
            model_id=request.model_id,
            provider=model_info.provider,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            finish_reason=response.choices[0].finish_reason
        )
    
    async def _stream_model(self, request: AIModelRequest) -> AsyncGenerator[str, None]:
        """Stream response from model"""
        model_info = AVAILABLE_MODELS.get(request.model_id)
        if not model_info:
            raise ValueError(f"Unknown model: {request.model_id}")
        
        client = self.clients.get(model_info.provider)
        if not client:
            raise ValueError(f"Client not configured for provider: {model_info.provider}")
        
        if model_info.provider in [AIProvider.OPENAI, AIProvider.XAI, AIProvider.DEEPSEEK, AIProvider.OLLAMA, AIProvider.MISTRAL]:
            async for chunk in self._stream_openai_compatible(client, request):
                yield chunk
        elif model_info.provider == AIProvider.ANTHROPIC:
            async for chunk in self._stream_anthropic(client, request):
                yield chunk
        else:
            # Fallback to non-streaming
            response = await self._call_model(request)
            yield response.content
    
    async def _stream_openai_compatible(
        self, 
        client: AsyncOpenAI, 
        request: AIModelRequest
    ) -> AsyncGenerator[str, None]:
        """Stream OpenAI-compatible response"""
        response = await client.chat.completions.create(
            model=request.model_id,
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _stream_anthropic(
        self, 
        client: anthropic.AsyncAnthropic, 
        request: AIModelRequest
    ) -> AsyncGenerator[str, None]:
        """Stream Anthropic response"""
        system_message = ""
        messages = []
        
        for msg in request.messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        async with client.messages.stream(
            model=request.model_id,
            max_tokens=request.max_tokens or 4096,
            temperature=request.temperature,
            system=system_message if system_message else None,
            messages=messages
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def _update_usage_stats(self, model_id: str, start_time: float, response: AIModelResponse):
        """Update usage statistics for a model"""
        if model_id not in self.usage_stats:
            self.usage_stats[model_id] = ModelUsageStats()
        
        stats = self.usage_stats[model_id]
        stats.total_requests += 1
        stats.last_used = time.time()
        
        if response.usage:
            stats.total_tokens += response.usage.get("total_tokens", 0)
        
        # Calculate cost if available
        model_info = AVAILABLE_MODELS.get(model_id)
        if model_info and model_info.cost_per_1k_tokens and response.usage:
            cost = (response.usage.get("total_tokens", 0) / 1000) * model_info.cost_per_1k_tokens
            stats.total_cost += cost
        
        # Update average response time
        response_time = time.time() - start_time
        stats.avg_response_time = (
            (stats.avg_response_time * (stats.total_requests - 1) + response_time) / 
            stats.total_requests
        )
    
    def _update_error_stats(self, model_id: str):
        """Update error statistics for a model"""
        if model_id not in self.usage_stats:
            self.usage_stats[model_id] = ModelUsageStats()
        
        self.usage_stats[model_id].error_count += 1
    
    def get_usage_stats(self) -> Dict[str, ModelUsageStats]:
        """Get usage statistics for all models"""
        return self.usage_stats.copy()
    
    def get_model_recommendations(self, task_type: str, context_length: int = 4000) -> List[str]:
        """Get recommended models for a specific task"""
        available_models = self.get_available_models()
        
        # Filter by capability and context length
        suitable_models = []
        for model in available_models:
            if model.context_length >= context_length:
                if task_type == "code" and any(cap.value.startswith("code") for cap in model.capabilities):
                    suitable_models.append(model)
                elif task_type == "chat" and any(cap.value == "chat" for cap in model.capabilities):
                    suitable_models.append(model)
                elif task_type == "analysis" and any(cap.value == "code_analysis" for cap in model.capabilities):
                    suitable_models.append(model)
        
        # Sort by cost-effectiveness (lower cost per token is better)
        suitable_models.sort(key=lambda x: x.cost_per_1k_tokens or 0)
        
        return [model.id for model in suitable_models[:5]]

