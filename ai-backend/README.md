# AI Assistant Backend

Backend service for the AI Assistant integrated into Code-OSS editor. Provides chat, code analysis, and completion services through REST API and WebSocket connections.

## Features

- **Chat Service**: Conversational AI with context awareness
- **Code Analysis**: Static analysis and AI-powered insights
- **Code Completion**: Intelligent code suggestions
- **WebSocket Support**: Real-time communication
- **Streaming Responses**: Real-time AI response streaming
- **Multi-language Support**: Python, JavaScript, TypeScript, and more

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Redis (optional, for caching)
- PostgreSQL (optional, for persistent storage)

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd ai-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. The service will be available at `http://localhost:8000`

## API Endpoints

### Chat API

- `POST /api/v1/chat/message` - Send chat message
- `POST /api/v1/chat/stream` - Stream chat response
- `GET /api/v1/chat/conversations` - List conversations
- `GET /api/v1/chat/conversations/{id}` - Get conversation
- `DELETE /api/v1/chat/conversations/{id}` - Clear conversation

### Code API

- `POST /api/v1/code/analyze` - Analyze code
- `POST /api/v1/code/complete` - Get code completions
- `POST /api/v1/code/explain` - Explain code
- `POST /api/v1/code/refactor` - Get refactoring suggestions
- `POST /api/v1/code/find-bugs` - Find potential bugs
- `POST /api/v1/code/generate-tests` - Generate unit tests

### WebSocket

- `WS /ws` - Real-time communication endpoint

### System

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/v1/status` - Detailed status
- `GET /docs` - Interactive API documentation

## Configuration

Key environment variables:

```bash
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000

# OpenAI
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2048

# Database
DATABASE_URL=sqlite:///./ai_assistant.db

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## WebSocket Protocol

### Message Format

```json
{
  "type": "chat|code_analysis|completion|ping",
  "id": "unique_message_id",
  "message": "content",
  "context": {},
  "stream": false
}
```

### Response Format

```json
{
  "type": "chat_response|analysis_response|completion_response|error",
  "id": "message_id",
  "response": "content",
  "status": "success|error"
}
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
isort app/
flake8 app/
```

### Adding New Services

1. Create service in `app/services/`
2. Add models in `app/models/`
3. Create API routes in `app/api/`
4. Register routes in `app/main.py`

## Architecture

```
app/
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── models/              # Data models
│   ├── chat_models.py
│   └── code_models.py
├── services/            # Business logic
│   ├── chat_service.py
│   ├── code_analysis_service.py
│   └── completion_service.py
├── api/                 # API routes
│   ├── chat_routes.py
│   ├── code_routes.py
│   └── websocket_routes.py
└── utils/               # Utilities
```

## Performance

- Async/await for non-blocking operations
- Connection pooling for database
- Redis caching for frequent requests
- Rate limiting to prevent abuse
- Streaming responses for real-time experience

## Security

- CORS configuration
- Input validation
- Rate limiting
- Error handling
- Secure WebSocket connections

## Monitoring

- Health check endpoints
- Structured logging
- Performance metrics
- Error tracking

## License

MIT License - see LICENSE file for details.

