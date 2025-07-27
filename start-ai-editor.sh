#!/bin/bash

echo "🤖 Starting AI-Enhanced Code Editor"
echo "=================================="

# Function to check if a process is running
check_process() {
    pgrep -f "$1" > /dev/null
}

# Function to start backend
start_backend() {
    echo "🚀 Starting AI Backend..."
    cd ai-backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/.deps_installed" ]; then
        echo "📦 Installing backend dependencies..."
        pip install -r requirements.txt
        touch venv/.deps_installed
    fi
    
    # Set environment variables
    export OPENAI_API_KEY="${OPENAI_API_KEY:-your_openai_key_here}"
    export DEBUG=true
    export HOST=0.0.0.0
    export PORT=8000
    
    # Start backend in background
    python -m app.main &
    BACKEND_PID=$!
    echo "✅ AI Backend started (PID: $BACKEND_PID)"
    
    cd ..
    return $BACKEND_PID
}

# Function to start VSCode
start_vscode() {
    echo "🚀 Starting Code-OSS..."
    cd vscode
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing VSCode dependencies..."
        npm install
    fi
    
    # Check if compiled
    if [ ! -d "out" ]; then
        echo "🔨 Compiling Code-OSS..."
        npm run compile
    fi
    
    # Start VSCode
    npm start &
    VSCODE_PID=$!
    echo "✅ Code-OSS started (PID: $VSCODE_PID)"
    
    cd ..
    return $VSCODE_PID
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping AI Backend..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$VSCODE_PID" ]; then
        echo "Stopping Code-OSS..."
        kill $VSCODE_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "app.main" 2>/dev/null || true
    pkill -f "code-oss" 2>/dev/null || true
    
    echo "✅ Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Check directories
if [ ! -d "ai-backend" ]; then
    echo "❌ AI Backend directory not found"
    exit 1
fi

if [ ! -d "vscode" ]; then
    echo "❌ VSCode directory not found"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start services
start_backend
BACKEND_PID=$!

# Wait a moment for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Test backend
echo "🧪 Testing backend connection..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is responding"
else
    echo "❌ Backend is not responding"
    cleanup
    exit 1
fi

start_vscode
VSCODE_PID=$!

echo ""
echo "🎉 AI-Enhanced Code Editor is running!"
echo ""
echo "📍 Services:"
echo "  - AI Backend: http://localhost:8000"
echo "  - Code-OSS: Running in new window"
echo ""
echo "🤖 AI Assistant Features:"
echo "  - Chat with AI about your code"
echo "  - Code explanation and analysis"
echo "  - Refactoring suggestions"
echo "  - Bug detection"
echo "  - Test generation"
echo ""
echo "📖 Usage:"
echo "  1. Look for the AI Assistant icon in the right sidebar"
echo "  2. Click to open the AI Assistant panel"
echo "  3. Start chatting or select code and use context menu actions"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait

