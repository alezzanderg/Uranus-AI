# 🤖 Multi-Model AI Guide - Uranus-AI

Uranus-AI ahora soporta múltiples proveedores de IA, permitiéndote elegir el mejor modelo para cada tarea específica.

## 🌟 Modelos Soportados

### 🔥 OpenAI
- **GPT-4 Turbo**: Modelo más avanzado con 128k contexto y visión
- **GPT-4**: Excelente para razonamiento complejo
- **GPT-3.5 Turbo**: Rápido y económico para tareas generales

### 🧠 Anthropic Claude
- **Claude 3 Opus**: El más poderoso para análisis complejo
- **Claude 3 Sonnet**: Balance perfecto entre rendimiento y costo
- **Claude 3 Haiku**: El más rápido para respuestas inmediatas

### 🔍 Google Gemini
- **Gemini Pro**: Modelo versátil de Google
- **Gemini Pro Vision**: Con capacidades de visión

### 🚀 xAI Grok
- **Grok Beta**: IA conversacional con conocimiento en tiempo real

### 💻 DeepSeek
- **DeepSeek Coder**: Especializado en generación y análisis de código
- **DeepSeek Chat**: Modelo conversacional general

### 🏠 Ollama (Local)
- **Llama 2**: Meta's Llama 2 ejecutándose localmente
- **Code Llama**: Modelo especializado en código local

### 🌊 Mistral
- **Mistral Large**: Modelo más capaz de Mistral
- **Mistral Medium**: Rendimiento balanceado

### 🎯 Cohere
- **Command R+**: Modelo avanzado con contexto largo

## 🛠️ Configuración

### 1. Variables de Entorno

Copia y configura el archivo `.env`:

```bash
cp ai-backend/.env.example ai-backend/.env
```

### 2. API Keys Requeridas

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# xAI Grok
XAI_API_KEY=your_xai_api_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Mistral
MISTRAL_API_KEY=your_mistral_api_key_here

# Cohere
COHERE_API_KEY=your_cohere_api_key_here

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 3. Configuración de Modelos por Defecto

```env
DEFAULT_MODEL=gpt-4
FALLBACK_MODELS=["gpt-3.5-turbo", "claude-3-haiku", "gemini-pro"]
ENABLE_MODEL_SWITCHING=true
ENABLE_AUTO_FALLBACK=true
```

## 🎯 Uso de Múltiples Modelos

### 1. Selección Automática de Modelo

El sistema puede recomendar el mejor modelo basado en la tarea:

```typescript
// En el frontend
const recommendations = await fetch('/api/v1/models/select', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_type: 'code_analysis',
    context_length: 8000,
    prefer_cost_effective: false
  })
});
```

### 2. Comparación de Modelos

Compara múltiples modelos con el mismo prompt:

```typescript
const comparison = await fetch('/api/v1/models/compare', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    models: ['gpt-4', 'claude-3-opus', 'gemini-pro'],
    test_prompt: 'Explain this JavaScript function',
    criteria: ['quality', 'speed', 'cost']
  })
});
```

### 3. Uso Directo de Modelo Específico

```typescript
const response = await fetch('/api/v1/models/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model_id: 'claude-3-opus',
    provider: 'anthropic',
    messages: [
      { role: 'user', content: 'Analyze this code for bugs' }
    ],
    temperature: 0.7
  })
});
```

## 📊 Características por Modelo

| Modelo | Proveedor | Contexto | Costo/1K | Mejor Para |
|--------|-----------|----------|----------|------------|
| GPT-4 Turbo | OpenAI | 128K | $0.01 | Análisis complejo, visión |
| Claude 3 Opus | Anthropic | 200K | $0.015 | Razonamiento profundo |
| Claude 3 Sonnet | Anthropic | 200K | $0.003 | Balance costo/calidad |
| Claude 3 Haiku | Anthropic | 200K | $0.00025 | Respuestas rápidas |
| Gemini Pro | Google | 32K | $0.0005 | Tareas generales |
| Grok Beta | xAI | 131K | $0.005 | Conocimiento actual |
| DeepSeek Coder | DeepSeek | 16K | $0.0014 | Programación |
| Llama 2 | Ollama | 4K | Gratis | Uso local/privado |

## 🎛️ Configuración Avanzada

### Fallback Automático

Si un modelo falla, el sistema automáticamente intenta con modelos de respaldo:

```env
ENABLE_AUTO_FALLBACK=true
FALLBACK_MODELS=["gpt-3.5-turbo", "claude-3-haiku", "gemini-pro"]
```

### Optimización de Costos

Habilita la optimización automática de costos:

```env
ENABLE_COST_OPTIMIZATION=true
PREFER_COST_EFFECTIVE=true
```

### Límites de Velocidad

Configura límites por modelo:

```env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## 🔄 Integración en el Frontend

### Selector de Modelo en UI

El AI Assistant ahora incluye un selector de modelo:

```typescript
// En aiAssistantView.ts
private createModelSelector(): HTMLElement {
  const selector = document.createElement('select');
  selector.className = 'ai-model-selector';
  
  // Cargar modelos disponibles
  this.loadAvailableModels().then(models => {
    models.forEach(model => {
      const option = document.createElement('option');
      option.value = model.id;
      option.textContent = `${model.name} (${model.provider})`;
      selector.appendChild(option);
    });
  });
  
  return selector;
}
```

### Chat con Modelo Específico

```typescript
async sendMessage(message: string, modelId?: string) {
  const selectedModel = modelId || this.getSelectedModel();
  
  const response = await this.communicationService.sendMessage({
    message,
    model_id: selectedModel,
    context: await this.contextService.getCurrentContext()
  });
  
  return response;
}
```

## 📈 Monitoreo y Analytics

### Estadísticas de Uso

Obtén estadísticas detalladas de uso:

```bash
curl http://localhost:8000/api/v1/models/stats
```

### Benchmarking

Ejecuta benchmarks automáticos:

```bash
curl -X POST http://localhost:8000/api/v1/models/benchmark \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gpt-4", "claude-3-opus", "gemini-pro"],
    "test_prompts": [
      "Explain quantum computing",
      "Write a Python function to sort a list",
      "Debug this JavaScript code"
    ]
  }'
```

## 🎯 Recomendaciones de Uso

### Para Chat General
1. **Claude 3 Sonnet** - Excelente balance
2. **GPT-4** - Respuestas de alta calidad
3. **Gemini Pro** - Opción económica

### Para Análisis de Código
1. **DeepSeek Coder** - Especializado en código
2. **Claude 3 Opus** - Análisis profundo
3. **GPT-4** - Versatilidad

### Para Respuestas Rápidas
1. **Claude 3 Haiku** - Más rápido
2. **GPT-3.5 Turbo** - Económico y rápido
3. **Gemini Pro** - Balance velocidad/costo

### Para Contexto Largo
1. **Claude 3 Sonnet** - 200K contexto
2. **GPT-4 Turbo** - 128K contexto
3. **Grok Beta** - 131K contexto

### Para Uso Local/Privado
1. **Code Llama** - Especializado en código
2. **Llama 2** - Uso general
3. **Ollama** - Fácil configuración local

## 🔧 Solución de Problemas

### Modelo No Disponible
```
Error: Client not configured for provider: anthropic
```
**Solución**: Verifica que la API key esté configurada en `.env`

### Límite de Tokens Excedido
```
Error: Token limit exceeded
```
**Solución**: Usa un modelo con mayor contexto o reduce el texto

### Fallback No Funciona
```
Error: All models failed
```
**Solución**: Verifica que al menos un modelo de fallback esté configurado

## 🚀 Próximas Funcionalidades

- [ ] **Modelos Locales Adicionales**: Soporte para más modelos Ollama
- [ ] **Fine-tuning**: Personalización de modelos
- [ ] **Embeddings**: Búsqueda semántica avanzada
- [ ] **Multimodal**: Soporte completo para imágenes y audio
- [ ] **Streaming Mejorado**: Streaming paralelo de múltiples modelos
- [ ] **Cache Inteligente**: Cache compartido entre modelos

## 💡 Tips y Trucos

### 1. Combinar Modelos
Usa diferentes modelos para diferentes partes de una tarea:
- **DeepSeek Coder** para generar código
- **Claude 3 Opus** para explicar el código
- **GPT-4** para documentación

### 2. Optimización de Costos
- Usa **Claude 3 Haiku** para tareas simples
- Reserva **GPT-4** para análisis complejos
- Aprovecha **modelos locales** para desarrollo

### 3. Contexto Largo
- **Claude 3** para documentos largos
- **GPT-4 Turbo** para análisis de repositorios completos
- **Grok** para información actualizada

---

¡Con múltiples modelos, Uranus-AI se convierte en la herramienta de IA más versátil para desarrollo! 🪐🚀

