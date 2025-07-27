"""
WebSocket routes for real-time communication.
"""
import json
import uuid
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from loguru import logger

from ..models.chat_models import ChatRequest, MessageType
from ..services.chat_service import get_chat_service


router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = "default"):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"WebSocket connection established: {connection_id} for user {user_id}")
    
    def disconnect(self, connection_id: str, user_id: str = "default"):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket connection closed: {connection_id} for user {user_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {str(e)}")
                # Remove broken connection
                self.disconnect(connection_id)
    
    async def send_user_message(self, message: dict, user_id: str):
        """Send a message to all connections of a user."""
        if user_id in self.user_connections:
            for connection_id in list(self.user_connections[user_id]):
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connections."""
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for AI Assistant communication."""
    connection_id = str(uuid.uuid4())
    user_id = "default"  # In a real app, this would come from authentication
    
    await manager.connect(websocket, connection_id, user_id)
    
    # Send welcome message
    await manager.send_personal_message({
        "type": "connection",
        "status": "connected",
        "connection_id": connection_id,
        "message": "Connected to AI Assistant"
    }, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(message, connection_id, user_id)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, connection_id)
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                }, connection_id)
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(connection_id, user_id)


async def handle_websocket_message(message: dict, connection_id: str, user_id: str):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type", "unknown")
    message_id = message.get("id", str(uuid.uuid4()))
    
    try:
        if message_type == "chat":
            await handle_chat_message(message, connection_id, user_id, message_id)
        elif message_type == "code_analysis":
            await handle_code_analysis_message(message, connection_id, user_id, message_id)
        elif message_type == "completion":
            await handle_completion_message(message, connection_id, user_id, message_id)
        elif message_type == "ping":
            await manager.send_personal_message({
                "type": "pong",
                "id": message_id,
                "timestamp": message.get("timestamp")
            }, connection_id)
        else:
            await manager.send_personal_message({
                "type": "error",
                "id": message_id,
                "message": f"Unknown message type: {message_type}"
            }, connection_id)
    
    except Exception as e:
        logger.error(f"Error handling {message_type} message: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "id": message_id,
            "message": f"Error processing {message_type}: {str(e)}"
        }, connection_id)


async def handle_chat_message(message: dict, connection_id: str, user_id: str, message_id: str):
    """Handle chat messages via WebSocket."""
    chat_service = get_chat_service()
    
    # Send acknowledgment
    await manager.send_personal_message({
        "type": "chat_status",
        "id": message_id,
        "status": "processing",
        "message": "Processing your message..."
    }, connection_id)
    
    try:
        # Create chat request
        request = ChatRequest(
            message=message.get("message", ""),
            context=message.get("context"),
            conversation_id=message.get("conversation_id"),
            message_type=MessageType.CHAT
        )
        
        # Check if streaming is requested
        if message.get("stream", False):
            # Handle streaming response
            async for chunk in chat_service.stream_chat_message(request, user_id):
                await manager.send_personal_message({
                    "type": "chat_stream",
                    "id": message_id,
                    "conversation_id": chunk.conversation_id,
                    "chunk": chunk.chunk,
                    "is_complete": chunk.is_complete
                }, connection_id)
        else:
            # Handle regular response
            response = await chat_service.process_chat_message(request, user_id)
            
            await manager.send_personal_message({
                "type": "chat_response",
                "id": message_id,
                "response": response.response,
                "conversation_id": response.conversation_id,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used
            }, connection_id)
    
    except Exception as e:
        await manager.send_personal_message({
            "type": "chat_error",
            "id": message_id,
            "message": f"Chat error: {str(e)}"
        }, connection_id)


async def handle_code_analysis_message(message: dict, connection_id: str, user_id: str, message_id: str):
    """Handle code analysis messages via WebSocket."""
    from ..services.code_analysis_service import get_code_analysis_service
    from ..models.code_models import CodeAnalysisRequest, CodeLanguage
    
    analysis_service = get_code_analysis_service()
    
    # Send acknowledgment
    await manager.send_personal_message({
        "type": "analysis_status",
        "id": message_id,
        "status": "processing",
        "message": "Analyzing code..."
    }, connection_id)
    
    try:
        # Create analysis request
        request = CodeAnalysisRequest(
            code=message.get("code", ""),
            language=CodeLanguage(message.get("language", "python")),
            file_path=message.get("file_path"),
            context=message.get("context"),
            analysis_types=message.get("analysis_types", ["syntax", "style", "complexity", "suggestions"])
        )
        
        response = await analysis_service.analyze_code(request)
        
        await manager.send_personal_message({
            "type": "analysis_response",
            "id": message_id,
            "analysis": response.dict()
        }, connection_id)
    
    except Exception as e:
        await manager.send_personal_message({
            "type": "analysis_error",
            "id": message_id,
            "message": f"Analysis error: {str(e)}"
        }, connection_id)


async def handle_completion_message(message: dict, connection_id: str, user_id: str, message_id: str):
    """Handle code completion messages via WebSocket."""
    from ..services.completion_service import get_completion_service
    from ..models.code_models import CodeCompletionRequest, CodeLanguage
    
    completion_service = get_completion_service()
    
    try:
        # Create completion request
        request = CodeCompletionRequest(
            prefix=message.get("prefix", ""),
            suffix=message.get("suffix", ""),
            language=CodeLanguage(message.get("language", "python")),
            file_path=message.get("file_path"),
            context=message.get("context"),
            max_completions=message.get("max_completions", 5)
        )
        
        response = await completion_service.get_completions(request)
        
        await manager.send_personal_message({
            "type": "completion_response",
            "id": message_id,
            "completions": [comp.dict() for comp in response.completions]
        }, connection_id)
    
    except Exception as e:
        await manager.send_personal_message({
            "type": "completion_error",
            "id": message_id,
            "message": f"Completion error: {str(e)}"
        }, connection_id)


def get_connection_manager() -> ConnectionManager:
    """Get the connection manager instance."""
    return manager

