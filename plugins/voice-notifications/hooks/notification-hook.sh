#!/bin/bash
#
# Voice Notifications - Notification Hook
# Intercepta notificaciones del sistema que requieren atención del usuario.
#

set -euo pipefail

# Configuración
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
SETTINGS_FILE="${PLUGIN_ROOT}/.claude-plugin/settings.json"
SPEAK_SCRIPT="${PLUGIN_ROOT}/scripts/speak.py"

# Función para log de debug
debug_log() {
    echo "[voice-notifications:notification] $1" >&2
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

# Función para extraer el mensaje de la notificación
extract_notification_message() {
    local event="$1"

    # Verificar si jq está disponible
    if ! command -v jq &> /dev/null; then
        debug_log "jq no disponible, usando fallback básico"
        # Fallback: extraer campo "message"
        echo "$event" | grep -oE '"message"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"message"[[:space:]]*:[[:space:]]*"//;s/"$//' | head -c 150
        return
    fi

    # Usar jq para parsear el JSON correctamente
    local message
    message=$(echo "$event" | jq -r '.message // ""' 2>/dev/null || echo "")

    if [[ -z "$message" || "$message" == "null" ]]; then
        debug_log "No se encontró mensaje en el evento de notificación"
        echo "notificación sin mensaje"
        return
    fi

    # Truncar a 150 caracteres
    echo "$message" | head -c 150
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

    # Leer evento desde stdin
    local event
    event=$(cat)

    if [[ -z "$event" ]]; then
        debug_log "Evento vacío, saliendo"
        exit 0
    fi

    # Extraer mensaje de la notificación
    local notification_message
    notification_message=$(extract_notification_message "$event")
    notification_message=$(sanitize_text "$notification_message")

    # Generar mensaje de voz
    local message="Claude necesita tu atención: ${notification_message}"

    # Truncar mensaje si es muy largo (seguridad adicional)
    message="${message:0:500}"

    debug_log "Notificación: ${notification_message:0:50}..."

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
