#!/bin/bash
set -e

echo "🚀 Building Code-OSS with AI Assistant Integration"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Not in VSCode root directory"
    echo "Please run this script from the vscode directory"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version)
echo "📦 Node.js version: $NODE_VERSION"

# Check if AI Assistant module exists
if [ ! -d "src/vs/workbench/contrib/aiAssistant" ]; then
    echo "❌ Error: AI Assistant module not found"
    echo "Please ensure the AI Assistant module is properly installed"
    exit 1
fi

echo "✅ AI Assistant module found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building Code-OSS..."
npm run compile

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo ""
    echo "🎉 Code-OSS with AI Assistant is ready!"
    echo ""
    echo "To run the editor:"
    echo "  npm start"
    echo ""
    echo "Or for development mode:"
    echo "  npm run watch"
    echo ""
    echo "The AI Assistant will appear in the Secondary Sidebar (right panel)"
    echo "Make sure to start the AI backend before using AI features:"
    echo "  cd ../ai-backend && python -m app.main"
else
    echo "❌ Build failed!"
    exit 1
fi

