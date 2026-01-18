# Voice Notifications Plugin - Guía para Claude Code

Esta guía explica cómo funciona el plugin voice-notifications internamente, para facilitar el debugging, extensiones y colaboración.

## Overview

El plugin voice-notifications intercepta eventos del ciclo de vida del agente Claude Code (Stop, Notification) para generar notificaciones de voz contextuales en español usando múltiples motores TTS.

**Objetivo**: Permitir al usuario trabajar sin monitorear visualmente la terminal, recibiendo feedback auditivo sobre el estado de las tareas.

**Motores TTS disponibles**:
- **System TTS**: macOS `say` / Linux `espeak` - latencia <100ms
- **Chatterbox-Turbo**: Neural TTS de alta calidad - latencia ~300-500ms después de carga inicial

## Arquitectura

### Flujo de ejecución

```
1. Usuario ejecuta tarea en Claude Code
   ↓
2. Claude Code procesa la tarea
   ↓
3. Al terminar, Claude Code dispara hook "Stop"
   ↓
4. stop-hook.sh recibe transcript vía stdin
   ↓
5. stop-hook.sh verifica settings.json (enabled?)
   ↓
6. stop-hook.sh extrae contexto del transcript
   ↓
7. stop-hook.sh genera mensaje español
   ↓
8. stop-hook.sh invoca speak.py en background
   ↓
9. speak.py carga settings (tts_engine, voz, rate, chatterbox config)
   ↓
10. speak.py ejecuta factory get_tts_engine()
    ↓
┌───────────────────────────────────────────────┐
│ Decision Engine                               │
│ ├─ tts_engine == "chatterbox"                 │
│ │   ├─ Lazy load model (solo primera vez)     │
│ │   ├─ Detect device (MPS/CUDA/CPU)           │
│ │   ├─ Generate audio con Chatterbox-Turbo    │
│ │   ├─ Play audio con sounddevice             │
│ │   └─ Si falla → Fallback a SystemTTS        │
│ └─ tts_engine == "system"                     │
│     └─ Ejecuta say/espeak (instantáneo)       │
└───────────────────────────────────────────────┘
    ↓
11. Audio se reproduce
    ↓
12. Hooks retornan exit 0 (no bloquean Claude Code)
```

### Componentes

#### 1. Hooks (Bash)

**stop-hook.sh**:
- Responsabilidad: Interceptar fin de sesión del agente
- Input: JSON con transcript vía stdin
- Output: Exit code 0 (siempre)
- Funciones clave:
  - `is_enabled()`: Verifica si plugin está habilitado
  - `extract_task_description()`: Extrae último mensaje del assistant
  - `detect_error()`: Busca patrones de error en transcript
  - `sanitize_text()`: Previene inyección de código

**notification-hook.sh**:
- Responsabilidad: Interceptar notificaciones del sistema
- Input: JSON con evento de notificación vía stdin
- Output: Exit code 0 (siempre)
- Funciones clave:
  - `is_enabled()`: Verifica si plugin está habilitado
  - `extract_notification_message()`: Extrae mensaje del evento
  - `sanitize_text()`: Previene inyección de código

**Patrones importantes**:
- Siempre retornan `exit 0` para no bloquear Claude Code
- Ejecutan `speak.py` en background con `nohup`
- Tienen fallback si `jq` no está disponible
- Sanitizan inputs antes de pasar a `speak.py`
- Logs a stderr con prefijo `[voice-notifications:*]`

#### 2. Script TTS (Python)

**speak.py**:
- Responsabilidad: Interfaz unificada para múltiples motores TTS
- Arquitectura:
  - `TTSEngine` (ABC): Clase base abstracta
  - `SystemTTS(TTSEngine)`: Implementación para TTS sistema (say/espeak)
  - `ChatterboxTurboTTS(TTSEngine)`: Implementación para Chatterbox-Turbo
  - `get_tts_engine(settings)`: Factory function que retorna el engine apropiado
- CLI Interface:
  ```bash
  speak.py --text "Mensaje"               # Sintetizar y reproducir
  speak.py --text "Mensaje" --voice Jorge # Con voz específica (solo SystemTTS)
  speak.py --rate 180                     # Ajustar velocidad (solo SystemTTS)
  speak.py --list-voices                  # Listar voces disponibles (varía según engine)
  ```
- Funciones clave:
  - `load_settings()`: Lee settings.json, merge con defaults para retrocompatibilidad
  - `get_tts_engine()`: Factory que retorna SystemTTS o ChatterboxTurboTTS
  - `SystemTTS.speak()`: Ejecuta comando TTS del sistema
  - `ChatterboxTurboTTS._load_model()`: Lazy loading del modelo (solo primera vez)
  - `ChatterboxTurboTTS._detect_device()`: Detecta MPS/CUDA/CPU
  - `ChatterboxTurboTTS._play_audio()`: Reproduce audio con sounddevice
- Manejo de errores:
  - Si `say`/`espeak` no disponible → print a stderr, exit 1
  - Si Chatterbox no instalado y `fallback_to_system=true` → usa SystemTTS
  - Si Chatterbox no instalado y `fallback_to_system=false` → exit 1
  - Si mensaje vacío → skip silenciosamente

#### 3. Configuración

**settings.json**:
```json
{
  "enabled": true,
  "tts_engine": "system",
  "voice": "Jorge",
  "rate": 200,
  "chatterbox": {
    "device": "mps",
    "voice_sample": null,
    "exaggeration": 1.0
  },
  "fallback_to_system": true
}
```

- Ubicación: `.claude-plugin/settings.json`
- Schema validado por comando config.md
- Creado automáticamente con defaults si no existe
- Retrocompatibilidad: Settings sin `tts_engine` funcionan (default a "system")

**Campos nuevos (vs versión anterior)**:
- `tts_engine`: "system" o "chatterbox"
- `chatterbox`: Configuración específica de Chatterbox-Turbo
  - `device`: "mps", "cpu", o "cuda"
  - `voice_sample`: Path a audio de referencia (opcional)
  - `exaggeration`: Nivel de expresividad (0.0-2.0)
- `fallback_to_system`: Boolean, usar TTS sistema si Chatterbox falla

**Voces españolas disponibles**:

System TTS (macOS):
| Voz | Región | Tipo |
|-----|--------|------|
| Jorge | España | Masculina |
| Mónica | España | Femenina |
| Paulina | México | Femenina |
| Juan | México | Masculina |

Chatterbox-Turbo:
- Voz default del modelo (sin configuración)
- Voice cloning con audio de referencia (avanzado)

**hooks.json**:
```json
{
  "hooks": {
    "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"}]}],
    "Notification": [{"matcher": "", "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/notification-hook.sh"}]}]
  }
}
```

- Ubicación: `hooks/hooks.json`
- Registra hooks con Claude Code
- Usa `${CLAUDE_PLUGIN_ROOT}` para paths relativos

#### 4. Comando de Configuración

**config.md**:
- Tipo: Comando markdown con frontmatter
- Allowed tools: Read, Write, Bash
- Responsabilidades:
  - Leer/escribir settings.json
  - Validar valores antes de escribir
  - Ejecutar `speak.py --list-voices`
- Validaciones:
  - `enabled`: boolean
  - `voice`: string no vacía (Jorge, Paulina, Juan, Mónica)
  - `rate`: number 80-300 (palabras por minuto)

## Contratos

### Hook Stop - Input (stdin)

```json
{
  "transcript": [
    {"role": "user", "content": "Instrucción del usuario"},
    {"role": "assistant", "content": "Respuesta final del agente"}
  ],
  "metadata": {
    "session_id": "...",
    "timestamp": "..."
  }
}
```

### Hook Notification - Input (stdin)

```json
{
  "type": "notification",
  "message": "Mensaje de la notificación",
  "severity": "info|warning|error",
  "timestamp": "..."
}
```

### speak.py CLI

```bash
# Success: exit 0, audio se reproduce instantáneamente
# Error: exit 1, mensaje a stderr

# Ejemplos:
speak.py --text "La tarea ha sido completada"
speak.py --text "Claude necesita tu atención" --voice Paulina
speak.py --text "Error detectado" --rate 180
speak.py --list-voices
```

## Mensajes de Notificación

### Plantillas

1. **Tarea completada**:
   ```
   "La tarea ha sido completada: [descripción breve max 150 chars]"
   ```

2. **Requiere atención**:
   ```
   "Claude necesita tu atención: [contexto]"
   ```

3. **Error detectado**:
   ```
   "Ha ocurrido un error: [tipo de error]"
   ```

### Reglas

- Máximo 150 caracteres por mensaje (claridad y velocidad)
- Truncado a 500 caracteres en caso de overflow (seguridad)
- Lenguaje natural, no jerga de código
- Sanitización de caracteres especiales

## Edge Cases y Comportamiento

| Escenario | Comportamiento |
|-----------|----------------|
| macOS sin voz instalada | say usa voz default del sistema |
| Linux sin espeak | speak.py print error a stderr, exit 1 |
| Settings.json corrupto | speak.py usa defaults, log warning |
| Settings.json no existe | speak.py usa defaults, log warning |
| Settings.json sin campos nuevos | Merge con defaults, retrocompatibilidad preservada |
| Mensaje vacío | speak.py skip silenciosamente |
| Múltiples hooks concurrentes | Ejecutan independientemente, audios pueden solaparse |
| Transcript sin mensajes | Hook skip, exit 0 |
| Mensaje > 500 chars | Truncado a 150 chars + "..." |
| Voz no disponible | say usa default, log warning |
| jq no disponible | Hooks usan fallback con grep/sed |
| **Chatterbox no instalado + fallback=true** | Usa SystemTTS automáticamente, log a stderr |
| **Chatterbox no instalado + fallback=false** | Error a stderr, exit 1 |
| **Primera carga de Chatterbox** | Latencia 2-3s (lazy loading), log a stderr |
| **Ejecuciones subsiguientes Chatterbox** | Modelo reutilizado, latencia ~300-500ms |
| **MPS no disponible (device=mps)** | Auto-detect, fallback a CPU, log warning |
| **sounddevice no instalado** | ImportError, mensaje sugiere instalación |
| **Memoria insuficiente para modelo** | RuntimeError, fallback a SystemTTS si enabled |
| **device=cuda pero no hay GPU** | Auto-detect, fallback a CPU o MPS |
| **voice_sample path inválido** | Ignora voice cloning, usa voz default |

## Convenciones de código

### Bash

- Usar `set -euo pipefail` al inicio
- Funciones descriptivas (`extract_task_description`, no `get_desc`)
- Logs a stderr con prefijo: `debug_log "[voice-notifications:stop] mensaje"`
- Siempre `exit 0` al final de hooks
- Sanitizar inputs con `sanitize_text()`
- Usar `${VARIABLE:-default}` para variables con fallback
- Verificar comandos con `command -v cmd &> /dev/null`

### Python

- Shebang: `#!/usr/bin/env python3`
- Docstrings en funciones públicas
- Print errores a stderr: `print("Error...", file=sys.stderr)`
- Exit codes: 0 success, 1 error
- Pathlib para manejo de paths
- Dependencias mínimas (solo stdlib)

### JSON

- Indentación: 2 espacios
- UTF-8 encoding
- Trailing commas no permitidas
- Schema validation en comando config.md

## Debugging

### Verificar instalación

```bash
# 1. Verificar estructura de archivos
ls -R plugins/voice-notifications/

# 2. Verificar permisos ejecutables
ls -l plugins/voice-notifications/hooks/*.sh
ls -l plugins/voice-notifications/scripts/*.py

# 3. Verificar voces españolas disponibles (macOS)
say -v '?' | grep es_

# 4. Verificar jq
command -v jq && echo "OK"

# 5. Probar speak.py manualmente con SystemTTS
cd plugins/voice-notifications
./scripts/speak.py --text "Prueba de voz"
./scripts/speak.py --list-voices

# 6. Verificar instalación de Chatterbox-Turbo (opcional)
python3 -c "from chatterbox.tts_turbo import ChatterboxTurboTTS; print('Chatterbox-Turbo: OK')"

# 6b. Si da error de token de HuggingFace, autenticarse:
pip install huggingface_hub
huggingface-cli login  # Crear token en https://huggingface.co/settings/tokens

# 7. Verificar PyTorch MPS (Apple Silicon)
python3 -c "import torch; print('MPS disponible:', torch.backends.mps.is_available())"

# 8. Verificar sounddevice
python3 -c "import sounddevice; print('sounddevice: OK')"

# 9. Probar speak.py con Chatterbox (si instalado)
# Primero configurar: /voice-notifications:config --engine chatterbox
./scripts/speak.py --text "Prueba con Chatterbox-Turbo"
```

### Simular hooks manualmente

```bash
# Test stop-hook.sh
echo '{"transcript":[{"role":"assistant","content":"Tarea completada exitosamente"}]}' | \
  CLAUDE_PLUGIN_ROOT=/path/to/plugins/voice-notifications \
  ./hooks/stop-hook.sh

# Test notification-hook.sh
echo '{"message":"Se requiere tu confirmación"}' | \
  CLAUDE_PLUGIN_ROOT=/path/to/plugins/voice-notifications \
  ./hooks/notification-hook.sh
```

### Ver logs

Los hooks escriben debug logs a stderr. Para verlos durante ejecución de Claude Code, monitorear stderr:

```bash
# Claude Code normalmente muestra stderr automáticamente
# O redirigir a archivo:
claude ... 2> debug.log
```

## Arquitectura Multi-Engine

### Patrón de diseño

El plugin usa **Strategy Pattern** con factory:

```python
# Clase base abstracta
class TTSEngine(ABC):
    @abstractmethod
    def speak(self, text: str, **kwargs) -> None:
        pass

    @abstractmethod
    def list_voices(self) -> None:
        pass

# Implementaciones concretas
class SystemTTS(TTSEngine):
    # Implementa speak() con say/espeak
    pass

class ChatterboxTurboTTS(TTSEngine):
    # Implementa speak() con Chatterbox-Turbo
    # Singleton para reutilizar modelo cargado
    pass

# Factory
def get_tts_engine(settings: dict) -> TTSEngine:
    if settings["tts_engine"] == "chatterbox":
        try:
            return ChatterboxTurboTTS(settings)
        except (ImportError, RuntimeError):
            if settings["fallback_to_system"]:
                return SystemTTS(settings)
            raise
    return SystemTTS(settings)
```

### Lazy Loading de modelo

ChatterboxTurboTTS usa **Singleton Pattern** para evitar cargar el modelo múltiples veces:

```python
class ChatterboxTurboTTS(TTSEngine):
    _instance = None
    _model = None  # Compartido entre todas las instancias

    def __new__(cls, settings):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:  # Solo cargar una vez
            self._model = ChatterboxTurboTTS.from_pretrained(device=...)
```

### Device Detection

Auto-detección de hardware con fallback chain:

```python
def _detect_device(self) -> str:
    if torch.backends.mps.is_available():
        return "mps"  # Apple Silicon
    elif torch.cuda.is_available():
        return "cuda"  # NVIDIA GPU
    return "cpu"  # Fallback universal
```

## Extensiones futuras

### Cola de mensajes

Para evitar solapamiento de audios, implementar lockfile:

```bash
# En hooks/*.sh, antes de invocar speak.py:
LOCKFILE="/tmp/voice-notifications.lock"
while [[ -f "$LOCKFILE" ]]; do
  sleep 0.1
done
echo $$ > "$LOCKFILE"
"$SPEAK_SCRIPT" --text "$message" &
rm "$LOCKFILE"
```

### Integración con notificaciones del OS

```bash
# En hooks, agregar fallback si speak.py falla:
if ! "$SPEAK_SCRIPT" --text "$message"; then
  # Fallback a notificación visual
  osascript -e "display notification \"$message\" with title \"Claude Code\""  # macOS
  # notify-send "$message"  # Linux
fi
```

### Triggers personalizables

Permitir al usuario definir patrones custom en settings.json:

```json
{
  "custom_triggers": [
    {
      "pattern": "test.*passed",
      "message": "Tests pasaron exitosamente"
    }
  ]
}
```

### Cacheo de audio

Para mensajes repetidos, cachear audio generado:

```python
# En ChatterboxTurboTTS
_audio_cache = {}  # {text: wav_array}

def speak(self, text: str):
    if text in self._audio_cache:
        wav = self._audio_cache[text]
    else:
        wav = self._model.generate(text)
        self._audio_cache[text] = wav
    self._play_audio(wav)
```

## Testing

### Manual tests

1. **Test básico**:
   - Ejecutar tarea simple en Claude Code
   - Verificar audio al completar (debe ser instantáneo)

2. **Test deshabilitado**:
   - `/voice-notifications:config --disable`
   - Ejecutar tarea, no debe sonar

3. **Test errores**:
   - Ejecutar tarea que cause error (ej: archivo no existe)
   - Verificar mensaje de error

4. **Test configuración**:
   - Cambiar voz, rate
   - Verificar que se apliquen los cambios

### Métricas

**SystemTTS**:
- Hook ejecuta en < 50ms
- Audio comienza en < 100ms desde trigger
- Sin dependencias externas

**ChatterboxTurboTTS**:
- Primera ejecución: 2-3s (carga de modelo)
- Ejecuciones subsiguientes: 300-500ms
- Uso de memoria: ~350MB (modelo cargado)
- Requiere: PyTorch, chatterbox, sounddevice

**Común**:
- No bloquea ejecución de Claude Code (background)
- Fallback robusto si Chatterbox falla

## Notas importantes para Claude

Al trabajar con este plugin:

1. **SIEMPRE** preservar la estructura de archivos
2. **NO** modificar hooks.json sin entender el contrato con Claude Code
3. **NO** eliminar sanitización de inputs (seguridad)
4. **NO** bloquear hooks (siempre background + exit 0)
5. **VALIDAR** inputs en comando config antes de escribir settings.json
6. **USAR** `${CLAUDE_PLUGIN_ROOT}` para paths en hooks.json
7. **MANTENER** mensajes en español natural
8. **PRESERVAR** compatibilidad con sistemas sin jq (fallbacks)
9. **TESTEAR** manualmente después de cambios
10. **RETROCOMPATIBILIDAD**: Settings sin campos nuevos deben funcionar
11. **FALLBACK**: Chatterbox-Turbo debe tener fallback a SystemTTS por defecto
12. **LAZY LOADING**: Modelo Chatterbox solo se carga en primera ejecución
13. **SINGLETON**: ChatterboxTurboTTS debe reutilizar instancia de modelo
14. **DEVICE AUTO-DETECT**: Si device configurado no disponible, auto-detectar
15. **LOGS CLAROS**: Siempre usar prefijo `[voice-notifications:speak]` en stderr

## Referencias

- README.md: Documentación de usuario
- Ejemplo de plugin: `../dev-workflow/`
- Ejemplo de hooks: `../ui-improve-loop/hooks/`
