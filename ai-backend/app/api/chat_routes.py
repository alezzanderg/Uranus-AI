"""
API routes for chat functionality.
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from loguru import logger

from ..models.chat_models import (
    ChatRequest, ChatResponse, Conversation, ConversationSummary
)
from ..services.chat_service import ChatService, get_chat_service


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a chat message and get AI response."""
    try:
        response = await chat_service.process_chat_message(request)
        return response
    except Exception as e:
        logger.error(f"Error in send_chat_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_chat_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Stream AI response for real-time chat."""
    try:
        async def generate():
            async for chunk in chat_service.stream_chat_message(request):
                yield f"data: {chunk.json()}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    except Exception as e:
        logger.error(f"Error in stream_chat_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=List[str])
async def list_conversations(
    user_id: str = "default",
    chat_service: ChatService = Depends(get_chat_service)
):
    """List all conversations for a user."""
    try:
        conversations = chat_service.list_conversations(user_id)
        return conversations
    except Exception as e:
        logger.error(f"Error in list_conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get conversation history."""
    try:
        conversation = chat_service.get_conversation_history(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Clear conversation history."""
    try:
        success = chat_service.clear_conversation_history(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "cleared", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in clear_conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Update conversation title."""
    try:
        conversation = chat_service.get_conversation_history(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.title = title
        return {"status": "updated", "conversation_id": conversation_id, "title": title}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_conversation_title: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

