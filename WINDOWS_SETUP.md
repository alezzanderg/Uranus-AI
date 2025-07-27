# 🪟 Uranus-AI Setup Guide for Windows

Esta guía te ayudará a configurar y ejecutar Uranus-AI en Windows paso a paso.

## 📋 Prerrequisitos

### 1. Software Requerido
- **Node.js 18+**: [Descargar aquí](https://nodejs.org/)
- **Python 3.11+**: [Descargar aquí](https://www.python.org/downloads/)
- **Git**: [Descargar aquí](https://git-scm.com/download/win)
- **Visual Studio Build Tools** (opcional): Para compilaciones nativas

### 2. Verificar Instalaciones
Abre PowerShell o Command Prompt y verifica:

```powershell
node --version    # Debe mostrar v18.x.x o superior
npm --version     # Debe mostrar 9.x.x o superior
python --version  # Debe mostrar 3.11.x o superior
git --version     # Debe mostrar 2.x.x o superior
```

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```powershell
git clone https://github.com/alezzanderg/Uranus-AI.git
cd Uranus-AI
```

### 2. Configurar Backend de IA
```powershell
cd ai-backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
```

### 3. Editar Configuración
Abre `.env` en tu editor favorito y agrega tus API keys:

```env
# Mínimo requerido (elige uno)
OPENAI_API_KEY=tu_clave_openai_aqui

# Opcional: Múltiples proveedores
ANTHROPIC_API_KEY=tu_clave_claude_aqui
GOOGLE_API_KEY=tu_clave_gemini_aqui
XAI_API_KEY=tu_clave_grok_aqui
DEEPSEEK_API_KEY=tu_clave_deepseek_aqui
```

### 4. Configurar Frontend
```powershell
cd ..\vscode

# Instalar dependencias
npm install

# Resolver vulnerabilidades (opcional)
npm audit fix
```

## 🎯 Ejecución

### Opción 1: Script Automático (Recomendado)
```powershell
# Desde el directorio raíz de Uranus-AI
.\start-ai-editor.bat
```

### Opción 2: Manual

#### Paso 1: Iniciar Backend
```powershell
cd ai-backend
venv\Scripts\activate
python -m app.main
```

#### Paso 2: Compilar VSCode (nueva terminal)
```powershell
cd vscode
npm run watch
```

## 🔧 Scripts Disponibles

### Para Windows (.bat)
- **`start-ai-editor.bat`**: Inicia todo automáticamente
- **`build-vscode.bat`**: Compila VSCode con opciones

### Scripts de NPM en VSCode
```powershell
cd vscode

# Ver todos los scripts disponibles
npm run

# Scripts comunes
npm run watch          # Desarrollo con auto-reload
npm run compile-build  # Compilación de producción
npm run compile-web    # Versión web
npm run test          # Ejecutar tests
```

## 🐛 Solución de Problemas

### Error: "npm run compile" no existe
**Problema**: El script `compile` no está definido en package.json
**Solución**: Usa uno de estos scripts alternativos:
```powershell
npm run watch          # Para desarrollo
npm run compile-build  # Para producción
```

### Error: Scripts .sh no funcionan
**Problema**: PowerShell no ejecuta scripts de shell
**Solución**: Usa los scripts .bat equivalentes:
```powershell
.\start-ai-editor.bat    # En lugar de ./start-ai-editor.sh
.\build-vscode.bat       # En lugar de ./build-vscode.sh
```

### Error: "python no se reconoce"
**Problema**: Python no está en el PATH
**Solución**: 
1. Reinstala Python marcando "Add to PATH"
2. O usa `py` en lugar de `python`:
```powershell
py -m venv venv
```

### Error: Vulnerabilidades de npm
**Problema**: Dependencias con vulnerabilidades conocidas
**Solución**:
```powershell
# Arreglar automáticamente
npm audit fix

# Arreglar forzadamente (puede romper compatibilidad)
npm audit fix --force

# Ver detalles
npm audit
```

### Error: "Cannot find module"
**Problema**: Dependencias no instaladas correctamente
**Solución**:
```powershell
# Limpiar cache y reinstalar
npm cache clean --force
rm -rf node_modules
npm install
```

### Error: Puerto en uso
**Problema**: Puerto 8000 ya está ocupado
**Solución**: Cambiar puerto en `.env`:
```env
PORT=8001
```

### Error: API Key inválida
**Problema**: Clave de API incorrecta o no configurada
**Solución**: Verificar en `.env`:
```env
OPENAI_API_KEY=sk-...  # Debe empezar con sk-
```

## 🎮 Uso del Editor

### 1. Acceder al AI Assistant
1. Compila y ejecuta VSCode
2. Busca el ícono 🤖 en la barra lateral derecha
3. Haz clic para abrir el panel del AI Assistant

### 2. Seleccionar Modelo
1. En el panel del AI Assistant, verás un selector de modelo
2. Elige entre los modelos disponibles según tus API keys
3. El sistema recomendará el mejor modelo para cada tarea

### 3. Funcionalidades Disponibles
- **Chat**: Conversación contextual sobre tu código
- **Análisis**: Análisis automático de archivos abiertos
- **Refactoring**: Sugerencias de mejora de código
- **Debugging**: Ayuda para encontrar y corregir errores
- **Documentación**: Generación automática de documentación

## 🔗 URLs Importantes

Una vez ejecutándose:
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Modelos Disponibles**: http://localhost:8000/api/v1/models/available

## 💡 Tips para Windows

### 1. Usar PowerShell como Administrador
Para evitar problemas de permisos:
```powershell
# Ejecutar PowerShell como administrador
Start-Process powershell -Verb runAs
```

### 2. Configurar Política de Ejecución
Si tienes problemas ejecutando scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Usar Windows Terminal
Para mejor experiencia, instala Windows Terminal desde Microsoft Store.

### 4. Variables de Entorno Globales
Para configurar variables de entorno globalmente:
1. Busca "Variables de entorno" en el menú inicio
2. Agrega las variables en "Variables del sistema"
3. Reinicia PowerShell

## 🆘 Obtener Ayuda

### 1. Logs del Backend
```powershell
cd ai-backend
tail -f logs/uranus-ai.log  # En Git Bash
# O abre el archivo en un editor
```

### 2. Logs de VSCode
Los logs aparecen en la consola donde ejecutaste `npm run watch`

### 3. Verificar Estado
```powershell
# Verificar que el backend esté ejecutándose
curl http://localhost:8000/health

# O en PowerShell
Invoke-RestMethod http://localhost:8000/health
```

### 4. Comunidad
- **GitHub Issues**: [Reportar problemas](https://github.com/alezzanderg/Uranus-AI/issues)
- **Discussions**: [Hacer preguntas](https://github.com/alezzanderg/Uranus-AI/discussions)

---

¡Con esta guía deberías poder ejecutar Uranus-AI perfectamente en Windows! 🪐🚀

