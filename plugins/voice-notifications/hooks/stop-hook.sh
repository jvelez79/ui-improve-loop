#!/bin/bash
#
# Voice Notifications - Stop Hook
# Intercepta el fin de sesión del agente y genera notificación de voz contextual.
#

set -euo pipefail

# Configuración
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
SETTINGS_FILE="${PLUGIN_ROOT}/.claude-plugin/settings.json"
SPEAK_SCRIPT="${PLUGIN_ROOT}/scripts/speak.py"

# Función para log de debug
debug_log() {
    echo "[voice-notifications:stop] $1" >&2
}

# Función para verificar si el plugin está habilitado
is_enabled() {
    if [[ ! -f "$SETTINGS_FILE" ]]; then
        debug_log "settings.json no encontrado, asumiendo habilitado"
        return 0
    fi

    # Verificar si jq está disponible
    if ! command -v jq &> /dev/null; then
        debug_log "jq no disponible, usando fallback con grep"
        # Fallback: buscar "enabled": true/false
        if grep -q '"enabled"[[:space:]]*:[[:space:]]*false' "$SETTINGS_FILE"; then
            return 1
        else
            return 0
        fi
    fi

    enabled=$(jq -r '.enabled // true' "$SETTINGS_FILE" 2>/dev/null || echo "true")
    [[ "$enabled" == "true" ]]
}

# Función para extraer el último mensaje del assistant del transcript
extract_task_description() {
    local transcript="$1"

    # Verificar si jq está disponible
    if ! command -v jq &> /dev/null; then
        debug_log "jq no disponible, usando fallback básico"
        # Fallback: extraer último contenido después de "assistant"
        echo "$transcript" | grep -oE '"content"[[:space:]]*:[[:space:]]*"[^"]*"' | tail -1 | sed 's/"content"[[:space:]]*:[[:space:]]*"//;s/"$//' | head -c 150
        return
    fi

    # Usar jq para parsear el JSON correctamente
    local description
    description=$(echo "$transcript" | jq -r '
        .transcript // [] |
        map(select(.role == "assistant")) |
        last |
        .content // ""
    ' 2>/dev/null || echo "")

    if [[ -z "$description" || "$description" == "null" ]]; then
        debug_log "No se encontró descripción de la tarea en el transcript"
        echo "tarea sin descripción"
        return
    fi

    # Truncar a 150 caracteres para mantener el mensaje conciso
    echo "$description" | head -c 150
}

# Función para detectar errores en el transcript
detect_error() {
    local transcript="$1"

    # Buscar patrones comunes de error
    if echo "$transcript" | grep -iqE '(error:|failed|exception|fatal|cannot|unable to|could not)'; then
        return 0  # Error detectado
    fi

    return 1  # No hay error
}

# Función para extraer tipo de error
extract_error_type() {
    local transcript="$1"

    # Intentar extraer el tipo de error
    local error_msg
    error_msg=$(echo "$transcript" | grep -ioE '(error:[^.]*|failed[^.]*|exception:[^.]*)' | head -1)

    if [[ -z "$error_msg" ]]; then
        echo "error desconocido"
    else
        echo "$error_msg" | head -c 100
    fi
}

# Función para sanitizar input (prevenir inyección)
sanitize_text() {
    local text="$1"
    # Remover caracteres especiales peligrosos y escapar comillas
    echo "$text" | tr -d '\n\r\t' | sed "s/'/'\\\\''/g; s/\"/\\\\\"/g"
}

# Main
main() {
    debug_log "Hook iniciado"

    # Verificar si el plugin está habilitado
    if ! is_enabled; then
        debug_log "Plugin deshabilitado, saliendo"
        exit 0
    fi

    # Leer transcript desde stdin
    local transcript
    transcript=$(cat)

    if [[ -z "$transcript" ]]; then
        debug_log "Transcript vacío, saliendo"
        exit 0
    fi

    # Generar mensaje según el contexto
    local message

    # Verificar si hay error
    if detect_error "$transcript"; then
        local error_type
        error_type=$(extract_error_type "$transcript")
        error_type=$(sanitize_text "$error_type")
        message="Ha ocurrido un error: ${error_type}"
        debug_log "Error detectado: $error_type"
    else
        # Tarea completada normalmente
        local task_description
        task_description=$(extract_task_description "$transcript")
        task_description=$(sanitize_text "$task_description")
        message="La tarea ha sido completada: ${task_description}"
        debug_log "Tarea completada: ${task_description:0:50}..."
    fi

    # Truncar mensaje si es muy largo (seguridad adicional)
    message="${message:0:500}"

    # Invocar speak.py en background para no bloquear
    if [[ -x "$SPEAK_SCRIPT" ]]; then
        debug_log "Invocando speak.py en background"
        "$SPEAK_SCRIPT" --text "$message" &
        # Obtener PID del proceso background
        local speak_pid=$!
        debug_log "speak.py iniciado con PID $speak_pid"
    else
        debug_log "Error: speak.py no encontrado o no ejecutable en $SPEAK_SCRIPT"
    fi

    # Siempre retornar 0 para no bloquear Claude Code
    exit 0
}

# Ejecutar main
main
