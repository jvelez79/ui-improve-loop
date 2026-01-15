# Especificación Técnica: Voice Notifications Plugin

## Resumen

Plugin de Claude Code que proporciona notificaciones de voz contextuales en español usando Chatterbox TTS (Resemble AI). El plugin intercepta eventos del ciclo de vida del agente (Stop, Notification) para generar mensajes de voz que informan al usuario sobre el estado de las tareas sin necesidad de monitorear visualmente la terminal.

**Approach técnico**: Hooks de Claude Code ejecutan scripts bash que generan mensajes contextuales y delegan la síntesis de voz a un script Python que usa Chatterbox TTS. La configuración on/off se maneja mediante un archivo de estado local.

## Arquitectura

```
Claude Code Agent
    ↓
Hook Triggered (Stop / Notification)
    ↓
hooks/voice-notification-hook.sh
    ↓ (lee estado y contexto)
    ↓
scripts/speak.py (Chatterbox TTS)
    ↓
Audio Output (Sistema)
```

### Flujo de datos

1. **Hook Stop**: Claude Code termina una tarea → hook extrae contexto del transcript → genera mensaje "Tarea completada: [descripción]" → invoca speak.py
2. **Hook Notification**: Sistema requiere atención → hook extrae pregunta del evento → genera mensaje "Claude necesita tu atención: [contexto]" → invoca speak.py
3. **Errores**: Detectados en transcript → mensaje "Ha ocurrido un error: [tipo]" → invoca speak.py

### Dependencias externas

- **Chatterbox TTS**: Biblioteca Python de Resemble AI (instalación manual por el usuario)
- **Python 3.8+**: Requerido para ejecutar el script TTS
- **Audio system**: Dependencias del sistema operativo para reproducción de audio (instaladas por Chatterbox)

## Componentes

### 1. Hook Stop (stop-hook.sh)

- **Ubicación**: `plugins/voice-notifications/hooks/stop-hook.sh`
- **Responsabilidad**: Intercepta el fin de sesión del agente, extrae contexto de la tarea completada y genera notificación de voz
- **Interface**: 
  - Input: Stdin con transcript JSON (provisto por Claude Code)
  - Output: Retorna exit code 0 (no bloquea la salida)
- **Dependencias**: 
  - `scripts/speak.py` - Síntesis de voz
  - `.claude-plugin/settings.json` - Configuración on/off
  - Herramientas: jq (para parsear JSON), sed, awk

**Lógica**:
```bash
1. Leer configuración (enabled: true/false)
2. Si disabled → exit 0
3. Leer transcript desde stdin
4. Extraer último mensaje del assistant
5. Generar descripción breve de la tarea (primeras 100 palabras)
6. Invocar speak.py con mensaje: "La tarea ha sido completada: [descripción]"
7. Exit 0 (no bloquear)
```

### 2. Hook Notification (notification-hook.sh)

- **Ubicación**: `plugins/voice-notifications/hooks/notification-hook.sh`
- **Responsabilidad**: Intercepta notificaciones del sistema que requieren atención del usuario
- **Interface**: 
  - Input: Stdin con evento de notificación JSON
  - Output: Retorna exit code 0
- **Dependencias**: 
  - `scripts/speak.py`
  - `.claude-plugin/settings.json`
  - jq, sed

**Lógica**:
```bash
1. Leer configuración (enabled: true/false)
2. Si disabled → exit 0
3. Leer evento desde stdin
4. Extraer mensaje de la notificación
5. Invocar speak.py con mensaje: "Claude necesita tu atención: [mensaje]"
6. Exit 0
```

### 3. Script TTS (speak.py)

- **Ubicación**: `plugins/voice-notifications/scripts/speak.py`
- **Responsabilidad**: Interfaz con Chatterbox TTS para sintetizar y reproducir voz
- **Interface**:
  ```bash
  speak.py --text "Mensaje a sintetizar" [--voice nombre_voz]
  ```
- **Dependencias**: 
  - `chatterbox` (pip package)
  - `.claude-plugin/settings.json` - Voz seleccionada por el usuario

**Funcionalidades**:
- Cargar voz configurada (default: voice español de Chatterbox)
- Sintetizar texto a audio
- Reproducir audio en el sistema
- Manejo de errores (si Chatterbox no instalado, mostrar mensaje en stderr)

### 4. Archivo de Configuración (settings.json)

- **Ubicación**: `plugins/voice-notifications/.claude-plugin/settings.json`
- **Responsabilidad**: Almacenar preferencias del usuario
- **Schema**:
```json
{
  "enabled": true,
  "voice": "es-ES-Standard-A",
  "volume": 0.8,
  "speed": 1.0
}
```

### 5. Registro de Hooks (hooks.json)

- **Ubicación**: `plugins/voice-notifications/hooks/hooks.json`
- **Responsabilidad**: Declarar qué hooks se registran
- **Schema**:
```json
{
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
        }
      ]
    }
  ],
  "Notification": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "${CLAUDE_PLUGIN_ROOT}/hooks/notification-hook.sh"
        }
      ]
    }
  ]
}
```

### 6. Metadata del Plugin (plugin.json)

- **Ubicación**: `plugins/voice-notifications/.claude-plugin/plugin.json`
- **Responsabilidad**: Metadata del plugin para Claude Code
- **Schema**:
```json
{
  "name": "voice-notifications",
  "version": "1.0.0",
  "description": "Notificaciones de voz contextuales en español usando Chatterbox TTS",
  "author": {
    "name": "jvelez79"
  },
  "repository": "https://github.com/jvelez79/claude-code-plugins",
  "license": "MIT",
  "keywords": ["tts", "voice", "notifications", "accessibility", "chatterbox"]
}
```

### 7. Comando de Configuración (config.md)

- **Ubicación**: `plugins/voice-notifications/commands/config.md`
- **Responsabilidad**: Permitir al usuario habilitar/deshabilitar el plugin y configurar voz
- **Interface**: 
  ```bash
  /voice-notifications:config [--enable|--disable] [--voice nombre_voz] [--list-voices]
  ```
- **Allowed Tools**: 
  - `Read` - Leer settings.json
  - `Write` - Actualizar settings.json
  - `Bash(${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices)` - Listar voces disponibles

## Contratos

### Hook Input/Output

#### Hook Stop - Input (stdin)
```json
{
  "transcript": [
    {
      "role": "user",
      "content": "Instrucción del usuario"
    },
    {
      "role": "assistant",
      "content": "Respuesta final del agente describiendo la tarea completada"
    }
  ],
  "metadata": {
    "session_id": "...",
    "timestamp": "..."
  }
}
```

#### Hook Notification - Input (stdin)
```json
{
  "type": "notification",
  "message": "Mensaje de la notificación",
  "severity": "info|warning|error",
  "timestamp": "..."
}
```

#### Hook Output
Ambos hooks retornan exit code 0 (no bloquean ejecución)

### Script speak.py - CLI Interface

```bash
# Sintetizar y reproducir texto
speak.py --text "Mensaje a decir"

# Usar voz específica
speak.py --text "Mensaje" --voice "es-ES-Standard-B"

# Listar voces disponibles
speak.py --list-voices

# Output (stderr si error):
# Error: chatterbox no instalado. Ejecuta: pip install chatterbox
```

### Settings Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "enabled": {
      "type": "boolean",
      "default": true,
      "description": "Habilitar/deshabilitar notificaciones de voz"
    },
    "voice": {
      "type": "string",
      "default": "es-ES-Standard-A",
      "description": "Identificador de la voz de Chatterbox a usar"
    },
    "volume": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.8,
      "description": "Volumen de reproducción (0.0 - 1.0)"
    },
    "speed": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 2.0,
      "default": 1.0,
      "description": "Velocidad de habla (0.5 - 2.0)"
    }
  },
  "required": ["enabled"]
}
```

## Mensajes de Notificación

### Plantillas en Español

1. **Tarea completada**:
   - "La tarea ha sido completada: [descripción breve de 100 caracteres max]"
   - Ejemplo: "La tarea ha sido completada: Se crearon tres componentes de React y se actualizó el archivo de rutas"

2. **Requiere atención**:
   - "Claude necesita tu atención: [pregunta o contexto]"
   - Ejemplo: "Claude necesita tu atención: ¿Deseas continuar con la siguiente iteración del loop?"

3. **Error detectado**:
   - "Ha ocurrido un error: [tipo de error]"
   - Ejemplo: "Ha ocurrido un error: Fallo en la compilación de TypeScript"

### Reglas de Generación

- Máximo 150 caracteres por mensaje (para claridad y velocidad)
- Priorizar información accionable sobre detalles técnicos
- Usar lenguaje natural, no jerga de código
- En caso de errores, mencionar el tipo pero no stack traces

## Edge Cases

| Escenario | Comportamiento esperado |
|-----------|------------------------|
| Chatterbox no instalado | Hook log error a stderr, no reproducir audio, mostrar mensaje: "Voice notifications disabled: chatterbox not installed" |
| Settings.json corrupto | Usar valores default (enabled: true, voice: default), log warning |
| Settings.json no existe | Crear con valores default en primera ejecución |
| Mensaje vacío o null | No sintetizar, log debug "Skipping empty message" |
| Multiple hooks concurrentes | Cada hook ejecuta independientemente, pueden solaparse audios (aceptable) |
| Transcript sin mensajes | Skip notificación, no es error |
| Usuario mata proceso speak.py | Hook continúa (no blocking), audio se detiene |
| Sistema sin dispositivo de audio | speak.py falla gracefully, log error, hook retorna 0 |
| Mensaje > 500 caracteres | Truncar a 150 caracteres + "..." |
| Voz no disponible en Chatterbox | Fallback a voz default, log warning |

## Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación |
|----------|--------------------------|---------------|
| **Chatterbox TTS** | - Google TTS API<br>- Festival TTS<br>- pyttsx3<br>- ElevenLabs API | Chatterbox es open source, cross-platform, alta calidad de voz en español, no requiere API keys, según requerimiento del usuario |
| **Instalación manual de Chatterbox** | - Bundling en el plugin<br>- Auto-instalación con pip | Evita inflar el plugin, da control al usuario sobre dependencias de Python, sigue convención de plugins de Claude Code |
| **Bash para hooks** | - Python scripts directos<br>- Node.js scripts | Consistente con ejemplos del repo (ui-improve-loop), menor overhead, mejor integración con shell de Claude Code |
| **JSON para settings** | - YAML<br>- TOML<br>- .env | JSON es nativo en Claude Code plugins, no requiere parsers adicionales, fácil lectura con jq |
| **No bloquear hooks** | - Bloquear hasta que audio termine | Permite al agente continuar sin esperar, UX más fluida, usuario puede cancelar si es molesto |
| **Truncado de mensajes a 150 chars** | - Mensajes completos<br>- Resumen con LLM | Balance entre contexto y velocidad de síntesis, evita mensajes excesivamente largos |
| **No detector de errores en transcript** | - Parser sofisticado de errores | Simple pattern matching (grep "Error:", "Failed", etc.), suficiente para MVP, extensible más adelante |
| **Settings locales (no globales)** | - Configuración global en ~/.claude | Permite configuraciones por proyecto, consistente con `.claude/` del repo |

## Riesgos y consideraciones

### Riesgos Técnicos

1. **Dependencia externa (Chatterbox TTS)**
   - **Riesgo**: Si Chatterbox cambia su API o deja de mantenerse, el plugin puede romperse
   - **Mitigación**: 
     - Documentar versión específica de Chatterbox en README
     - Proveer fallback a síntesis básica (pyttsx3 como backup)
     - Testear con versión pinned: `chatterbox==1.0.0` (actualizar según versión estable)

2. **Performance en mensajes largos**
   - **Riesgo**: Transcripts muy largos pueden causar latencia en el hook
   - **Mitigación**: 
     - Truncado a 150 caracteres en bash antes de llamar speak.py
     - Timeout de 5 segundos en speak.py
     - Ejecutar speak.py en background (`&`) para no bloquear

3. **Cross-platform audio issues**
   - **Riesgo**: Diferentes sistemas operativos tienen distintos backends de audio
   - **Mitigación**: 
     - Chatterbox maneja esto internamente
     - Documentar requisitos por OS en README (ej: Linux puede necesitar `libsndfile`)
     - Testear en macOS, Linux, Windows

4. **Parsing de JSON en bash**
   - **Riesgo**: jq no disponible en el sistema
   - **Mitigación**: 
     - Incluir verificación de jq en hooks (`command -v jq`)
     - Si no existe, fallback a parsing básico con sed/awk (menos robusto pero funcional)
     - Documentar jq como dependencia

5. **Hooks concurrentes solapados**
   - **Riesgo**: Si Stop y Notification ocurren simultáneamente, audios se solapan
   - **Mitigación**: 
     - Aceptable para MVP (raro escenario)
     - Futuro: implementar cola de mensajes con lockfile

### Consideraciones de UX

1. **Accesibilidad**: 
   - El plugin beneficia usuarios con discapacidad visual
   - Considerar agregar soporte para subtítulos/transcripts en futuras versiones

2. **Interrupciones**: 
   - Notificaciones de voz pueden ser disruptivas en entornos compartidos
   - Solución: settings on/off fáciles de cambiar con `/voice-notifications:config --disable`

3. **Personalización de voces**: 
   - Usuarios pueden preferir diferentes voces (género, acento)
   - Comando `/voice-notifications:config --list-voices` debe mostrar opciones claras

4. **Volumen y velocidad**:
   - Valores default (0.8 volumen, 1.0 velocidad) pueden no ser ideales para todos
   - Settings permiten ajuste fino

### Consideraciones de Seguridad

1. **Inyección en mensajes**:
   - **Riesgo**: Si transcript contiene caracteres especiales, pueden romper el comando bash
   - **Mitigación**: 
     - Sanitizar input en bash antes de pasar a speak.py
     - Usar comillas apropiadas y escapar caracteres especiales
     - Validar longitud de mensajes

2. **Path traversal en CLAUDE_PLUGIN_ROOT**:
   - **Riesgo**: Variable puede ser manipulada
   - **Mitigación**: Claude Code provee esta variable de manera segura, confiar en el runtime

## Archivos a crear

### Estructura del plugin

```
plugins/voice-notifications/
├── .claude-plugin/
│   ├── plugin.json          # Metadata del plugin
│   └── settings.json        # Configuración del usuario (creado en instalación)
├── hooks/
│   ├── hooks.json           # Registro de hooks Stop y Notification
│   ├── stop-hook.sh         # Hook para tareas completadas
│   └── notification-hook.sh # Hook para notificaciones
├── scripts/
│   ├── speak.py             # Script Python para Chatterbox TTS
│   └── init-settings.sh     # Script para crear settings.json con defaults
├── commands/
│   └── config.md            # Comando para configurar el plugin
├── README.md                # Documentación de instalación y uso
├── SPEC.md                  # Este documento
└── CLAUDE.md                # Guía para Claude Code al trabajar con el plugin
```

### Contenido de cada archivo

#### 1. `plugins/voice-notifications/.claude-plugin/plugin.json`
Metadata estándar del plugin (ver sección Componente 6)

#### 2. `plugins/voice-notifications/.claude-plugin/settings.json`
Archivo de configuración inicial con defaults (ver Settings Schema)

#### 3. `plugins/voice-notifications/hooks/hooks.json`
Registro de hooks Stop y Notification (ver sección Componente 5)

#### 4. `plugins/voice-notifications/hooks/stop-hook.sh`
- Parsear stdin (transcript JSON)
- Verificar `enabled` en settings
- Extraer último mensaje del assistant
- Truncar a 150 caracteres
- Generar mensaje: "La tarea ha sido completada: [descripción]"
- Invocar `speak.py --text "$mensaje"` en background
- Exit 0

#### 5. `plugins/voice-notifications/hooks/notification-hook.sh`
- Parsear stdin (evento JSON)
- Verificar `enabled` en settings
- Extraer campo `message`
- Generar mensaje: "Claude necesita tu atención: [mensaje]"
- Invocar `speak.py --text "$mensaje"` en background
- Exit 0

#### 6. `plugins/voice-notifications/scripts/speak.py`
Funcionalidades:
- Argparse para `--text`, `--voice`, `--list-voices`
- Cargar settings.json para obtener voz/volumen/velocidad configurados
- Verificar instalación de chatterbox (try/except import)
- Inicializar engine de Chatterbox
- Sintetizar texto
- Reproducir audio
- Manejo de errores con mensajes claros

```python
#!/usr/bin/env python3
# Pseudocódigo:
import argparse
import json
import sys

try:
    import chatterbox
except ImportError:
    print("Error: chatterbox not installed. Run: pip install chatterbox", file=sys.stderr)
    sys.exit(1)

def load_settings():
    # Leer .claude-plugin/settings.json
    # Retornar dict con voice, volume, speed

def list_voices():
    # Usar API de Chatterbox para listar voces
    # Imprimir lista formateada

def speak(text, voice=None):
    settings = load_settings()
    voice = voice or settings.get("voice", "es-ES-Standard-A")
    volume = settings.get("volume", 0.8)
    speed = settings.get("speed", 1.0)
    
    # Inicializar Chatterbox
    # Cargar voz
    # Sintetizar texto con volume/speed
    # Reproducir audio

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--voice", help="Voice to use")
    parser.add_argument("--list-voices", action="store_true")
    
    args = parser.parse_args()
    
    if args.list_voices:
        list_voices()
    elif args.text:
        speak(args.text, args.voice)
    else:
        parser.print_help()
```

#### 7. `plugins/voice-notifications/scripts/init-settings.sh`
- Verificar si `.claude-plugin/settings.json` existe
- Si no, crear con defaults
- Usado en primera instalación

#### 8. `plugins/voice-notifications/commands/config.md`
Comando markdown con:
- Frontmatter: name, description, argument-hint, allowed-tools
- Instrucciones para el agente sobre cómo modificar settings.json
- Validaciones de valores (enabled: bool, voice: string, volume: 0-1, speed: 0.5-2.0)

#### 9. `plugins/voice-notifications/README.md`
Documentación completa:
- Descripción del plugin
- Características
- Instalación (pip install chatterbox, /plugin install voice-notifications)
- Requisitos (Python 3.8+, Chatterbox TTS)
- Uso (/voice-notifications:config)
- Configuración (settings.json)
- Ejemplos
- Troubleshooting (Chatterbox no instalado, sin audio, etc.)
- Licencia

#### 10. `plugins/voice-notifications/CLAUDE.md`
Guía para Claude Code:
- Overview del plugin
- Arquitectura de hooks
- Componentes principales
- Flujo de ejecución
- Convenciones de código
- Testing (manual)

## Requisitos de Instalación (README)

### Dependencias del Sistema

**Python 3.8+**
```bash
python3 --version
```

**jq** (para parsing JSON en bash)
```bash
# macOS
brew install jq

# Linux (Ubuntu/Debian)
sudo apt install jq

# Windows (Git Bash)
# Incluido en Git for Windows
```

### Dependencias de Python

**Chatterbox TTS**
```bash
pip install chatterbox
```

Nota: Chatterbox puede requerir dependencias adicionales según el sistema operativo:
- **Linux**: `sudo apt install libsndfile1`
- **macOS**: Incluido
- **Windows**: Puede requerir VC++ Redistributable

### Instalación del Plugin

```bash
# Agregar marketplace (si no está agregado)
/plugin marketplace add jvelez79/claude-code-plugins

# Instalar plugin
/plugin install voice-notifications

# Verificar instalación
/voice-notifications:config --list-voices
```

### Configuración Inicial

```bash
# Habilitar notificaciones de voz
/voice-notifications:config --enable

# Seleccionar voz (opcional)
/voice-notifications:config --voice "es-ES-Standard-B"

# Deshabilitar si es necesario
/voice-notifications:config --disable
```

## Plan de Testing

### Testing Manual

1. **Test Hook Stop**:
   - Ejecutar tarea simple en Claude Code (ej: crear archivo)
   - Verificar que al completar se escucha: "La tarea ha sido completada: [descripción]"
   
2. **Test Hook Notification**:
   - Escenario que requiera input del usuario
   - Verificar audio: "Claude necesita tu atención: [mensaje]"

3. **Test Configuración**:
   - Deshabilitar: `/voice-notifications:config --disable`
   - Ejecutar tarea, no debe haber audio
   - Habilitar: `/voice-notifications:config --enable`
   - Ejecutar tarea, debe haber audio

4. **Test Voces**:
   - Listar voces: `/voice-notifications:config --list-voices`
   - Cambiar voz: `/voice-notifications:config --voice "otra-voz"`
   - Verificar que la nueva voz se usa

5. **Test Edge Cases**:
   - Mensaje muy largo (>500 chars) → debe truncar
   - Sin Chatterbox instalado → debe mostrar error pero no romper Claude Code
   - Settings.json corrupto → debe usar defaults

### Métricas de Éxito

- Hook ejecuta en < 200ms (sin audio)
- Audio comienza a reproducirse en < 2 segundos desde el trigger
- No bloquea ejecución de Claude Code
- Graceful degradation si Chatterbox no está disponible

## Futuras Extensiones

1. **Cola de mensajes**: Evitar solapamiento de audios
2. **Notificaciones visuales**: Fallback a notificaciones del sistema
3. **Soporte multiidioma**: Detectar idioma del mensaje y usar voz apropiada
4. **Transcripts guardados**: Opción de guardar transcripts de audio en `.claude/voice-logs/`
5. **Integración con notificaciones del OS**: Usar sistema de notificaciones nativo además de audio
6. **Detección inteligente de errores**: Usar LLM para clasificar severidad de errores
7. **Custom triggers**: Permitir al usuario definir patrones custom para triggers adicionales

## Referencias

- Chatterbox TTS: https://github.com/resemble-ai/chatterbox
- Claude Code Plugin API: (documentación oficial de Anthropic)
- Ejemplo de hooks: `plugins/ui-improve-loop/hooks/stop-hook.sh`
- Ejemplo de plugin structure: `plugins/dev-workflow/`
