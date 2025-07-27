# 🪐 Uranus-AI Editor

Un editor de código moderno basado en Code-OSS con capacidades nativas de inteligencia artificial integradas directamente en el código fuente, **ahora con soporte para múltiples modelos de IA**.

![Uranus-AI Logo](https://img.shields.io/badge/Uranus--AI-Editor-blue?style=for-the-badge&logo=visual-studio-code)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=for-the-badge&logo=fastapi)
![Version](https://img.shields.io/badge/Version-1.1.0-orange?style=for-the-badge)

## 🚀 Características Principales

### 🤖 Multi-Model AI Support (NUEVO v1.1.0)
- **15+ Modelos Soportados**: OpenAI, Claude, Gemini, Grok, DeepSeek, Mistral, Cohere, Ollama
- **Selección Inteligente**: El sistema recomienda el mejor modelo para cada tarea
- **Fallback Automático**: Si un modelo falla, automáticamente usa alternativas
- **Comparación en Tiempo Real**: Compara respuestas de múltiples modelos
- **Optimización de Costos**: Elige automáticamente modelos cost-effective
- **Modelos Locales**: Soporte completo para Ollama (Llama 2, Code Llama)

### 🧠 AI Assistant Nativo
- **Integración Directa**: El AI Assistant está integrado directamente en el código fuente de Code-OSS
- **Secondary Sidebar**: Aparece como un panel persistente en la barra lateral derecha
- **Chat Inteligente**: Conversación contextual con múltiples modelos de IA
- **Análisis de Código**: Análisis estático y sugerencias inteligentes powered by AI

### 💬 Funcionalidades de Chat
- Chat en tiempo real con contexto del workspace
- Soporte para markdown en las respuestas
- Historial de conversaciones persistente
- Streaming de respuestas para experiencia fluida

### 🔧 Herramientas de Código
- **Explicar Código**: Explica qué hace el código seleccionado
- **Refactorizar**: Sugerencias de refactoring inteligentes
- **Encontrar Bugs**: Detección de errores potenciales
- **Generar Tests**: Generación automática de pruebas unitarias
- **Autocompletado**: Sugerencias de código contextual

### 🌐 Backend IA
- API REST y WebSocket para comunicación en tiempo real
- Soporte para múltiples modelos de IA (OpenAI, etc.)
- Análisis contextual del workspace y archivos abiertos
- Reconexión automática y manejo de errores

## 📋 Requisitos del Sistema

### Software Requerido
- **Node.js** 18.x o superior
- **Python** 3.11 o superior
- **Git** para clonar repositorios
- **OpenAI API Key** (o compatible)

### Sistemas Operativos Soportados
- Linux (Ubuntu 22.04+, otras distribuciones)
- macOS 10.15+
- Windows 10/11 (con WSL recomendado)

## 🛠️ Instalación Rápida

### 1. Clonar el Proyecto
```bash
git clone https://github.com/alezzanderg/Uranus-AI.git
cd Uranus-AI
```

### 2. Configurar Backend IA
```bash
cd ai-backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

### 3. Configurar Code-OSS
```bash
cd ../vscode

# Instalar dependencias
npm install

# Compilar el proyecto
npm run compile
```

### 4. Inicio Automático
```bash
# Desde el directorio raíz del proyecto
./start-ai-editor.sh
```

Este script iniciará automáticamente:
- El backend IA en `http://localhost:8000`
- Code-OSS con AI Assistant integrado

## 🎯 Uso del AI Assistant

### Acceder al AI Assistant
1. Abre Uranus-AI Editor
2. Busca el ícono del robot 🤖 en la barra lateral derecha (Secondary Sidebar)
3. Haz clic para abrir el panel del AI Assistant

### Chat con IA
- Escribe tu pregunta en el área de texto
- Presiona Enter o haz clic en "Send"
- La IA responderá con contexto de tu workspace actual

### Acciones de Código
1. Selecciona código en el editor
2. Haz clic derecho para abrir el menú contextual
3. Elige una acción del AI Assistant:
   - **Explain Code**: Explica el código seleccionado
   - **Refactor Code**: Sugiere mejoras
   - **Find Bugs**: Busca errores potenciales
   - **Generate Tests**: Genera pruebas unitarias

## 🏗️ Arquitectura del Sistema

### Frontend (Code-OSS)
```
src/vs/workbench/contrib/aiAssistant/
├── browser/
│   ├── actions/           # Acciones y comandos
│   ├── services/          # Servicios de comunicación
│   ├── views/             # Componentes de UI
│   └── media/             # Estilos CSS
├── common/                # Tipos y constantes
└── aiAssistant.contribution.ts
```

### Backend (FastAPI)
```
ai-backend/
├── app/
│   ├── api/               # Endpoints REST y WebSocket
│   ├── models/            # Modelos de datos
│   ├── services/          # Lógica de negocio
│   └── main.py            # Aplicación principal
├── requirements.txt
└── docker-compose.yml
```

## 🧪 Testing

### Probar Backend
```bash
# Instalar dependencias de testing
pip install websockets requests

# Ejecutar tests
python test-backend.py
```

### Probar Integración
```bash
# Compilar y probar Code-OSS
cd vscode
./build-vscode.sh
```

## 🐛 Solución de Problemas

### Backend no se conecta
- Verificar que el puerto 8000 esté libre
- Comprobar la configuración de OPENAI_API_KEY
- Revisar logs en la consola del backend

### AI Assistant no aparece
- Verificar que la compilación fue exitosa
- Comprobar que el módulo está importado en `workbench.common.main.ts`
- Revisar la consola de desarrollo de Code-OSS (F12)

### Errores de WebSocket
- Verificar que el backend esté ejecutándose
- Comprobar la URL de conexión en configuración
- Revisar firewall y configuración de red

## 📚 Documentación Adicional

- [Guía de Instalación Detallada](INSTALLATION.md)
- [Guía de Desarrollo](DEVELOPMENT.md)
- [Arquitectura del Sistema](ai-assistant-architecture.md)
- [Resumen del Proyecto](PROJECT_SUMMARY.md)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🆚 Comparación con Cursor

| Característica | Uranus-AI | Cursor |
|---|---|---|
| **Open Source** | ✅ Completamente abierto | ❌ Propietario |
| **Integración** | ✅ Nativa en el core | ❌ Basado en extensiones |
| **Backend Propio** | ✅ Control total | ❌ Backend cerrado |
| **Customizable** | ✅ Código modificable | ❌ Limitado |
| **Multi-Modelo** | ✅ Soporte extensible | ✅ Limitado |
| **Costo** | ✅ Gratis (solo API) | ❌ Suscripción |

## 🔮 Roadmap

### v1.1 (Próximamente)
- [ ] Soporte para más modelos de IA (Llama, Claude)
- [ ] Plugins de terceros
- [ ] Análisis de código más avanzado
- [ ] Integración con Git

### v1.2 (Futuro)
- [ ] Colaboración en tiempo real
- [ ] Métricas y analytics
- [ ] Integración con CI/CD
- [ ] Soporte para bases de datos

## 📄 Licencia

Este proyecto está basado en Code-OSS (MIT License) con modificaciones adicionales para integración de IA.

```
MIT License

Copyright (c) 2024 Uranus-AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Agradecimientos

- **Microsoft**: Por Code-OSS y VS Code
- **OpenAI**: Por los modelos de IA
- **FastAPI**: Por el framework del backend
- **Comunidad Open Source**: Por las herramientas y librerías utilizadas

## 📞 Soporte

Si encuentras problemas o tienes preguntas:

- 🐛 [Reportar Bug](https://github.com/alezzanderg/Uranus-AI/issues/new?template=bug_report.md)
- 💡 [Solicitar Feature](https://github.com/alezzanderg/Uranus-AI/issues/new?template=feature_request.md)
- 💬 [Discusiones](https://github.com/alezzanderg/Uranus-AI/discussions)

---

<div align="center">

**🪐 Desarrollado con ❤️ por la comunidad Uranus-AI**

[⭐ Dale una estrella si te gusta el proyecto](https://github.com/alezzanderg/Uranus-AI)

</div>

