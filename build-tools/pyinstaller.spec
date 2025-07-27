# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Uranus-AI Backend
Creates a single executable file with all dependencies
"""

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
backend_path = project_root / "ai-backend"
app_path = backend_path / "app"

# Add the backend path to Python path
sys.path.insert(0, str(backend_path))

block_cipher = None

# Data files to include
datas = [
    # Include all Python files from app directory
    (str(app_path), 'app'),
    
    # Include configuration files
    (str(backend_path / '.env.example'), '.'),
    
    # Include any additional data files
    (str(backend_path / 'requirements.txt'), '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    # FastAPI and dependencies
    'fastapi',
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.websockets',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    
    # SQLAlchemy and PostgreSQL
    'sqlalchemy',
    'sqlalchemy.dialects.postgresql',
    'psycopg2',
    'alembic',
    
    # AI providers
    'openai',
    'anthropic',
    'google.generativeai',
    'cohere',
    
    # Cryptography
    'cryptography',
    'cryptography.fernet',
    
    # Other dependencies
    'pydantic',
    'httpx',
    'websockets',
    'json',
    'logging',
    'asyncio',
    'concurrent.futures',
    
    # App modules
    'app.main',
    'app.config',
    'app.database',
    'app.database.connection',
    'app.database.models',
    'app.database.config_service',
    'app.database.migration',
    'app.services.multi_model_service',
    'app.api.chat_routes',
    'app.api.code_routes',
    'app.api.websocket_routes',
    'app.api.multi_model_routes',
]

# Binaries to include
binaries = []

# Analysis configuration
a = Analysis(
    [str(backend_path / 'app' / 'main.py')],
    pathex=[str(backend_path)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'numpy.random._examples',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='uranus-ai-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'uranus-ai.ico') if (project_root / 'assets' / 'uranus-ai.ico').exists() else None,
    version_file=str(project_root / 'build-tools' / 'version_info.txt') if (project_root / 'build-tools' / 'version_info.txt').exists() else None,
)

