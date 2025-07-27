#!/usr/bin/env python3
"""
Test script for AI Assistant Backend
"""
import asyncio
import json
import websockets
import requests
import time
import sys
import os

# Backend configuration
BACKEND_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws"

def test_http_endpoints():
    """Test HTTP API endpoints"""
    print("🧪 Testing HTTP API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test status endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/status")
        if response.status_code == 200:
            print("✅ Status endpoint working")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test chat endpoint
    try:
        chat_data = {
            "message": "Hello, this is a test message",
            "context": {
                "editor": {
                    "language": "python",
                    "fileName": "test.py"
                }
            }
        }
        response = requests.post(f"{BACKEND_URL}/api/v1/chat/message", json=chat_data)
        if response.status_code == 200:
            print("✅ Chat endpoint working")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
    
    # Test code analysis endpoint
    try:
        code_data = {
            "code": "def hello():\n    print('Hello World')",
            "language": "python",
            "analysis_types": ["syntax", "style"]
        }
        response = requests.post(f"{BACKEND_URL}/api/v1/code/analyze", json=code_data)
        if response.status_code == 200:
            print("✅ Code analysis endpoint working")
        else:
            print(f"❌ Code analysis endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Code analysis endpoint error: {e}")
    
    return True

async def test_websocket():
    """Test WebSocket connection"""
    print("🧪 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✅ WebSocket connection established")
            
            # Send ping message
            ping_message = {
                "type": "ping",
                "id": "test_ping",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "pong":
                print("✅ WebSocket ping/pong working")
            else:
                print(f"❌ Unexpected WebSocket response: {response_data}")
            
            # Send chat message
            chat_message = {
                "type": "chat",
                "id": "test_chat",
                "message": "Hello via WebSocket",
                "context": {
                    "editor": {
                        "language": "javascript",
                        "fileName": "test.js"
                    }
                }
            }
            await websocket.send(json.dumps(chat_message))
            
            # Wait for chat response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "chat_response":
                print("✅ WebSocket chat working")
            else:
                print(f"❌ Unexpected chat response: {response_data}")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def check_backend_running():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test function"""
    print("🚀 AI Assistant Backend Test Suite")
    print("=" * 50)
    
    # Check if backend is running
    if not check_backend_running():
        print("❌ Backend is not running!")
        print(f"Please start the backend first:")
        print(f"cd ai-backend && python -m app.main")
        sys.exit(1)
    
    print("✅ Backend is running")
    
    # Test HTTP endpoints
    if not test_http_endpoints():
        print("❌ HTTP tests failed")
        sys.exit(1)
    
    # Test WebSocket
    if not asyncio.run(test_websocket()):
        print("❌ WebSocket tests failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("Backend is ready for integration with Code-OSS")

if __name__ == "__main__":
    main()

