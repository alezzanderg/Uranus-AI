"""
Chat service for AI interactions.
"""
import json
import time
import uuid
from typing import Dict, List, Optional, AsyncGenerator
from openai import AsyncOpenAI
from loguru import logger

from ..config import settings
from ..models.chat_models import (
    ChatMessage, ChatRequest, ChatResponse, Conversation,
    MessageRole, MessageType, StreamingChatResponse, AiContext
)


class ChatService:
    """Service for handling AI chat interactions."""
    
    def __init__(self):
        """Initialize the chat service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.conversations: Dict[str, Conversation] = {}
        self.max_history = settings.max_conversation_history
        
    async def process_chat_message(
        self, 
        request: ChatRequest,
        user_id: str = "default"
    ) -> ChatResponse:
        """Process a chat message and return AI response."""
        try:
            start_time = time.time()
            
            # Get or create conversation
            conversation_id = request.conversation_id or f"{user_id}_{int(time.time())}"
            conversation = self.get_or_create_conversation(conversation_id)
            
            # Build system message with context
            system_message = self._build_system_message(request.context)
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history
            for msg in conversation.messages[-self.max_history:]:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({
                "role": MessageRole.USER.value,
                "content": request.message
            })
            
            # Generate AI response
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            # Create message objects
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.USER,
                content=request.message,
                context=request.context
            )
            
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=ai_response
            )
            
            # Update conversation
            conversation.messages.extend([user_message, assistant_message])
            conversation.updated_at = int(time.time())
            
            # Trim conversation if too long
            if len(conversation.messages) > self.max_history * 2:
                conversation.messages = conversation.messages[-self.max_history * 2:]
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return ChatResponse(
                id=assistant_message.id,
                response=ai_response,
                conversation_id=conversation_id,
                message_type=request.message_type,
                tokens_used=tokens_used,
                model_used=settings.openai_model,
                metadata={
                    "processing_time_ms": processing_time,
                    "user_message_id": user_message.id
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            raise
    
    async def stream_chat_message(
        self,
        request: ChatRequest,
        user_id: str = "default"
    ) -> AsyncGenerator[StreamingChatResponse, None]:
        """Stream AI response for real-time chat."""
        try:
            conversation_id = request.conversation_id or f"{user_id}_{int(time.time())}"
            conversation = self.get_or_create_conversation(conversation_id)
            
            # Build system message with context
            system_message = self._build_system_message(request.context)
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history
            for msg in conversation.messages[-self.max_history:]:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({
                "role": MessageRole.USER.value,
                "content": request.message
            })
            
            # Stream response from OpenAI
            stream = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                stream=True
            )
            
            response_id = str(uuid.uuid4())
            full_response = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    chunk_content = chunk.choices[0].delta.content
                    full_response += chunk_content
                    
                    yield StreamingChatResponse(
                        id=response_id,
                        conversation_id=conversation_id,
                        chunk=chunk_content,
                        is_complete=False
                    )
            
            # Send completion signal
            yield StreamingChatResponse(
                id=response_id,
                conversation_id=conversation_id,
                chunk="",
                is_complete=True
            )
            
            # Save complete conversation
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.USER,
                content=request.message,
                context=request.context
            )
            
            assistant_message = ChatMessage(
                id=response_id,
                role=MessageRole.ASSISTANT,
                content=full_response
            )
            
            conversation.messages.extend([user_message, assistant_message])
            conversation.updated_at = int(time.time())
            
        except Exception as e:
            logger.error(f"Error streaming chat message: {str(e)}")
            yield StreamingChatResponse(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                chunk=f"Error: {str(e)}",
                is_complete=True
            )
    
    def get_or_create_conversation(self, conversation_id: str) -> Conversation:
        """Get existing conversation or create new one."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(
                id=conversation_id,
                title=f"Conversation {len(self.conversations) + 1}"
            )
        return self.conversations[conversation_id]
    
    def get_conversation_history(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation history."""
        return self.conversations.get(conversation_id)
    
    def clear_conversation_history(self, conversation_id: str) -> bool:
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    def list_conversations(self, user_id: str = "default") -> List[str]:
        """List all conversation IDs for a user."""
        return [
            conv_id for conv_id in self.conversations.keys()
            if conv_id.startswith(user_id)
        ]
    
    def _build_system_message(self, context: Optional[AiContext]) -> str:
        """Build system message with context information."""
        system_parts = [
            "You are an AI assistant integrated into a code editor.",
            "Help the user with coding tasks, explanations, and improvements.",
            "Provide clear, concise, and helpful responses.",
            "When discussing code, use proper formatting and explain your reasoning."
        ]
        
        if context:
            if context.editor:
                editor_info = context.editor
                if editor_info.get('fileName'):
                    system_parts.append(f"Current file: {editor_info['fileName']}")
                if editor_info.get('language'):
                    system_parts.append(f"Language: {editor_info['language']}")
            
            if context.selection:
                selection = context.selection
                system_parts.append(f"Selected code:\n```\n{selection['text']}\n```")
            
            if context.workspace:
                workspace = context.workspace
                if workspace.get('name'):
                    system_parts.append(f"Workspace: {workspace['name']}")
            
            if context.project_info:
                project_info = context.project_info
                if project_info.get('type'):
                    system_parts.append(f"Project type: {project_info['type']}")
        
        return "\n\n".join(system_parts)


# Global chat service instance
chat_service = ChatService()


def get_chat_service() -> ChatService:
    """Get the chat service instance."""
    return chat_service

