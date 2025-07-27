@echo off
echo 🪐 Starting Uranus-AI Editor for Windows
echo ========================================

REM Check if we're in the right directory
if not exist "vscode" (
    echo ❌ Error: vscode directory not found!
    echo Please run this script from the Uranus-AI root directory
    pause
    exit /b 1
)

if not exist "ai-backend" (
    echo ❌ Error: ai-backend directory not found!
    echo Please run this script from the Uranus-AI root directory
    pause
    exit /b 1
)

echo ✅ Directories found, starting services...

REM Start AI Backend
echo 🚀 Starting AI Backend...
cd ai-backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo Please copy .env.example to .env and configure your API keys
    echo.
    echo Creating .env from example...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your API keys before continuing!
    echo Press any key to continue anyway...
    pause
)

REM Start backend in background
echo 🌐 Starting FastAPI backend...
start "Uranus-AI Backend" cmd /k "venv\Scripts\activate.bat && python -m app.main"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Go back to root directory
cd ..

REM Start VSCode compilation
echo 🔨 Preparing VSCode...
cd vscode

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
) else (
    echo ✅ Node.js dependencies already installed
)

REM Check available scripts
echo 📋 Available npm scripts:
npm run

echo.
echo 🎯 To compile VSCode, run one of these commands:
echo    npm run watch          (for development with auto-reload)
echo    npm run compile-build  (for production build)
echo    npm run compile-web    (for web version)
echo.

REM Try to start development mode
echo 🚀 Starting VSCode in development mode...
echo If this fails, check the available scripts above and run manually
npm run watch

echo.
echo 🎉 Uranus-AI Editor should now be running!
echo.
echo 📍 Backend API: http://localhost:8000
echo 📍 Backend Docs: http://localhost:8000/docs
echo 📍 VSCode: Follow the compilation output above
echo.
echo Press any key to exit...
pause

