# 🏗️ Executable Build Guide - Uranus-AI

Guía completa para compilar Uranus-AI como un ejecutable (.exe) para Windows.

## 🎯 Resumen

Este sistema permite crear:
- **🔧 Backend ejecutable** - Un solo archivo .exe que contiene todo el backend Python
- **📱 Aplicación de escritorio** - Aplicación Electron con interfaz nativa
- **📦 Instalador completo** - Instalador NSIS con configuración automática
- **🎒 Versión portable** - Ejecutable que no requiere instalación

## 📋 Prerrequisitos

### Software Requerido
- **Python 3.11+** con pip
- **Node.js 18+** con npm
- **Git** para control de versiones
- **Visual Studio Build Tools** (opcional, para compilaciones optimizadas)

### Dependencias de Compilación
```powershell
# Instalar PyInstaller para compilar Python
pip install pyinstaller

# Instalar dependencias de Electron
cd electron-app
npm install
```

## 🚀 Proceso de Compilación

### Opción 1: Compilación Automática (Recomendado)

```powershell
# Ejecutar script de compilación completa
.\build-executable.bat
```

Este script hace todo automáticamente:
1. ✅ Verifica la estructura del proyecto
2. 🐍 Instala dependencias de Python
3. 🔨 Compila el backend con PyInstaller
4. 📝 Construye VSCode
5. ⚡ Prepara la aplicación Electron
6. 📦 Crea el instalador final
7. 🎒 Genera versión portable

### Opción 2: Compilación Manual

#### Paso 1: Compilar Backend
```powershell
cd ai-backend

# Activar entorno virtual
venv\Scripts\activate

# Instalar PyInstaller
pip install pyinstaller

# Compilar backend
cd ..
pyinstaller --clean --noconfirm build-tools\pyinstaller.spec
```

#### Paso 2: Compilar VSCode
```powershell
cd vscode

# Instalar dependencias
npm install

# Compilar
npm run compile-build
```

#### Paso 3: Crear Aplicación Electron
```powershell
cd electron-app

# Instalar dependencias
npm install

# Copiar archivos compilados
mkdir resources\backend
copy ..\dist\uranus-ai-backend.exe resources\backend\

mkdir resources\vscode
xcopy ..\vscode\out resources\vscode\ /E /I /Y

# Compilar aplicación Electron
npm run build-win
```

## 📁 Estructura de Archivos de Compilación

```
Uranus-AI/
├── build-tools/
│   ├── pyinstaller.spec          # Configuración PyInstaller
│   ├── version_info.txt          # Información de versión Windows
│   └── installer.nsh             # Script instalador NSIS
├── electron-app/
│   ├── package.json              # Configuración Electron
│   ├── src/
│   │   ├── main.js               # Proceso principal Electron
│   │   └── preload.js            # Script de preload
│   └── build/                    # Recursos de construcción
├── dist/
│   ├── uranus-ai-backend.exe     # Backend compilado
│   ├── final/                    # Ejecutables finales
│   └── portable/                 # Versión portable
└── build-executable.bat          # Script de compilación
```

## 🔧 Configuración de PyInstaller

### Archivo `pyinstaller.spec`

```python
# Configuraciones importantes:
- hiddenimports: Módulos que PyInstaller podría no detectar
- datas: Archivos de datos a incluir
- binaries: Bibliotecas nativas requeridas
- excludes: Módulos a excluir para reducir tamaño
```

### Optimizaciones Incluidas

- **UPX Compression**: Reduce el tamaño del ejecutable
- **Hidden Imports**: Incluye todas las dependencias necesarias
- **Data Files**: Empaqueta configuraciones y recursos
- **Icon & Version**: Información de versión y branding

## ⚡ Configuración de Electron

### Características de la Aplicación

- **Auto-updater**: Actualizaciones automáticas
- **Native Menus**: Menús nativos del sistema operativo
- **Backend Integration**: Gestión automática del backend
- **Multi-platform**: Soporte para Windows, Mac, Linux

### Configuración del Instalador

```json
"build": {
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true,
    "createStartMenuShortcut": true
  }
}
```

## 🗄️ Integración con PostgreSQL

### Configuración de Base de Datos

El ejecutable incluye:
- **Conexión automática** a Neon PostgreSQL
- **Migración automática** de configuraciones .env
- **Encriptación** de API keys sensibles
- **Fallback** a variables de entorno si la DB no está disponible

### Variables de Entorno en Ejecutable

```env
# La conexión a PostgreSQL está embebida
DATABASE_URL=postgresql://neondb_owner:npg_btfS8wXgFjl7@ep-rapid-sea-adxzz6h8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Las API keys se almacenan encriptadas en la base de datos
# No es necesario configurar .env en el ejecutable
```

## 📦 Tipos de Distribución

### 1. Instalador NSIS (.exe)
- **Descripción**: Instalador completo con wizard
- **Características**: 
  - Asociaciones de archivos
  - Accesos directos en escritorio y menú inicio
  - Desinstalador incluido
  - Configuración inicial de proveedores AI

### 2. Versión Portable (.exe)
- **Descripción**: Ejecutable único sin instalación
- **Características**:
  - No requiere permisos de administrador
  - Configuración portátil
  - Ideal para USB o uso temporal

### 3. Microsoft Store Package (.appx)
- **Descripción**: Paquete para Microsoft Store
- **Características**:
  - Instalación desde la tienda
  - Actualizaciones automáticas
  - Sandboxing de seguridad

## 🔍 Solución de Problemas

### Error: "Module not found"
```powershell
# Solución: Agregar módulo a hiddenimports en pyinstaller.spec
hiddenimports = [
    'tu_modulo_faltante',
    # ... otros módulos
]
```

### Error: "Backend not starting"
```powershell
# Verificar que el ejecutable del backend existe
dir dist\uranus-ai-backend.exe

# Verificar logs de Electron
# Los logs aparecen en la consola durante desarrollo
```

### Error: "Database connection failed"
```powershell
# Verificar conexión a internet
ping ep-rapid-sea-adxzz6h8-pooler.c-2.us-east-1.aws.neon.tech

# El sistema automáticamente hace fallback a .env si la DB no está disponible
```

### Ejecutable muy grande
```powershell
# Optimizaciones en pyinstaller.spec:
- Agregar más módulos a 'excludes'
- Habilitar UPX compression
- Usar --onefile para un solo archivo
```

## 🎯 Distribución

### Subir a GitHub Releases

```powershell
# Crear release con los ejecutables
gh release create v1.2.0 \
  dist\final\Uranus-AI-Editor-Setup-1.2.0.exe \
  dist\portable\Uranus-AI-Editor-Portable-1.2.0.exe \
  --title "Uranus-AI v1.2.0 - PostgreSQL Integration" \
  --notes "Complete executable with database integration"
```

### Firma Digital (Opcional)

```powershell
# Firmar ejecutables para evitar warnings de Windows
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com dist\final\*.exe
```

## 📊 Métricas de Compilación

### Tamaños Típicos
- **Backend ejecutable**: ~150-200 MB
- **Aplicación Electron**: ~200-300 MB
- **Instalador completo**: ~300-400 MB
- **Versión portable**: ~400-500 MB

### Tiempo de Compilación
- **Backend (PyInstaller)**: 2-5 minutos
- **VSCode**: 3-8 minutos
- **Electron**: 1-3 minutos
- **Total**: 6-16 minutos

## 🚀 Automatización CI/CD

### GitHub Actions (Futuro)

```yaml
name: Build Executables
on: [push, release]
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Build executable
        run: .\build-executable.bat
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: uranus-ai-windows
          path: dist/final/
```

## 💡 Tips y Mejores Prácticas

### 1. Optimización de Tamaño
- Excluir dependencias innecesarias
- Usar UPX compression
- Optimizar imports en Python

### 2. Rendimiento
- Compilar en modo release
- Usar --optimize en PyInstaller
- Minimizar imports dinámicos

### 3. Seguridad
- Firmar ejecutables
- Validar integridad de archivos
- Usar HTTPS para actualizaciones

### 4. Testing
- Probar en máquinas limpias
- Verificar en diferentes versiones de Windows
- Testear instalación y desinstalación

---

¡Con esta guía puedes crear ejecutables profesionales de Uranus-AI listos para distribución! 🎉

