#!/bin/bash
#
# Voice Notifications - Init Settings
# Crea el archivo settings.json con valores default si no existe.
#

set -euo pipefail

# Configuración
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SETTINGS_DIR="${PLUGIN_ROOT}/.claude-plugin"
SETTINGS_FILE="${SETTINGS_DIR}/settings.json"

# Valores default
DEFAULT_SETTINGS='{
  "enabled": true,
  "voice": "es-ES-Standard-A",
  "volume": 0.8,
  "speed": 1.0
}'

# Main
main() {
    # Verificar si el directorio .claude-plugin existe
    if [[ ! -d "$SETTINGS_DIR" ]]; then
        echo "Creando directorio .claude-plugin..."
        mkdir -p "$SETTINGS_DIR"
    fi

    # Verificar si settings.json ya existe
    if [[ -f "$SETTINGS_FILE" ]]; then
        echo "settings.json ya existe, no se sobrescribirá."
        echo "Configuración actual:"
        cat "$SETTINGS_FILE"
        exit 0
    fi

    # Crear settings.json con valores default
    echo "Creando settings.json con valores default..."
    echo "$DEFAULT_SETTINGS" > "$SETTINGS_FILE"

    echo "settings.json creado exitosamente en: $SETTINGS_FILE"
    echo "Contenido:"
    cat "$SETTINGS_FILE"

    echo ""
    echo "Usa /voice-notifications:config para modificar la configuración."
}

# Ejecutar main
main
