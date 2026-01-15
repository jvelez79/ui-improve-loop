# Voice Notifications Plugin - Guía para Claude Code

Esta guía explica cómo funciona el plugin voice-notifications internamente, para facilitar el debugging, extensiones y colaboración.

## Overview

El plugin voice-notifications intercepta eventos del ciclo de vida del agente Claude Code (Stop, Notification) para generar notificaciones de voz contextuales en español usando Chatterbox TTS.

**Objetivo**: Permitir al usuario trabajar sin monitorear visualmente la terminal, recibiendo feedback auditivo sobre el estado de las tareas.

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
9. speak.py carga settings (voz, volumen, velocidad)
   ↓
10. speak.py usa Chatterbox TTS para sintetizar
    ↓
11. Audio se reproduce en el sistema
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
- Ejecutan `speak.py` en background con `&`
- Tienen fallback si `jq` no está disponible
- Sanitizan inputs antes de pasar a `speak.py`
- Logs a stderr con prefijo `[voice-notifications:*]`

#### 2. Script TTS (Python)

**speak.py**:
- Responsabilidad: Interfaz con Chatterbox TTS
- CLI Interface:
  ```bash
  speak.py --text "Mensaje"               # Sintetizar y reproducir
  speak.py --text "Mensaje" --voice "voz" # Con voz específica
  speak.py --list-voices                  # Listar voces
  ```
- Funciones clave:
  - `load_settings()`: Lee settings.json, retorna defaults si falla
  - `list_voices()`: Lista voces disponibles en Chatterbox
  - `speak()`: Sintetiza y reproduce texto
- Manejo de errores:
  - Si Chatterbox no instalado → print a stderr, exit 1
  - Si audio device no disponible → print a stderr, exit 1
  - Si mensaje vacío → skip silenciosamente

#### 3. Configuración

**settings.json**:
```json
{
  "enabled": true,
  "voice": "es-ES-Standard-A",
  "volume": 0.8,
  "speed": 1.0
}
```

- Ubicación: `.claude-plugin/settings.json`
- Schema validado por comando config.md
- Creado automáticamente con defaults si no existe

**hooks.json**:
```json
{
  "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"}]}],
  "Notification": [{"matcher": "", "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/notification-hook.sh"}]}]
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
  - `voice`: string no vacía
  - `volume`: number 0.0-1.0
  - `speed`: number 0.5-2.0

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
# Success: exit 0, audio se reproduce
# Error: exit 1, mensaje a stderr

# Ejemplos:
speak.py --text "La tarea ha sido completada"
speak.py --text "Claude necesita tu atención" --voice "es-ES-Standard-B"
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
| Chatterbox no instalado | speak.py print error a stderr, exit 1. Hook continúa, no bloquea |
| Settings.json corrupto | speak.py usa defaults, log warning |
| Settings.json no existe | speak.py usa defaults, log warning |
| Mensaje vacío | speak.py skip silenciosamente |
| Múltiples hooks concurrentes | Ejecutan independientemente, audios pueden solaparse (aceptable) |
| Transcript sin mensajes | Hook skip, exit 0 |
| Sistema sin audio device | speak.py falla, log error, hook exit 0 |
| Mensaje > 500 chars | Truncado a 150 chars + "..." |
| Voz no disponible | speak.py usa default, log warning |
| jq no disponible | Hooks usan fallback con grep/sed |

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
- Try/except para imports de dependencias externas
- Print errores a stderr: `print("Error...", file=sys.stderr)`
- Exit codes: 0 success, 1 error
- Pathlib para manejo de paths
- Type hints opcionales pero recomendados

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

# 3. Verificar Chatterbox
python3 -c "import chatterbox; print('OK')"

# 4. Verificar jq
command -v jq && echo "OK"

# 5. Probar speak.py manualmente
cd plugins/voice-notifications
./scripts/speak.py --text "Prueba de voz"
./scripts/speak.py --list-voices
```

### Simular hooks manualmente

```bash
# Test stop-hook.sh
echo '{"transcript":[{"role":"assistant","content":"Tarea completada exitosamente"}]}' | \
  CLAUDE_PLUGIN_ROOT=/Users/juanca/Projects/ui-improve-loop/plugins/voice-notifications \
  ./hooks/stop-hook.sh

# Test notification-hook.sh
echo '{"message":"Se requiere tu confirmación"}' | \
  CLAUDE_PLUGIN_ROOT=/Users/juanca/Projects/ui-improve-loop/plugins/voice-notifications \
  ./hooks/notification-hook.sh
```

### Ver logs

Los hooks escriben debug logs a stderr. Para verlos durante ejecución de Claude Code, monitorear stderr:

```bash
# Claude Code normalmente muestra stderr automáticamente
# O redirigir a archivo:
claude ... 2> debug.log
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

## Testing

### Manual tests

1. **Test básico**:
   - Ejecutar tarea simple en Claude Code
   - Verificar audio al completar

2. **Test deshabilitado**:
   - `/voice-notifications:config --disable`
   - Ejecutar tarea, no debe sonar

3. **Test errores**:
   - Ejecutar tarea que cause error (ej: archivo no existe)
   - Verificar mensaje de error

4. **Test configuración**:
   - Cambiar voz, volumen, velocidad
   - Verificar que se apliquen los cambios

### Métricas

- Hook ejecuta en < 200ms (sin contar audio)
- Audio comienza en < 2 segundos desde trigger
- No bloquea ejecución de Claude Code
- Graceful degradation sin Chatterbox

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

## Referencias

- SPEC.md: Especificación técnica completa
- README.md: Documentación de usuario
- Ejemplo de plugin: `../dev-workflow/`
- Ejemplo de hooks: `../ui-improve-loop/hooks/`
