@echo off
echo 🔨 Building Uranus-AI VSCode for Windows
echo ========================================

REM Check if we're in the right directory
if not exist "vscode" (
    echo ❌ Error: vscode directory not found!
    echo Please run this script from the Uranus-AI root directory
    pause
    exit /b 1
)

cd vscode

echo 📦 Installing dependencies...
npm install

echo 🔍 Checking available build scripts...
npm run

echo.
echo 🎯 Choose build type:
echo 1. Development build (watch mode)
echo 2. Production build
echo 3. Web build
echo 4. Show all available scripts
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🚀 Starting development build with watch mode...
    npm run watch
) else if "%choice%"=="2" (
    echo 🏗️  Starting production build...
    npm run compile-build
) else if "%choice%"=="3" (
    echo 🌐 Starting web build...
    npm run compile-web
) else if "%choice%"=="4" (
    echo 📋 All available scripts:
    npm run
    echo.
    echo Enter the script name you want to run:
    set /p script="Script name: "
    npm run %script%
) else (
    echo ❌ Invalid choice. Showing available scripts:
    npm run
)

echo.
echo ✅ Build process completed!
echo.
echo 💡 Tips:
echo - Use 'npm run watch' for development (auto-recompiles on changes)
echo - Use 'npm run compile-build' for production builds
echo - Check the VSCode documentation for more build options
echo.
pause

