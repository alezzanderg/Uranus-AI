# Guía de Instalación - AI-Enhanced Code-OSS

Esta guía te llevará paso a paso a través del proceso de instalación y configuración del AI-Enhanced Code-OSS Editor.

## 📋 Requisitos Previos

### Sistema Operativo
- **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+, Fedora 35+
- **macOS**: 10.15 (Catalina) o superior
- **Windows**: Windows 10/11 (se recomienda WSL2)

### Software Requerido

#### Node.js y npm
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS (con Homebrew)
brew install node@18

# Windows (descargar desde nodejs.org)
# https://nodejs.org/en/download/
```

#### Python 3.11+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11

# Windows
# Descargar desde python.org
```

#### Git
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows
# Descargar Git for Windows
```

### Herramientas de Compilación

#### Linux
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# CentOS/RHEL/Fedora
sudo dnf install gcc gcc-c++ python3-devel
```

#### macOS
```bash
# Instalar Xcode Command Line Tools
xcode-select --install
```

#### Windows
```bash
# En PowerShell como administrador
npm install -g windows-build-tools
```

## 🚀 Instalación Paso a Paso

### 1. Obtener el Código Fuente

#### Opción A: Clonar desde Git
```bash
git clone <repository-url>
cd ai-enhanced-code-oss
```

#### Opción B: Descargar ZIP
1. Descargar el archivo ZIP del repositorio
2. Extraer en el directorio deseado
3. Abrir terminal en el directorio extraído

### 2. Configurar el Backend IA

#### Crear Entorno Virtual
```bash
cd ai-backend

# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### Instalar Dependencias
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

#### Configurar Variables de Entorno
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración
nano .env  # o tu editor preferido
```

**Configuración mínima requerida:**
```env
# OpenAI Configuration
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2048

# Server Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "vscode-file://vscode-app"]
```

#### Verificar Instalación del Backend
```bash
# Ejecutar tests
python -m pytest tests/ -v

# Iniciar servidor de prueba
python -m app.main
```

El backend debería estar disponible en `http://localhost:8000`

### 3. Configurar Code-OSS

#### Instalar Dependencias
```bash
cd ../vscode

# Instalar dependencias de Node.js
npm install

# Si hay errores, limpiar cache
npm cache clean --force
npm install
```

#### Compilar el Proyecto
```bash
# Compilación completa
npm run compile

# Para desarrollo (con watch)
npm run watch
```

#### Verificar Integración del AI Assistant
```bash
# Verificar que el módulo existe
ls -la src/vs/workbench/contrib/aiAssistant/

# Verificar importación en main
grep -n "aiAssistant" src/vs/workbench/workbench.common.main.ts
```

### 4. Configuración Inicial

#### Configurar OpenAI API Key
1. Obtener API key de [OpenAI Platform](https://platform.openai.com/api-keys)
2. Agregar al archivo `.env` del backend
3. Verificar que tienes créditos disponibles

#### Configurar Firewall (si es necesario)
```bash
# Linux (ufw)
sudo ufw allow 8000

# macOS
# Permitir conexiones en Preferencias del Sistema > Seguridad

# Windows
# Configurar Windows Defender Firewall
```

## 🧪 Verificación de la Instalación

### 1. Test Automático
```bash
# Desde el directorio raíz
python test-backend.py
```

### 2. Test Manual

#### Iniciar Servicios
```bash
# Terminal 1: Backend
cd ai-backend
source venv/bin/activate
python -m app.main

# Terminal 2: Code-OSS
cd vscode
npm start
```

#### Verificar Funcionalidad
1. **Backend**: Visitar `http://localhost:8000/docs`
2. **Code-OSS**: Buscar ícono 🤖 en barra lateral derecha
3. **AI Assistant**: Abrir panel y enviar mensaje de prueba

### 3. Script de Inicio Automático
```bash
# Hacer ejecutable
chmod +x start-ai-editor.sh

# Ejecutar
./start-ai-editor.sh
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### Error: "Module not found"
```bash
# Limpiar node_modules
cd vscode
rm -rf node_modules package-lock.json
npm install
```

#### Error: "Python version not supported"
```bash
# Verificar versión de Python
python3 --version

# Crear entorno con versión específica
python3.11 -m venv venv
```

#### Error: "OpenAI API key invalid"
1. Verificar que la API key es correcta
2. Comprobar que tienes créditos disponibles
3. Verificar que la key tiene permisos necesarios

#### Error: "Port 8000 already in use"
```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Terminar proceso
kill -9 <PID>

# O cambiar puerto en .env
PORT=8001
```

#### Error de Compilación en Code-OSS
```bash
# Verificar versión de Node.js
node --version  # Debe ser 18.x+

# Limpiar cache de TypeScript
cd vscode
npx tsc --build --clean
npm run compile
```

### Logs de Debugging

#### Backend
```bash
# Ver logs en tiempo real
cd ai-backend
tail -f logs/app.log
```

#### Code-OSS
1. Abrir DevTools (F12)
2. Ver Console para errores JavaScript
3. Network tab para problemas de conexión

### Configuración Avanzada

#### Usar Modelos Locales
```env
# En .env
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama2
```

#### Configurar Proxy
```env
# En .env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

#### Configurar SSL/TLS
```bash
# Generar certificados
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configurar en .env
SSL_CERT_PATH=cert.pem
SSL_KEY_PATH=key.pem
```

## 📦 Instalación con Docker

### Usar Docker Compose
```bash
cd ai-backend

# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Dockerfile Personalizado
```dockerfile
# Ejemplo para desarrollo
FROM node:18-alpine AS frontend
WORKDIR /app
COPY vscode/package*.json ./
RUN npm install
COPY vscode/ ./
RUN npm run compile

FROM python:3.11-slim AS backend
WORKDIR /app
COPY ai-backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY ai-backend/ ./
EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

## 🔄 Actualización

### Actualizar Backend
```bash
cd ai-backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Actualizar Frontend
```bash
cd vscode
npm update
npm run compile
```

### Actualizar Código Fuente
```bash
git pull origin main
./build-vscode.sh
```

## 🚀 Despliegue en Producción

### Configuración de Producción
```env
DEBUG=false
LOG_LEVEL=INFO
WORKERS=4
```

### Usar Nginx como Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Systemd Service
```ini
[Unit]
Description=AI Assistant Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ai-backend
Environment=PATH=/path/to/ai-backend/venv/bin
ExecStart=/path/to/ai-backend/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. **Revisar logs**: Verificar mensajes de error en consola
2. **Documentación**: Consultar DEVELOPMENT.md para detalles técnicos
3. **Issues**: Reportar problemas en el repositorio
4. **Community**: Buscar ayuda en foros de desarrollo

---

¡Felicidades! Ahora tienes un editor de código con IA nativa funcionando. Disfruta programando con tu asistente inteligente. 🚀

