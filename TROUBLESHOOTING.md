# 🔧 Troubleshooting Guide - Uranus-AI

Guía completa para resolver problemas comunes en Uranus-AI.

## 🚨 Problemas Comunes

### 1. Problemas de Compilación

#### Error: "npm run compile" no existe
```
npm ERR! Missing script: "compile"
```

**Causa**: VSCode no tiene un script `compile` genérico.

**Solución**:
```bash
# Ver scripts disponibles
cd vscode && npm run

# Usar scripts específicos
npm run watch          # Para desarrollo
npm run compile-build  # Para producción
npm run compile-web    # Para versión web
```

#### Error: Dependencias faltantes
```
Error: Cannot find module 'xyz'
```

**Solución**:
```bash
# Limpiar e instalar dependencias
cd vscode
rm -rf node_modules package-lock.json
npm install

# O usar el script del proyecto
npm run install-frontend
```

### 2. Problemas del Backend

#### Error: Puerto en uso
```
Error: [Errno 48] Address already in use
```

**Solución**:
```bash
# Encontrar proceso usando el puerto
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Cambiar puerto en .env
PORT=8001

# O matar el proceso
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

#### Error: API Key inválida
```
Error: Invalid API key provided
```

**Solución**:
1. Verificar que la API key esté en `.env`:
```env
OPENAI_API_KEY=sk-...  # Debe empezar con sk-
```

2. Verificar que el archivo `.env` esté en `ai-backend/`:
```bash
cd ai-backend
ls -la .env  # Debe existir
```

3. Verificar formato correcto:
```env
# Correcto
OPENAI_API_KEY=sk-1234567890abcdef

# Incorrecto (con espacios o comillas)
OPENAI_API_KEY = "sk-1234567890abcdef"
```

### 3. Problemas de Conexión

#### Error: Backend no responde
```
Error: Connection refused to localhost:8000
```

**Verificación**:
```bash
# Verificar que el backend esté ejecutándose
curl http://localhost:8000/health

# O en Windows PowerShell
Invoke-RestMethod http://localhost:8000/health
```

**Solución**:
```bash
# Iniciar backend manualmente
cd ai-backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python -m app.main
```

#### Error: CORS
```
Access to fetch at 'http://localhost:8000' from origin 'vscode-file://' has been blocked by CORS policy
```

**Solución**: Verificar configuración CORS en `.env`:
```env
BACKEND_CORS_ORIGINS=["http://localhost:3000", "vscode-file://vscode-app", "http://localhost:8080"]
```

### 4. Problemas de Modelos

#### Error: Modelo no disponible
```
Error: Model 'gpt-4' not available
```

**Verificación**:
```bash
# Ver modelos disponibles
curl http://localhost:8000/api/v1/models/available
```

**Solución**:
1. Verificar API key del proveedor
2. Verificar que el modelo esté soportado
3. Usar modelo alternativo:
```env
DEFAULT_MODEL=gpt-3.5-turbo
```

#### Error: Límite de tokens excedido
```
Error: This model's maximum context length is 4096 tokens
```

**Solución**:
1. Usar modelo con mayor contexto:
```typescript
// En el frontend, seleccionar modelo con más contexto
const model = 'claude-3-sonnet';  // 200K contexto
```

2. Reducir el contexto enviado
3. Configurar límites en `.env`:
```env
MAX_CONTEXT_LENGTH=8000
```

### 5. Problemas de Windows

#### Error: Scripts .sh no funcionan
```
'./start-ai-editor.sh' is not recognized as an internal or external command
```

**Solución**: Usar scripts .bat para Windows:
```powershell
.\start-ai-editor.bat
.\build-vscode.bat
```

#### Error: Política de ejecución
```
Execution of scripts is disabled on this system
```

**Solución**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Error: Python no encontrado
```
'python' is not recognized as an internal or external command
```

**Solución**:
1. Instalar Python desde python.org
2. Marcar "Add to PATH" durante instalación
3. O usar `py` en lugar de `python`:
```powershell
py -m venv venv
```

### 6. Problemas de Rendimiento

#### Backend lento
**Síntomas**: Respuestas tardías del AI

**Solución**:
1. Verificar modelo usado:
```env
# Usar modelos más rápidos
DEFAULT_MODEL=claude-3-haiku  # Más rápido
FALLBACK_MODELS=["gpt-3.5-turbo", "gemini-pro"]
```

2. Optimizar configuración:
```env
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT_SECONDS=30
```

#### VSCode lento al compilar
**Síntomas**: Compilación tarda mucho

**Solución**:
1. Usar modo watch en lugar de compilación completa:
```bash
npm run watch  # En lugar de compile-build
```

2. Excluir archivos innecesarios:
```json
// En tsconfig.json
{
  "exclude": ["node_modules", "out", "dist"]
}
```

### 7. Problemas de Memoria

#### Error: Out of memory
```
FATAL ERROR: Ineffective mark-compacts near heap limit
```

**Solución**:
```bash
# Aumentar memoria para Node.js
export NODE_OPTIONS="--max-old-space-size=8192"

# En Windows
set NODE_OPTIONS=--max-old-space-size=8192
```

#### Backend consume mucha memoria
**Solución**: Configurar límites en `.env`:
```env
MAX_CONVERSATION_HISTORY=10
ENABLE_RESPONSE_CACHING=true
CACHE_TTL_SECONDS=1800
```

## 🔍 Herramientas de Diagnóstico

### 1. Verificar Estado del Sistema
```bash
# Script de diagnóstico completo
./diagnose.sh  # Linux/Mac
.\diagnose.bat  # Windows
```

### 2. Logs Detallados

#### Backend Logs
```bash
# Ver logs en tiempo real
tail -f ai-backend/logs/uranus-ai.log

# En Windows
Get-Content ai-backend\logs\uranus-ai.log -Wait
```

#### Frontend Logs
Los logs aparecen en la consola donde ejecutaste `npm run watch`.

### 3. Verificar Configuración
```bash
# Verificar variables de entorno
cd ai-backend
python -c "from app.config import get_settings; print(get_settings())"
```

### 4. Test de Conectividad
```bash
# Test completo de API
python ai-backend/test-backend.py

# Test específico de modelo
curl -X POST http://localhost:8000/api/v1/models/generate \
  -H "Content-Type: application/json" \
  -d '{"model_id": "gpt-3.5-turbo", "provider": "openai", "messages": [{"role": "user", "content": "Hello"}]}'
```

## 🛠️ Scripts de Diagnóstico

### diagnose.sh (Linux/Mac)
```bash
#!/bin/bash
echo "🔍 Uranus-AI Diagnostic Tool"
echo "============================"

echo "📋 System Information:"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python --version)"

echo "🔌 Backend Status:"
curl -s http://localhost:8000/health || echo "❌ Backend not responding"

echo "📦 Dependencies:"
cd vscode && npm list --depth=0
cd ../ai-backend && pip list | grep -E "(fastapi|openai|anthropic)"

echo "🔧 Configuration:"
ls -la ai-backend/.env || echo "❌ .env file not found"
```

### diagnose.bat (Windows)
```batch
@echo off
echo 🔍 Uranus-AI Diagnostic Tool
echo ============================

echo 📋 System Information:
node --version
npm --version
python --version

echo 🔌 Backend Status:
curl -s http://localhost:8000/health || echo ❌ Backend not responding

echo 📦 Dependencies:
cd vscode && npm list --depth=0
cd ..\ai-backend && pip list | findstr "fastapi openai anthropic"

echo 🔧 Configuration:
if exist ai-backend\.env (echo ✅ .env file found) else (echo ❌ .env file not found)
```

## 📞 Obtener Ayuda

### 1. Información para Reportes
Cuando reportes un problema, incluye:

```bash
# Información del sistema
uname -a  # Linux/Mac
systeminfo  # Windows

# Versiones
node --version
npm --version
python --version

# Logs relevantes
tail -50 ai-backend/logs/uranus-ai.log

# Configuración (sin API keys)
cat ai-backend/.env | grep -v "API_KEY"
```

### 2. Canales de Soporte
- **GitHub Issues**: [Reportar bugs](https://github.com/alezzanderg/Uranus-AI/issues)
- **Discussions**: [Hacer preguntas](https://github.com/alezzanderg/Uranus-AI/discussions)
- **Wiki**: [Documentación extendida](https://github.com/alezzanderg/Uranus-AI/wiki)

### 3. Plantilla de Issue
```markdown
## 🐛 Descripción del Problema
[Describe el problema claramente]

## 🔄 Pasos para Reproducir
1. [Primer paso]
2. [Segundo paso]
3. [Ver error]

## 💻 Entorno
- OS: [Windows 11 / macOS 13 / Ubuntu 22.04]
- Node.js: [v18.17.0]
- Python: [3.11.4]
- Uranus-AI: [v1.1.0]

## 📋 Logs
```
[Pegar logs relevantes aquí]
```

## ✅ Intentos de Solución
- [x] Revisé la documentación
- [x] Busqué en issues existentes
- [x] Probé reiniciar los servicios
```

---

¡Con esta guía deberías poder resolver la mayoría de problemas en Uranus-AI! 🪐🔧

