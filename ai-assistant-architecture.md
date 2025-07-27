# Arquitectura del Componente AI Assistant Nativo para Code-OSS

**Autor:** Manus AI  
**Fecha:** 27 de Julio, 2025  
**Versión:** 1.0

## Resumen Ejecutivo

Este documento presenta el diseño arquitectónico completo para la integración nativa de un componente de inteligencia artificial en el editor Code-OSS, evitando el sistema de extensiones y modificando directamente el código fuente del workbench. La solución propuesta implementa un AI Assistant integrado en el Secondary Sidebar con comunicación directa a un backend de IA basado en Flask/FastAPI.

## Tabla de Contenidos

1. [Análisis del Código Base Existente](#análisis-del-código-base-existente)
2. [Arquitectura Propuesta](#arquitectura-propuesta)
3. [Estructura de Archivos y Módulos](#estructura-de-archivos-y-módulos)
4. [Integración con el Secondary Sidebar](#integración-con-el-secondary-sidebar)
5. [Backend de Inteligencia Artificial](#backend-de-inteligencia-artificial)
6. [Comunicación Frontend-Backend](#comunicación-frontend-backend)
7. [Servicios y APIs](#servicios-y-apis)
8. [Consideraciones de Implementación](#consideraciones-de-implementación)




## Análisis del Código Base Existente

### Estructura del Workbench de VSCode

El análisis del repositorio de microsoft/vscode revela una arquitectura modular bien definida que facilita la integración de nuevos componentes. El workbench de VSCode está organizado siguiendo principios de separación de responsabilidades y modularidad, con una clara distinción entre el núcleo del editor y las contribuciones específicas.

La estructura principal del workbench se encuentra en `src/vs/workbench/` y está dividida en las siguientes capas fundamentales:

**Capa Core del Workbench** (`vs/workbench/{common|browser|electron-browser}`): Esta capa contiene la funcionalidad mínima esencial del workbench, incluyendo la gestión de ventanas, el sistema de layout y los servicios básicos. Es importante destacar que esta capa mantiene un conjunto mínimo de dependencias para garantizar la estabilidad y el rendimiento del editor.

**Capa de Servicios** (`vs/workbench/services`): Proporciona servicios centralizados que pueden ser utilizados por cualquier componente del workbench. Estos servicios incluyen gestión de configuración, almacenamiento, temas, y comunicación entre componentes. Para nuestro AI Assistant, será necesario crear servicios específicos que gestionen la comunicación con el backend de IA y el estado del componente.

**Capa de Contribuciones** (`vs/workbench/contrib`): Esta es la capa más relevante para nuestro proyecto, ya que aquí residen todas las funcionalidades específicas que extienden el workbench básico. Cada contribución sigue un patrón específico que incluye un archivo `.contribution.ts` que actúa como punto de entrada y registro del módulo.

### Análisis del Secondary Sidebar

El Secondary Sidebar es implementado a través del archivo `src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`, que extiende la clase `AbstractPaneCompositePart`. Esta implementación proporciona la infraestructura necesaria para mostrar y gestionar paneles en la barra lateral secundaria.

La clase `SidebarPart` define las siguientes características clave que son relevantes para nuestro AI Assistant:

- **Dimensiones Flexibles**: El sidebar tiene un ancho mínimo de 170px y un ancho máximo ilimitado, lo que proporciona suficiente espacio para una interfaz de chat rica.
- **Prioridad de Layout**: Utiliza `LayoutPriority.Low`, lo que significa que se redimensiona después de otros componentes más críticos.
- **Gestión de Estado**: Mantiene el estado de visibilidad y el viewlet activo a través de configuraciones persistentes.

### Patrón de Contribuciones Existente

El análisis del módulo `chat` existente en `src/vs/workbench/contrib/chat/` proporciona un excelente modelo para nuestra implementación. Este módulo demuestra cómo integrar funcionalidades de IA de manera nativa sin depender del sistema de extensiones.

El archivo `chat.contribution.ts` muestra el patrón estándar para registrar contribuciones:

```typescript
// Registro de servicios
registerSingleton(IChatService, ChatService, InstantiationType.Delayed);
registerSingleton(IChatWidgetService, ChatWidgetService, InstantiationType.Delayed);

// Registro de contribuciones del workbench
registerWorkbenchContribution2(ChatGettingStartedContribution.ID, ChatGettingStartedContribution, WorkbenchPhase.BlockRestore);

// Registro de acciones y comandos
registerChatActions();
registerChatExecuteActions();
```

Este patrón será adaptado para nuestro AI Assistant, manteniendo la consistencia con la arquitectura existente.

### Servicios de Comunicación

VSCode utiliza un sistema robusto de servicios para la comunicación entre componentes. Los servicios relevantes para nuestro AI Assistant incluyen:

- **ICommandService**: Para ejecutar comandos del editor desde el AI Assistant
- **IEditorService**: Para interactuar con editores abiertos y obtener contexto del código
- **IConfigurationService**: Para gestionar configuraciones específicas del AI Assistant
- **INotificationService**: Para mostrar notificaciones y mensajes de estado

### Integración con el Sistema de Vistas

El Secondary Sidebar utiliza el sistema de vistas de VSCode, que permite registrar y gestionar múltiples paneles. Nuestro AI Assistant se registrará como una vista personalizada que puede ser mostrada u ocultada según las preferencias del usuario.

La integración se realizará a través del `IViewDescriptorService`, que gestiona el registro y la visibilidad de las vistas en el workbench. Este servicio permite definir:

- Identificador único de la vista
- Título y descripción
- Icono para la barra de actividades
- Condiciones de visibilidad
- Posición predeterminada en el layout

### Consideraciones de Rendimiento

El análisis del código existente revela varias optimizaciones importantes que debemos considerar:

- **Lazy Loading**: Los servicios utilizan `InstantiationType.Delayed` para cargar solo cuando son necesarios
- **Disposable Pattern**: Todos los componentes implementan el patrón Disposable para la gestión adecuada de memoria
- **Event-Driven Architecture**: La comunicación se basa en eventos para minimizar el acoplamiento

Esta arquitectura event-driven será especialmente importante para nuestro AI Assistant, ya que necesitará responder a cambios en el editor, selecciones de texto, y eventos del usuario de manera eficiente.


## Arquitectura Propuesta

### Visión General del Sistema

La arquitectura propuesta para el AI Assistant nativo se basa en una separación clara entre el frontend integrado en Code-OSS y un backend de IA independiente. Esta separación permite mantener la flexibilidad del sistema de IA mientras se integra de manera nativa con la interfaz del editor.

El sistema completo consta de tres componentes principales:

1. **Frontend Nativo**: Integrado directamente en el código fuente de Code-OSS como un módulo de contribución
2. **Backend de IA**: Servidor independiente basado en Flask/FastAPI que proporciona servicios de inteligencia artificial
3. **Capa de Comunicación**: Sistema de comunicación bidireccional entre frontend y backend usando WebSockets y HTTP

### Principios de Diseño

**Integración Nativa**: El AI Assistant se integra directamente en el workbench de Code-OSS sin utilizar el sistema de extensiones. Esto garantiza un rendimiento óptimo y una experiencia de usuario fluida, similar a las funcionalidades nativas del editor.

**Modularidad**: Siguiendo los patrones establecidos en VSCode, el AI Assistant se implementa como un módulo independiente en `workbench/contrib/aiAssistant/`, manteniendo una separación clara de responsabilidades y facilitando el mantenimiento.

**Escalabilidad**: La arquitectura permite agregar nuevas funcionalidades de IA sin modificar el núcleo del sistema. Nuevos servicios pueden ser añadidos al backend y consumidos por el frontend a través de la capa de comunicación establecida.

**Consistencia de UI**: La interfaz del AI Assistant sigue las guías de diseño de VSCode, utilizando los mismos componentes, temas y patrones de interacción que el resto del editor.

### Componentes del Frontend

**AI Assistant View**: El componente principal que se muestra en el Secondary Sidebar. Implementa una interfaz de chat similar a Cursor, con soporte para:
- Conversaciones contextuales con el código
- Visualización de sugerencias y explicaciones
- Botones de acción rápida para tareas comunes
- Historial de conversaciones persistente

**AI Service Layer**: Capa de servicios que gestiona:
- Comunicación con el backend de IA
- Gestión del estado de las conversaciones
- Cache de respuestas para optimizar rendimiento
- Integración con el contexto del editor

**Context Provider**: Componente responsable de extraer y proporcionar contexto relevante del editor:
- Código seleccionado o en el cursor
- Archivos abiertos y su contenido
- Información del proyecto y dependencias
- Historial de cambios recientes

### Componentes del Backend

**API Gateway**: Punto de entrada único para todas las solicitudes del frontend. Implementa:
- Autenticación y autorización
- Rate limiting y throttling
- Logging y monitoreo
- Routing a servicios específicos

**Chat Service**: Servicio principal para conversaciones de IA:
- Procesamiento de consultas en lenguaje natural
- Mantenimiento del contexto de conversación
- Integración con modelos de lenguaje (OpenAI, Anthropic, etc.)
- Generación de respuestas contextuales

**Code Analysis Service**: Servicio especializado en análisis de código:
- Análisis estático de código
- Detección de patrones y antipatrones
- Sugerencias de refactorización
- Explicación de código complejo

**Completion Service**: Servicio de autocompletado inteligente:
- Sugerencias de código basadas en contexto
- Completado de funciones y métodos
- Generación de documentación automática
- Sugerencias de imports y dependencias

### Flujo de Datos

El flujo de datos en el sistema sigue un patrón request-response asíncrono:

1. **Captura de Contexto**: El Context Provider extrae información relevante del editor
2. **Preparación de Request**: El AI Service Layer prepara la solicitud con contexto y metadatos
3. **Comunicación**: La solicitud se envía al backend a través de WebSocket o HTTP
4. **Procesamiento**: El backend procesa la solicitud usando los servicios de IA apropiados
5. **Respuesta**: El backend envía la respuesta de vuelta al frontend
6. **Renderizado**: El AI Assistant View muestra la respuesta al usuario
7. **Persistencia**: El estado de la conversación se guarda para futuras referencias

### Gestión de Estado

El sistema implementa una gestión de estado robusta que incluye:

**Estado Local**: Mantenido en el frontend para respuesta inmediata:
- Estado actual de la conversación
- Configuraciones del usuario
- Cache de respuestas recientes
- Estado de la UI (paneles expandidos, filtros, etc.)

**Estado Persistente**: Almacenado en el backend para persistencia a largo plazo:
- Historial completo de conversaciones
- Preferencias del usuario
- Configuraciones del modelo de IA
- Métricas de uso y rendimiento

**Estado Compartido**: Sincronizado entre frontend y backend:
- Contexto actual del proyecto
- Archivos y cambios recientes
- Estado de autenticación
- Configuraciones de la sesión

### Seguridad y Privacidad

La arquitectura incorpora múltiples capas de seguridad:

**Comunicación Segura**: Todas las comunicaciones entre frontend y backend utilizan HTTPS/WSS con certificados válidos.

**Gestión de Contexto**: El sistema implementa políticas estrictas sobre qué información del código se envía al backend, permitiendo al usuario controlar el nivel de contexto compartido.

**Almacenamiento Local**: Información sensible se mantiene localmente cuando es posible, minimizando la transferencia de datos al backend.

**Configuración de Privacidad**: El usuario puede configurar diferentes niveles de privacidad, desde completamente local hasta completamente en la nube.


## Estructura de Archivos y Módulos

### Organización del Frontend

La implementación del AI Assistant seguirá la estructura estándar de contribuciones de VSCode, ubicándose en `src/vs/workbench/contrib/aiAssistant/`. La organización de archivos propuesta es la siguiente:

```
src/vs/workbench/contrib/aiAssistant/
├── browser/
│   ├── actions/
│   │   ├── aiAssistantActions.ts          # Acciones principales del AI Assistant
│   │   ├── aiChatActions.ts               # Acciones específicas del chat
│   │   ├── aiCodeActions.ts               # Acciones de análisis de código
│   │   └── aiContextActions.ts            # Acciones de gestión de contexto
│   ├── services/
│   │   ├── aiAssistantService.ts          # Servicio principal del AI Assistant
│   │   ├── aiCommunicationService.ts      # Servicio de comunicación con backend
│   │   ├── aiContextService.ts            # Servicio de gestión de contexto
│   │   └── aiStateService.ts              # Servicio de gestión de estado
│   ├── views/
│   │   ├── aiAssistantView.ts             # Vista principal del AI Assistant
│   │   ├── aiChatWidget.ts                # Widget de chat
│   │   ├── aiSuggestionsWidget.ts         # Widget de sugerencias
│   │   └── aiStatusWidget.ts              # Widget de estado
│   ├── media/
│   │   ├── aiAssistant.css                # Estilos del AI Assistant
│   │   └── icons/                         # Iconos específicos
│   ├── aiAssistant.contribution.ts        # Punto de entrada principal
│   └── aiAssistantTypes.ts                # Definiciones de tipos
├── common/
│   ├── aiAssistantService.ts              # Interfaz del servicio principal
│   ├── aiCommunicationProtocol.ts         # Protocolo de comunicación
│   ├── aiContextTypes.ts                  # Tipos de contexto
│   └── aiConstants.ts                     # Constantes del sistema
└── electron-browser/
    └── aiAssistant.contribution.ts        # Contribución específica de Electron
```

### Archivos Clave del Frontend

**aiAssistant.contribution.ts**: Este archivo actúa como el punto de entrada principal del módulo y es responsable de registrar todos los servicios, vistas, acciones y comandos del AI Assistant. Siguiendo el patrón establecido por otros módulos de VSCode, este archivo incluirá:

```typescript
// Registro de servicios singleton
registerSingleton(IAiAssistantService, AiAssistantService, InstantiationType.Delayed);
registerSingleton(IAiCommunicationService, AiCommunicationService, InstantiationType.Delayed);

// Registro de vistas
Registry.as<IViewsRegistry>(ViewExtensions.ViewsRegistry).registerViews([{
    id: AI_ASSISTANT_VIEW_ID,
    name: localize('aiAssistant', 'AI Assistant'),
    ctorDescriptor: new SyncDescriptor(AiAssistantView),
    canToggleVisibility: true,
    canMoveView: true,
    containerIcon: aiAssistantIcon,
    when: ContextKeyExpr.true()
}], viewContainer);

// Registro de acciones
registerAiAssistantActions();
```

**aiAssistantView.ts**: Implementa la vista principal que se muestra en el Secondary Sidebar. Esta clase extiende `ViewPane` y proporciona la interfaz principal para interactuar con el AI Assistant:

```typescript
export class AiAssistantView extends ViewPane {
    private chatWidget: AiChatWidget;
    private suggestionsWidget: AiSuggestionsWidget;
    private statusWidget: AiStatusWidget;

    constructor(
        options: IViewPaneOptions,
        @IAiAssistantService private readonly aiService: IAiAssistantService,
        @IContextKeyService contextKeyService: IContextKeyService,
        // ... otros servicios
    ) {
        super(options, keybindingService, contextMenuService, configurationService, contextKeyService, viewDescriptorService, instantiationService, openerService, themeService, telemetryService, hoverService);
    }

    protected renderBody(container: HTMLElement): void {
        // Implementación del renderizado de la UI
    }
}
```

**aiCommunicationService.ts**: Gestiona toda la comunicación con el backend de IA, implementando tanto conexiones WebSocket para comunicación en tiempo real como HTTP para solicitudes puntuales:

```typescript
export class AiCommunicationService implements IAiCommunicationService {
    private websocket: WebSocket | null = null;
    private readonly httpClient: HttpClient;

    async sendChatMessage(message: string, context: AiContext): Promise<AiResponse> {
        // Implementación de envío de mensajes
    }

    async requestCodeAnalysis(code: string): Promise<AiCodeAnalysis> {
        // Implementación de análisis de código
    }

    private establishWebSocketConnection(): void {
        // Implementación de conexión WebSocket
    }
}
```

### Organización del Backend

El backend de IA se organizará como un proyecto Python independiente con la siguiente estructura:

```
ai-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada de la aplicación
│   ├── config.py                  # Configuración de la aplicación
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat_models.py         # Modelos de datos para chat
│   │   ├── code_models.py         # Modelos de datos para código
│   │   └── context_models.py      # Modelos de contexto
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py        # Servicio de chat con IA
│   │   ├── code_analysis_service.py # Servicio de análisis de código
│   │   ├── completion_service.py   # Servicio de autocompletado
│   │   └── context_service.py     # Servicio de gestión de contexto
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat_routes.py         # Rutas de API para chat
│   │   ├── code_routes.py         # Rutas de API para código
│   │   └── websocket_routes.py    # Rutas de WebSocket
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py                # Utilidades de autenticación
│   │   ├── logging.py             # Configuración de logging
│   │   └── validation.py          # Validación de datos
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py                # Middleware de CORS
│       ├── rate_limiting.py       # Middleware de rate limiting
│       └── error_handling.py      # Manejo de errores
├── tests/
│   ├── __init__.py
│   ├── test_chat_service.py
│   ├── test_code_analysis.py
│   └── test_api_routes.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### Archivos de Configuración

**Frontend Configuration**: El AI Assistant utilizará el sistema de configuración de VSCode para permitir personalización por parte del usuario:

```typescript
// En aiAssistant.contribution.ts
const configurationRegistry = Registry.as<IConfigurationRegistry>(ConfigurationExtensions.Configuration);
configurationRegistry.registerConfiguration({
    id: 'aiAssistant',
    order: 20,
    title: localize('aiAssistantConfiguration', 'AI Assistant'),
    properties: {
        'aiAssistant.enabled': {
            type: 'boolean',
            default: true,
            description: localize('aiAssistant.enabled', 'Enable AI Assistant functionality')
        },
        'aiAssistant.backend.url': {
            type: 'string',
            default: 'ws://localhost:8000',
            description: localize('aiAssistant.backend.url', 'AI Assistant backend URL')
        },
        'aiAssistant.chat.maxHistory': {
            type: 'number',
            default: 50,
            description: localize('aiAssistant.chat.maxHistory', 'Maximum number of chat messages to keep in history')
        }
    }
});
```

**Backend Configuration**: El backend utilizará variables de entorno y archivos de configuración para gestionar diferentes entornos:

```python
# config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Assistant Backend"
    debug: bool = False
    backend_cors_origins: list = ["http://localhost:3000"]
    
    # AI Model Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = "gpt-4"
    max_tokens: int = 2048
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ai_assistant.db")
    
    # WebSocket Configuration
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Integración con el Sistema de Build

Para integrar el AI Assistant en el proceso de build de VSCode, será necesario modificar varios archivos de configuración:

**Modificación de workbench.common.main.ts**: Agregar la importación del módulo AI Assistant para asegurar que se cargue durante la inicialización:

```typescript
// En src/vs/workbench/workbench.common.main.ts
import 'vs/workbench/contrib/aiAssistant/browser/aiAssistant.contribution';
```

**Actualización de package.json**: Agregar dependencias específicas del AI Assistant si son necesarias:

```json
{
  "dependencies": {
    "ws": "^8.13.0",
    "axios": "^1.4.0"
  }
}
```

Esta estructura modular permite un desarrollo incremental y facilita el mantenimiento a largo plazo, siguiendo las mejores prácticas establecidas en el ecosistema de VSCode.


## Integración con el Secondary Sidebar

### Modificación del Sistema de Vistas

La integración del AI Assistant en el Secondary Sidebar requiere modificaciones específicas en el sistema de gestión de vistas de VSCode. El proceso de integración se realiza a través de varios pasos clave que aseguran una integración nativa y consistente con el resto del editor.

**Registro de View Container**: El AI Assistant se registra como un view container independiente que puede contener múltiples vistas relacionadas con IA:

```typescript
const AI_ASSISTANT_CONTAINER_ID = 'workbench.view.aiAssistant';

const viewContainer: IViewContainerDescriptor = {
    id: AI_ASSISTANT_CONTAINER_ID,
    title: localize('aiAssistant', 'AI Assistant'),
    icon: aiAssistantIcon,
    ctorDescriptor: new SyncDescriptor(ViewPaneContainer, [AI_ASSISTANT_CONTAINER_ID, { mergeViewWithContainerWhenSingleView: true }]),
    storageId: AI_ASSISTANT_CONTAINER_ID,
    hideIfEmpty: true,
    order: 3, // Posición en el Secondary Sidebar
};

Registry.as<IViewContainersRegistry>(ViewExtensions.ViewContainersRegistry)
    .registerViewContainer(viewContainer, ViewContainerLocation.AuxiliaryBar);
```

**Configuración de Layout**: El AI Assistant se configura para aparecer en el Secondary Sidebar (AuxiliaryBar) por defecto, pero permite al usuario moverlo a otras ubicaciones según sus preferencias:

```typescript
// Configuración de posición predeterminada
const defaultViewLocation = {
    [AI_ASSISTANT_VIEW_ID]: ViewContainerLocation.AuxiliaryBar
};

// Registro de la configuración de layout
Registry.as<IDefaultViewLocationRegistry>(ViewExtensions.DefaultViewLocationRegistry)
    .registerDefaultViewLocation(AI_ASSISTANT_VIEW_ID, ViewContainerLocation.AuxiliaryBar);
```

### Gestión de Estado del Sidebar

El AI Assistant implementa un sistema robusto de gestión de estado que se integra con el sistema de persistencia de VSCode:

**Persistencia de Estado**: El estado del AI Assistant se guarda automáticamente y se restaura entre sesiones:

```typescript
export class AiAssistantStateService implements IAiAssistantStateService {
    private static readonly STORAGE_KEY = 'aiAssistant.state';
    
    constructor(
        @IStorageService private readonly storageService: IStorageService
    ) {}

    saveState(state: AiAssistantState): void {
        this.storageService.store(
            AiAssistantStateService.STORAGE_KEY,
            JSON.stringify(state),
            StorageScope.WORKSPACE,
            StorageTarget.USER
        );
    }

    loadState(): AiAssistantState | null {
        const stored = this.storageService.get(
            AiAssistantStateService.STORAGE_KEY,
            StorageScope.WORKSPACE
        );
        return stored ? JSON.parse(stored) : null;
    }
}
```

**Sincronización con Editor**: El AI Assistant mantiene sincronización automática con el estado del editor para proporcionar contexto relevante:

```typescript
export class AiContextSyncService {
    constructor(
        @IEditorService private readonly editorService: IEditorService,
        @ITextModelService private readonly textModelService: ITextModelService
    ) {
        this.registerEventListeners();
    }

    private registerEventListeners(): void {
        // Escuchar cambios en el editor activo
        this.editorService.onDidActiveEditorChange(() => {
            this.updateContext();
        });

        // Escuchar cambios en la selección
        this.editorService.onDidChangeSelection(() => {
            this.updateSelectionContext();
        });
    }
}
```

## Backend de Inteligencia Artificial

### Arquitectura del Servidor

El backend de IA está diseñado como un microservicio independiente que puede escalarse horizontalmente según las necesidades de carga. La arquitectura utiliza FastAPI como framework principal debido a su excelente soporte para APIs asíncronas y WebSockets.

**Servidor Principal**: El servidor principal gestiona todas las conexiones entrantes y las distribuye a los servicios apropiados:

```python
# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Assistant Backend", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestor de conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Procesar mensaje y enviar respuesta
            response = await process_ai_request(data)
            await manager.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Servicios de IA

**Chat Service**: Implementa la funcionalidad principal de chat con IA, incluyendo mantenimiento de contexto y generación de respuestas:

```python
# services/chat_service.py
from openai import AsyncOpenAI
from typing import List, Dict
import json

class ChatService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.conversations: Dict[str, List[Dict]] = {}

    async def process_chat_message(self, user_id: str, message: str, context: Dict) -> str:
        # Preparar contexto de la conversación
        conversation = self.conversations.get(user_id, [])
        
        # Agregar contexto del código si está disponible
        system_message = self.build_system_message(context)
        
        messages = [
            {"role": "system", "content": system_message},
            *conversation,
            {"role": "user", "content": message}
        ]

        # Generar respuesta usando OpenAI
        response = await self.client.chat.completions.create(
            model=settings.model_name,
            messages=messages,
            max_tokens=settings.max_tokens,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        
        # Actualizar historial de conversación
        conversation.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Mantener solo los últimos N mensajes
        if len(conversation) > settings.max_conversation_history:
            conversation = conversation[-settings.max_conversation_history:]
        
        self.conversations[user_id] = conversation
        
        return ai_response

    def build_system_message(self, context: Dict) -> str:
        system_parts = [
            "You are an AI assistant integrated into a code editor.",
            "Help the user with coding tasks, explanations, and improvements."
        ]
        
        if context.get('current_file'):
            system_parts.append(f"Current file: {context['current_file']}")
        
        if context.get('selected_code'):
            system_parts.append(f"Selected code:\n```\n{context['selected_code']}\n```")
        
        if context.get('project_info'):
            system_parts.append(f"Project context: {context['project_info']}")
        
        return "\n\n".join(system_parts)
```

**Code Analysis Service**: Proporciona análisis estático de código y sugerencias de mejora:

```python
# services/code_analysis_service.py
import ast
import re
from typing import List, Dict, Any

class CodeAnalysisService:
    def __init__(self):
        self.analyzers = {
            'python': self.analyze_python_code,
            'javascript': self.analyze_javascript_code,
            'typescript': self.analyze_typescript_code
        }

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        analyzer = self.analyzers.get(language.lower())
        if not analyzer:
            return {"error": f"Unsupported language: {language}"}
        
        try:
            analysis = analyzer(code)
            suggestions = await self.generate_suggestions(code, language, analysis)
            
            return {
                "analysis": analysis,
                "suggestions": suggestions,
                "metrics": self.calculate_metrics(code, analysis)
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_issues": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "complexity": self.calculate_cyclomatic_complexity(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis["imports"].append({
                        "line": node.lineno,
                        "module": getattr(node, 'module', None),
                        "names": [alias.name for alias in node.names]
                    })
            
            return analysis
            
        except SyntaxError as e:
            return {"syntax_error": str(e)}

    async def generate_suggestions(self, code: str, language: str, analysis: Dict) -> List[str]:
        suggestions = []
        
        # Sugerencias basadas en análisis estático
        if analysis.get("functions"):
            for func in analysis["functions"]:
                if func.get("complexity", 0) > 10:
                    suggestions.append(f"Function '{func['name']}' has high complexity. Consider refactoring.")
        
        # Usar IA para sugerencias más sofisticadas
        ai_suggestions = await self.get_ai_suggestions(code, language, analysis)
        suggestions.extend(ai_suggestions)
        
        return suggestions

    async def get_ai_suggestions(self, code: str, language: str, analysis: Dict) -> List[str]:
        # Implementar llamada a IA para sugerencias contextuales
        prompt = f"""
        Analyze this {language} code and provide specific improvement suggestions:
        
        Code:
        ```{language}
        {code}
        ```
        
        Static analysis results:
        {json.dumps(analysis, indent=2)}
        
        Provide 3-5 specific, actionable suggestions for improvement.
        """
        
        # Llamada a OpenAI para obtener sugerencias
        # (implementación similar al ChatService)
        return []  # Placeholder
```

## Comunicación Frontend-Backend

### Protocolo de Comunicación

El sistema implementa un protocolo de comunicación híbrido que utiliza tanto WebSockets para comunicación en tiempo real como HTTP REST para operaciones puntuales:

**WebSocket Protocol**: Para comunicación bidireccional en tiempo real:

```typescript
// Frontend - aiCommunicationService.ts
interface AiMessage {
    id: string;
    type: 'chat' | 'code_analysis' | 'completion' | 'status';
    payload: any;
    timestamp: number;
    context?: AiContext;
}

interface AiResponse {
    id: string;
    type: string;
    payload: any;
    status: 'success' | 'error' | 'pending';
    timestamp: number;
}

export class AiCommunicationService implements IAiCommunicationService {
    private websocket: WebSocket | null = null;
    private messageQueue: Map<string, (response: AiResponse) => void> = new Map();
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;

    async connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.backendUrl);
                
                this.websocket.onopen = () => {
                    this.reconnectAttempts = 0;
                    resolve();
                };

                this.websocket.onmessage = (event) => {
                    this.handleMessage(JSON.parse(event.data));
                };

                this.websocket.onclose = () => {
                    this.handleDisconnection();
                };

                this.websocket.onerror = (error) => {
                    reject(error);
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    async sendMessage(message: AiMessage): Promise<AiResponse> {
        return new Promise((resolve, reject) => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                reject(new Error('WebSocket not connected'));
                return;
            }

            const messageId = message.id || this.generateMessageId();
            message.id = messageId;

            this.messageQueue.set(messageId, resolve);
            this.websocket.send(JSON.stringify(message));

            // Timeout después de 30 segundos
            setTimeout(() => {
                if (this.messageQueue.has(messageId)) {
                    this.messageQueue.delete(messageId);
                    reject(new Error('Request timeout'));
                }
            }, 30000);
        });
    }

    private handleMessage(response: AiResponse): void {
        const callback = this.messageQueue.get(response.id);
        if (callback) {
            callback(response);
            this.messageQueue.delete(response.id);
        }
    }

    private async handleDisconnection(): void {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Backoff exponencial
            
            setTimeout(() => {
                this.connect().catch(() => {
                    // Manejar error de reconexión
                });
            }, delay);
        }
    }
}
```

### Gestión de Contexto

El sistema implementa una gestión inteligente de contexto que optimiza la información enviada al backend:

```typescript
// aiContextService.ts
export class AiContextService implements IAiContextService {
    constructor(
        @IEditorService private readonly editorService: IEditorService,
        @IWorkspaceContextService private readonly workspaceService: IWorkspaceContextService,
        @IFileService private readonly fileService: IFileService
    ) {}

    async getCurrentContext(): Promise<AiContext> {
        const activeEditor = this.editorService.activeTextEditorControl;
        const context: AiContext = {
            timestamp: Date.now(),
            workspace: this.getWorkspaceInfo(),
            editor: null,
            selection: null,
            openFiles: []
        };

        if (activeEditor && isCodeEditor(activeEditor)) {
            const model = activeEditor.getModel();
            if (model) {
                context.editor = {
                    fileName: model.uri.fsPath,
                    language: model.getLanguageId(),
                    lineCount: model.getLineCount(),
                    content: this.shouldIncludeFullContent() ? model.getValue() : null
                };

                const selection = activeEditor.getSelection();
                if (selection && !selection.isEmpty()) {
                    context.selection = {
                        text: model.getValueInRange(selection),
                        startLine: selection.startLineNumber,
                        endLine: selection.endLineNumber,
                        startColumn: selection.startColumn,
                        endColumn: selection.endColumn
                    };
                }
            }
        }

        // Obtener información de archivos abiertos
        context.openFiles = this.getOpenFilesInfo();

        return context;
    }

    private shouldIncludeFullContent(): boolean {
        // Lógica para determinar si incluir el contenido completo del archivo
        // basado en configuraciones de privacidad y tamaño del archivo
        const config = this.configurationService.getValue<AiAssistantConfiguration>('aiAssistant');
        return config.context.includeFullFile && this.getCurrentFileSize() < config.context.maxFileSize;
    }

    private getWorkspaceInfo(): WorkspaceInfo {
        const workspace = this.workspaceService.getWorkspace();
        return {
            name: workspace.name,
            folders: workspace.folders.map(folder => ({
                name: folder.name,
                uri: folder.uri.toString()
            })),
            configuration: this.getRelevantWorkspaceConfig()
        };
    }
}
```

## Servicios y APIs

### Definición de Interfaces

El sistema define interfaces claras para todos los servicios, facilitando el testing y la extensibilidad:

```typescript
// common/aiAssistantService.ts
export interface IAiAssistantService {
    readonly onDidChangeState: Event<AiAssistantState>;
    
    sendChatMessage(message: string, context?: AiContext): Promise<AiChatResponse>;
    requestCodeAnalysis(code: string, language: string): Promise<AiCodeAnalysis>;
    requestCompletion(prefix: string, suffix: string, context: AiContext): Promise<AiCompletion[]>;
    
    getConversationHistory(): AiConversation[];
    clearConversationHistory(): void;
    
    isConnected(): boolean;
    getConnectionStatus(): AiConnectionStatus;
}

export interface IAiCommunicationService {
    readonly onDidConnect: Event<void>;
    readonly onDidDisconnect: Event<void>;
    readonly onDidReceiveMessage: Event<AiResponse>;
    
    connect(): Promise<void>;
    disconnect(): void;
    sendMessage(message: AiMessage): Promise<AiResponse>;
    
    isConnected(): boolean;
    getLastError(): Error | null;
}

export interface IAiContextService {
    readonly onDidChangeContext: Event<AiContext>;
    
    getCurrentContext(): Promise<AiContext>;
    getSelectionContext(): AiSelectionContext | null;
    getWorkspaceContext(): AiWorkspaceContext;
    
    setContextFilter(filter: AiContextFilter): void;
    getContextFilter(): AiContextFilter;
}
```

### API Endpoints del Backend

El backend expone una API REST completa además de la comunicación WebSocket:

```python
# api/chat_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: int

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        response = await chat_service.process_chat_message(
            user_id=request.conversation_id or "default",
            message=request.message,
            context=request.context or {}
        )
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id or "default",
            timestamp=int(time.time())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    history = chat_service.get_conversation_history(conversation_id)
    return {"history": history}

@router.delete("/history/{conversation_id}")
async def clear_conversation_history(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    chat_service.clear_conversation_history(conversation_id)
    return {"status": "cleared"}
```

## Consideraciones de Implementación

### Fases de Desarrollo

La implementación del AI Assistant se realizará en fases incrementales para minimizar riesgos y permitir testing continuo:

**Fase 1 - Infraestructura Base**: Implementación de la estructura básica del módulo, servicios fundamentales y comunicación básica con el backend.

**Fase 2 - UI Básica**: Desarrollo de la interfaz de usuario básica en el Secondary Sidebar con funcionalidad de chat simple.

**Fase 3 - Servicios de IA**: Implementación completa de los servicios de IA en el backend, incluyendo chat, análisis de código y autocompletado.

**Fase 4 - Integración Avanzada**: Implementación de funcionalidades avanzadas como gestión de contexto inteligente, persistencia de estado y optimizaciones de rendimiento.

**Fase 5 - Testing y Optimización**: Testing exhaustivo, optimización de rendimiento y preparación para producción.

### Consideraciones de Rendimiento

**Lazy Loading**: Todos los componentes del AI Assistant se cargan de manera diferida para no impactar el tiempo de inicio del editor.

**Caching**: Implementación de cache inteligente para respuestas de IA frecuentes y análisis de código repetitivos.

**Debouncing**: Las solicitudes de análisis de código se debounce para evitar llamadas excesivas durante la edición activa.

**Connection Pooling**: El backend utiliza connection pooling para optimizar las conexiones a servicios de IA externos.

### Consideraciones de Seguridad

**Validación de Entrada**: Todas las entradas del usuario se validan tanto en frontend como backend para prevenir ataques de inyección.

**Rate Limiting**: Implementación de rate limiting para prevenir abuso del sistema de IA.

**Sanitización de Contexto**: El contexto del código se sanitiza antes de enviarlo a servicios externos para proteger información sensible.

**Configuración de Privacidad**: Los usuarios pueden configurar qué información se comparte con el backend de IA.

### Testing Strategy

**Unit Testing**: Testing exhaustivo de todos los servicios y componentes individuales.

**Integration Testing**: Testing de la comunicación entre frontend y backend.

**End-to-End Testing**: Testing de flujos completos de usuario usando herramientas como Playwright.

**Performance Testing**: Testing de carga para asegurar que el sistema puede manejar múltiples usuarios concurrentes.

Esta arquitectura proporciona una base sólida para la implementación de un AI Assistant nativo en Code-OSS, manteniendo la flexibilidad para futuras extensiones y optimizaciones.

