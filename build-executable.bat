@echo off
echo 🏗️ Building Uranus-AI Executable for Windows
echo =============================================

REM Check if we're in the right directory
if not exist "ai-backend" (
    echo ❌ Error: ai-backend directory not found!
    echo Please run this script from the Uranus-AI root directory
    pause
    exit /b 1
)

if not exist "vscode" (
    echo ❌ Error: vscode directory not found!
    echo Please run this script from the Uranus-AI root directory
    pause
    exit /b 1
)

echo ✅ Project structure verified

REM Create build directories
echo 📁 Creating build directories...
if not exist "dist" mkdir dist
if not exist "build-tools" mkdir build-tools
if not exist "electron-app\build" mkdir electron-app\build

REM Step 1: Install Python dependencies for building
echo 🐍 Step 1: Installing Python build dependencies...
cd ai-backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies including PyInstaller
echo 📥 Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Step 2: Build backend executable
echo 🔨 Step 2: Building backend executable...
cd ..

REM Run PyInstaller with our spec file
echo 🚀 Running PyInstaller...
ai-backend\venv\Scripts\pyinstaller.exe --clean --noconfirm build-tools\pyinstaller.spec

REM Check if backend executable was created
if exist "dist\uranus-ai-backend.exe" (
    echo ✅ Backend executable created successfully
) else (
    echo ❌ Failed to create backend executable
    pause
    exit /b 1
)

REM Step 3: Prepare VSCode build
echo 📝 Step 3: Preparing VSCode build...
cd vscode

REM Install VSCode dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing VSCode dependencies...
    npm install
)

REM Build VSCode
echo 🔨 Building VSCode...
npm run compile-build

REM Check if VSCode build was successful
if exist "out" (
    echo ✅ VSCode build completed
) else (
    echo ❌ VSCode build failed
    cd ..
    pause
    exit /b 1
)

cd ..

REM Step 4: Prepare Electron app
echo ⚡ Step 4: Preparing Electron app...
cd electron-app

REM Install Electron dependencies
if not exist "node_modules" (
    echo 📦 Installing Electron dependencies...
    npm install
)

REM Copy backend executable to electron resources
echo 📋 Copying backend executable...
if not exist "resources" mkdir resources
if not exist "resources\backend" mkdir resources\backend
copy "..\dist\uranus-ai-backend.exe" "resources\backend\" >nul

REM Copy VSCode build to electron resources
echo 📋 Copying VSCode build...
if not exist "resources\vscode" mkdir resources\vscode
xcopy "..\vscode\out" "resources\vscode\" /E /I /Y >nul

REM Step 5: Build Electron executable
echo 🔨 Step 5: Building Electron executable...
npm run build-win

REM Check if Electron build was successful
if exist "dist" (
    echo ✅ Electron build completed
    
    REM Copy final executable to root dist folder
    if not exist "..\dist\final" mkdir ..\dist\final
    copy "dist\*.exe" "..\dist\final\" >nul
    
    echo.
    echo 🎉 BUILD COMPLETED SUCCESSFULLY!
    echo.
    echo 📦 Final executables are in: dist\final\
    echo.
    dir ..\dist\final\
    echo.
    echo 💡 You can now distribute the executable files!
    
) else (
    echo ❌ Electron build failed
    cd ..
    pause
    exit /b 1
)

cd ..

REM Step 6: Create portable package
echo 📦 Step 6: Creating portable package...
if not exist "dist\portable" mkdir dist\portable

REM Copy main executable
copy "dist\final\*.exe" "dist\portable\" >nul

REM Create README for portable version
echo Creating README for portable version...
echo # Uranus-AI Editor - Portable Version > dist\portable\README.txt
echo. >> dist\portable\README.txt
echo This is a portable version of Uranus-AI Editor. >> dist\portable\README.txt
echo. >> dist\portable\README.txt
echo To run: >> dist\portable\README.txt
echo 1. Double-click the .exe file >> dist\portable\README.txt
echo 2. The AI backend will start automatically >> dist\portable\README.txt
echo 3. The editor will open when ready >> dist\portable\README.txt
echo. >> dist\portable\README.txt
echo Features: >> dist\portable\README.txt
echo - Multi-model AI support (OpenAI, Claude, Gemini, etc.) >> dist\portable\README.txt
echo - Native AI assistant integration >> dist\portable\README.txt
echo - Code analysis and refactoring >> dist\portable\README.txt
echo - PostgreSQL configuration storage >> dist\portable\README.txt
echo. >> dist\portable\README.txt
echo For more information: https://github.com/alezzanderg/Uranus-AI >> dist\portable\README.txt

echo.
echo 🎊 COMPLETE BUILD PROCESS FINISHED!
echo.
echo 📁 Build artifacts:
echo    - Backend executable: dist\uranus-ai-backend.exe
echo    - Electron installer: dist\final\*.exe
echo    - Portable version: dist\portable\
echo.
echo 🚀 Ready for distribution!
echo.

REM Show final directory structure
echo 📋 Final build structure:
tree dist /F

echo.
echo Press any key to exit...
pause >nul

