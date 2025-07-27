"""
AI Models and Provider Configuration
Supports multiple AI providers: OpenAI, Claude, Gemini, Grok, DeepSeek, etc.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass


class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # Claude
    GOOGLE = "google"        # Gemini
    XAI = "xai"             # Grok
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"       # Local models
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    MISTRAL = "mistral"


class ModelCapability(str, Enum):
    """Model capabilities"""
    CHAT = "chat"
    CODE_COMPLETION = "code_completion"
    CODE_ANALYSIS = "code_analysis"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    LONG_CONTEXT = "long_context"


@dataclass
class ModelInfo:
    """Information about an AI model"""
    id: str
    name: str
    provider: AIProvider
    max_tokens: int
    context_length: int
    capabilities: List[ModelCapability]
    cost_per_1k_tokens: Optional[float] = None
    description: str = ""
    supports_streaming: bool = True


class AIModelRequest(BaseModel):
    """Request for AI model interaction"""
    model_id: str = Field(..., description="Model identifier")
    provider: AIProvider = Field(..., description="AI provider")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    stream: bool = Field(True, description="Enable streaming response")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class AIModelResponse(BaseModel):
    """Response from AI model"""
    content: str = Field(..., description="Generated content")
    model_id: str = Field(..., description="Model used")
    provider: AIProvider = Field(..., description="Provider used")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage")
    finish_reason: Optional[str] = Field(None, description="Why generation stopped")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ModelConfiguration(BaseModel):
    """Configuration for a specific model"""
    model_id: str
    provider: AIProvider
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    organization: Optional[str] = None
    enabled: bool = True
    default_params: Dict[str, Any] = Field(default_factory=dict)


class MultiModelConfig(BaseModel):
    """Configuration for multiple AI models"""
    default_model: str = Field(..., description="Default model to use")
    models: Dict[str, ModelConfiguration] = Field(..., description="Available models")
    fallback_models: List[str] = Field(default_factory=list, description="Fallback order")
    enable_model_switching: bool = Field(True, description="Allow dynamic model switching")
    enable_cost_optimization: bool = Field(False, description="Optimize for cost")


# Predefined model configurations
AVAILABLE_MODELS: Dict[str, ModelInfo] = {
    # OpenAI Models
    "gpt-4": ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider=AIProvider.OPENAI,
        max_tokens=8192,
        context_length=8192,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.FUNCTION_CALLING
        ],
        cost_per_1k_tokens=0.03,
        description="Most capable OpenAI model, excellent for complex reasoning"
    ),
    "gpt-4-turbo": ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider=AIProvider.OPENAI,
        max_tokens=4096,
        context_length=128000,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.VISION,
            ModelCapability.LONG_CONTEXT
        ],
        cost_per_1k_tokens=0.01,
        description="Latest GPT-4 with 128k context and vision capabilities"
    ),
    "gpt-3.5-turbo": ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider=AIProvider.OPENAI,
        max_tokens=4096,
        context_length=16385,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.FUNCTION_CALLING
        ],
        cost_per_1k_tokens=0.001,
        description="Fast and cost-effective for most tasks"
    ),
    
    # Anthropic Claude Models
    "claude-3-opus": ModelInfo(
        id="claude-3-opus-20240229",
        name="Claude 3 Opus",
        provider=AIProvider.ANTHROPIC,
        max_tokens=4096,
        context_length=200000,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.VISION
        ],
        cost_per_1k_tokens=0.015,
        description="Most powerful Claude model, excellent for complex analysis"
    ),
    "claude-3-sonnet": ModelInfo(
        id="claude-3-sonnet-20240229",
        name="Claude 3 Sonnet",
        provider=AIProvider.ANTHROPIC,
        max_tokens=4096,
        context_length=200000,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.VISION
        ],
        cost_per_1k_tokens=0.003,
        description="Balanced performance and cost"
    ),
    "claude-3-haiku": ModelInfo(
        id="claude-3-haiku-20240307",
        name="Claude 3 Haiku",
        provider=AIProvider.ANTHROPIC,
        max_tokens=4096,
        context_length=200000,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.LONG_CONTEXT
        ],
        cost_per_1k_tokens=0.00025,
        description="Fastest Claude model, great for quick responses"
    ),
    
    # Google Gemini Models
    "gemini-pro": ModelInfo(
        id="gemini-pro",
        name="Gemini Pro",
        provider=AIProvider.GOOGLE,
        max_tokens=8192,
        context_length=32768,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.FUNCTION_CALLING
        ],
        cost_per_1k_tokens=0.0005,
        description="Google's most capable model"
    ),
    "gemini-pro-vision": ModelInfo(
        id="gemini-pro-vision",
        name="Gemini Pro Vision",
        provider=AIProvider.GOOGLE,
        max_tokens=8192,
        context_length=32768,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.VISION
        ],
        cost_per_1k_tokens=0.0005,
        description="Gemini with vision capabilities"
    ),
    
    # xAI Grok Models
    "grok-beta": ModelInfo(
        id="grok-beta",
        name="Grok Beta",
        provider=AIProvider.XAI,
        max_tokens=4096,
        context_length=131072,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.LONG_CONTEXT
        ],
        cost_per_1k_tokens=0.005,
        description="xAI's conversational AI with real-time knowledge"
    ),
    
    # DeepSeek Models
    "deepseek-coder": ModelInfo(
        id="deepseek-coder",
        name="DeepSeek Coder",
        provider=AIProvider.DEEPSEEK,
        max_tokens=4096,
        context_length=16384,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.CODE_ANALYSIS
        ],
        cost_per_1k_tokens=0.0014,
        description="Specialized for code generation and analysis"
    ),
    "deepseek-chat": ModelInfo(
        id="deepseek-chat",
        name="DeepSeek Chat",
        provider=AIProvider.DEEPSEEK,
        max_tokens=4096,
        context_length=32768,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS
        ],
        cost_per_1k_tokens=0.0014,
        description="General purpose conversational model"
    ),
    
    # Ollama Local Models
    "llama2": ModelInfo(
        id="llama2",
        name="Llama 2",
        provider=AIProvider.OLLAMA,
        max_tokens=4096,
        context_length=4096,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_COMPLETION
        ],
        cost_per_1k_tokens=0.0,  # Local model, no cost
        description="Meta's Llama 2 running locally"
    ),
    "codellama": ModelInfo(
        id="codellama",
        name="Code Llama",
        provider=AIProvider.OLLAMA,
        max_tokens=4096,
        context_length=16384,
        capabilities=[
            ModelCapability.CODE_COMPLETION,
            ModelCapability.CODE_ANALYSIS
        ],
        cost_per_1k_tokens=0.0,
        description="Specialized code model running locally"
    ),
    
    # Mistral Models
    "mistral-large": ModelInfo(
        id="mistral-large-latest",
        name="Mistral Large",
        provider=AIProvider.MISTRAL,
        max_tokens=8192,
        context_length=32768,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.FUNCTION_CALLING
        ],
        cost_per_1k_tokens=0.008,
        description="Mistral's most capable model"
    ),
    "mistral-medium": ModelInfo(
        id="mistral-medium-latest",
        name="Mistral Medium",
        provider=AIProvider.MISTRAL,
        max_tokens=8192,
        context_length=32768,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS
        ],
        cost_per_1k_tokens=0.0027,
        description="Balanced performance model"
    ),
    
    # Cohere Models
    "command-r-plus": ModelInfo(
        id="command-r-plus",
        name="Command R+",
        provider=AIProvider.COHERE,
        max_tokens=4096,
        context_length=128000,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_ANALYSIS,
            ModelCapability.LONG_CONTEXT
        ],
        cost_per_1k_tokens=0.003,
        description="Cohere's most advanced model"
    )
}


def get_models_by_capability(capability: ModelCapability) -> List[ModelInfo]:
    """Get all models that support a specific capability"""
    return [model for model in AVAILABLE_MODELS.values() 
            if capability in model.capabilities]


def get_models_by_provider(provider: AIProvider) -> List[ModelInfo]:
    """Get all models from a specific provider"""
    return [model for model in AVAILABLE_MODELS.values() 
            if model.provider == provider]


def get_cheapest_models(capability: ModelCapability, limit: int = 5) -> List[ModelInfo]:
    """Get the cheapest models for a specific capability"""
    models = get_models_by_capability(capability)
    # Filter out models without cost info (local models)
    models_with_cost = [m for m in models if m.cost_per_1k_tokens is not None]
    return sorted(models_with_cost, key=lambda x: x.cost_per_1k_tokens)[:limit]


def get_recommended_model(task_type: str, context_length_needed: int = 4000) -> Optional[ModelInfo]:
    """Get recommended model based on task type and requirements"""
    recommendations = {
        "chat": ["gpt-4-turbo", "claude-3-sonnet", "gemini-pro"],
        "code_completion": ["deepseek-coder", "codellama", "gpt-3.5-turbo"],
        "code_analysis": ["claude-3-opus", "gpt-4", "deepseek-coder"],
        "long_context": ["claude-3-sonnet", "gpt-4-turbo", "command-r-plus"],
        "cost_effective": ["gpt-3.5-turbo", "claude-3-haiku", "gemini-pro"]
    }
    
    model_ids = recommendations.get(task_type, ["gpt-4"])
    
    for model_id in model_ids:
        if model_id in AVAILABLE_MODELS:
            model = AVAILABLE_MODELS[model_id]
            if model.context_length >= context_length_needed:
                return model
    
    return AVAILABLE_MODELS.get("gpt-4")  # Fallback

