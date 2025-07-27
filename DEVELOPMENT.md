# Guía de Desarrollo - AI-Enhanced Code-OSS

Esta guía proporciona información detallada para desarrolladores que deseen entender, modificar o extender el AI-Enhanced Code-OSS Editor.

## 🏗️ Arquitectura Técnica

### Principios de Diseño

El AI Assistant está diseñado con los siguientes principios:

1. **Integración Nativa**: No es una extensión, sino parte integral del código fuente
2. **Modularidad**: Código organizado en módulos independientes y reutilizables
3. **Escalabilidad**: Arquitectura que permite agregar nuevas funcionalidades fácilmente
4. **Performance**: Comunicación asíncrona y manejo eficiente de recursos
5. **Compatibilidad**: Mantiene compatibilidad con el ecosistema de VSCode

### Estructura del Frontend

#### Módulo AI Assistant
```
src/vs/workbench/contrib/aiAssistant/
├── common/
│   ├── aiConstants.ts          # Constantes y configuración
│   ├── aiTypes.ts              # Interfaces TypeScript
│   └── aiAssistantService.ts   # Definición de servicios
├── browser/
│   ├── services/
│   │   ├── aiCommunicationService.ts    # WebSocket/HTTP
│   │   ├── aiContextService.ts          # Contexto del editor
│   │   └── aiAssistantServiceImpl.ts    # Implementación principal
│   ├── views/
│   │   ├── aiAssistantView.ts           # Vista principal
│   │   ├── aiChatWidget.ts              # Widget de chat
│   │   └── aiStatusWidget.ts            # Widget de estado
│   ├── actions/
│   │   └── aiAssistantActions.ts        # Acciones y comandos
│   └── media/
│       └── aiAssistant.css              # Estilos
└── aiAssistant.contribution.ts          # Registro de contribuciones
```

#### Servicios Principales

**AiCommunicationService**
- Maneja conexiones WebSocket
- Implementa reconexión automática
- Gestiona cola de mensajes
- Proporciona API para envío/recepción

**AiContextService**
- Captura contexto del workspace
- Obtiene información del editor activo
- Proporciona contexto de archivos abiertos
- Maneja selecciones de texto

**AiAssistantServiceImpl**
- Orquesta comunicación entre servicios
- Implementa lógica de negocio
- Maneja historial de conversaciones
- Proporciona API unificada

#### Widgets de UI

**AiAssistantView**
- Vista principal con tabs
- Maneja navegación entre secciones
- Integra widgets individuales
- Gestiona estado de visibilidad

**AiChatWidget**
- Interfaz de chat
- Renderizado de markdown
- Indicador de escritura
- Historial de mensajes

**AiStatusWidget**
- Indicador de conexión
- Manejo de errores
- Estados de reconexión

### Estructura del Backend

#### Aplicación FastAPI
```
ai-backend/
├── app/
│   ├── main.py                 # Aplicación principal
│   ├── config.py               # Configuración
│   ├── models/
│   │   ├── chat_models.py      # Modelos de chat
│   │   └── code_models.py      # Modelos de código
│   ├── services/
│   │   ├── chat_service.py     # Servicio de chat
│   │   ├── code_analysis_service.py  # Análisis de código
│   │   └── completion_service.py     # Autocompletado
│   └── api/
│       ├── chat_routes.py      # Endpoints de chat
│       ├── code_routes.py      # Endpoints de código
│       └── websocket_routes.py # WebSocket
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

#### Servicios del Backend

**ChatService**
- Procesamiento de mensajes
- Integración con OpenAI
- Manejo de contexto
- Streaming de respuestas

**CodeAnalysisService**
- Análisis estático de código
- Detección de patrones
- Sugerencias de mejora
- Métricas de complejidad

**CompletionService**
- Autocompletado inteligente
- Análisis de contexto
- Ranking de sugerencias
- Soporte multi-lenguaje

## 🔧 Configuración de Desarrollo

### Entorno de Desarrollo

#### Requisitos
- Node.js 18+ con npm/yarn
- Python 3.11+ con pip
- Git para control de versiones
- Editor de código (recomendado: VSCode)

#### Configuración Inicial
```bash
# Clonar repositorio
git clone <repo-url>
cd ai-enhanced-code-oss

# Configurar backend
cd ai-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependencias de desarrollo

# Configurar frontend
cd ../vscode
npm install
npm run compile

# Variables de entorno
cp ai-backend/.env.example ai-backend/.env
# Editar .env con configuración local
```

#### Desarrollo con Hot Reload

**Backend**
```bash
cd ai-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd vscode
npm run watch  # Compilación automática
# En otra terminal:
npm start      # Ejecutar Code-OSS
```

### Debugging

#### Frontend (Code-OSS)
- Usar F12 para abrir DevTools
- Puntos de interrupción en TypeScript
- Console.log para debugging rápido
- VSCode debugger para debugging avanzado

#### Backend (FastAPI)
```python
# Agregar en el código
import pdb; pdb.set_trace()

# O usar logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Testing

### Testing del Frontend

#### Unit Tests
```bash
cd vscode
npm test
```

#### Integration Tests
```bash
# Ejecutar Code-OSS en modo test
npm run test:integration
```

### Testing del Backend

#### Unit Tests
```bash
cd ai-backend
pytest tests/unit/
```

#### Integration Tests
```bash
pytest tests/integration/
```

#### End-to-End Tests
```bash
python test-backend.py
```

### Testing Manual

#### Checklist de Funcionalidades
- [ ] AI Assistant aparece en Secondary Sidebar
- [ ] Conexión WebSocket funciona
- [ ] Chat responde correctamente
- [ ] Acciones de código funcionan
- [ ] Configuración se guarda
- [ ] Reconexión automática funciona
- [ ] Temas claro/oscuro se aplican

## 🚀 Deployment

### Desarrollo Local
```bash
./start-ai-editor.sh
```

### Producción con Docker
```bash
cd ai-backend
docker-compose up -d
```

### Build para Distribución
```bash
cd vscode
npm run compile-build
npm run package  # Crear paquetes instalables
```

## 🔄 Flujo de Contribución

### 1. Preparación
```bash
git checkout -b feature/nueva-funcionalidad
```

### 2. Desarrollo
- Implementar cambios
- Agregar tests
- Actualizar documentación

### 3. Testing
```bash
# Backend
cd ai-backend && pytest
# Frontend
cd vscode && npm test
# Integration
python test-backend.py
```

### 4. Commit y Push
```bash
git add .
git commit -m "feat: agregar nueva funcionalidad"
git push origin feature/nueva-funcionalidad
```

### 5. Pull Request
- Crear PR con descripción detallada
- Incluir screenshots si hay cambios de UI
- Asegurar que todos los tests pasen

## 📝 Convenciones de Código

### TypeScript (Frontend)
```typescript
// Usar interfaces para tipos
interface IAiMessage {
    id: string;
    content: string;
    timestamp: number;
}

// Usar async/await
async function sendMessage(message: string): Promise<IAiResponse> {
    return await this.communicationService.sendMessage(message);
}

// Usar eventos para comunicación
private readonly _onDidReceiveMessage = new Emitter<IAiMessage>();
readonly onDidReceiveMessage = this._onDidReceiveMessage.event;
```

### Python (Backend)
```python
# Usar type hints
from typing import List, Optional

async def process_message(message: str) -> Optional[str]:
    """Process AI message and return response."""
    pass

# Usar Pydantic para validación
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None
```

### CSS
```css
/* Usar variables CSS de VSCode */
.ai-assistant-view {
    background: var(--vscode-editor-background);
    color: var(--vscode-foreground);
}

/* Seguir convenciones de naming */
.ai-chat-message-user {
    /* Estilos específicos */
}
```

## 🐛 Debugging Común

### Problemas de Conexión
```typescript
// Verificar estado de conexión
if (!this.communicationService.isConnected()) {
    console.log('WebSocket not connected');
    await this.communicationService.connect();
}
```

### Problemas de Contexto
```typescript
// Debug contexto del editor
const context = await this.contextService.getCurrentContext();
console.log('Current context:', context);
```

### Problemas de UI
```css
/* Debug layout issues */
.debug-border {
    border: 1px solid red !important;
}
```

## 📚 Recursos Adicionales

### Documentación de VSCode
- [VSCode Extension API](https://code.visualstudio.com/api)
- [Workbench API](https://code.visualstudio.com/api/extension-capabilities/extending-workbench)
- [Theming](https://code.visualstudio.com/api/extension-capabilities/theming)

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Support](https://fastapi.tiangolo.com/advanced/websockets/)
- [Async Programming](https://fastapi.tiangolo.com/async/)

### OpenAI
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

## 🔮 Roadmap de Desarrollo

### Próximas Funcionalidades
- [ ] Soporte para más modelos de IA
- [ ] Plugins de terceros
- [ ] Análisis de código más avanzado
- [ ] Integración con Git
- [ ] Colaboración en tiempo real
- [ ] Métricas y analytics

### Mejoras Técnicas
- [ ] Optimización de performance
- [ ] Mejor manejo de errores
- [ ] Tests más completos
- [ ] Documentación interactiva
- [ ] CI/CD pipeline

---

Esta guía está en constante evolución. Para contribuir con mejoras o reportar problemas, por favor crea un issue en el repositorio.

