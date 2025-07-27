"""
Data models for chat functionality.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Roles for chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Types of messages."""
    CHAT = "chat"
    CODE_ANALYSIS = "code_analysis"
    COMPLETION = "completion"
    STATUS = "status"
    ERROR = "error"


class AiContext(BaseModel):
    """Context information for AI requests."""
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    workspace: Optional[Dict[str, Any]] = None
    editor: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    open_files: List[Dict[str, Any]] = Field(default_factory=list)
    project_info: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    """Individual chat message."""
    id: str
    role: MessageRole
    content: str
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    context: Optional[AiContext] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request for chat interaction."""
    message: str = Field(..., min_length=1, max_length=10000)
    context: Optional[AiContext] = None
    conversation_id: Optional[str] = None
    message_type: MessageType = MessageType.CHAT
    stream: bool = False


class ChatResponse(BaseModel):
    """Response from chat interaction."""
    id: str
    response: str
    conversation_id: str
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    message_type: MessageType = MessageType.CHAT
    metadata: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class Conversation(BaseModel):
    """Complete conversation thread."""
    id: str
    title: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    metadata: Optional[Dict[str, Any]] = None


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing purposes."""
    id: str
    title: Optional[str] = None
    message_count: int
    created_at: int
    updated_at: int
    last_message_preview: Optional[str] = None


class StreamingChatResponse(BaseModel):
    """Streaming response chunk for chat."""
    id: str
    conversation_id: str
    chunk: str
    is_complete: bool = False
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    metadata: Optional[Dict[str, Any]] = None

