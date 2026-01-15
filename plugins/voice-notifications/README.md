# Voice Notifications Plugin

Plugin de Claude Code que proporciona notificaciones de voz contextuales en español usando Chatterbox TTS. El plugin intercepta eventos del ciclo de vida del agente para informar al usuario sobre el estado de las tareas sin necesidad de monitorear visualmente la terminal.

## Características

- Notificaciones de voz al completar tareas
- Alertas cuando Claude necesita atención del usuario
- Detección automática de errores con mensajes contextuales
- Configuración flexible (habilitar/deshabilitar, cambiar voz, ajustar volumen y velocidad)
- Mensajes en español naturales y concisos
- Ejecución no bloqueante (background)

## Requisitos

### Sistema

- **Python 3.8+**
  ```bash
  python3 --version
  ```

- **jq** (para parsing JSON en bash)
  ```bash
  # macOS
  brew install jq

  # Linux (Ubuntu/Debian)
  sudo apt install jq

  # Windows (Git Bash)
  # Incluido en Git for Windows
  ```

### Python

- **Chatterbox TTS** (Resemble AI)
  ```bash
  pip install chatterbox
  ```

  Dependencias adicionales según el sistema operativo:
  - **Linux**: `sudo apt install libsndfile1`
  - **macOS**: Incluidas por defecto
  - **Windows**: Puede requerir VC++ Redistributable

## Instalación

### 1. Agregar el marketplace (si no está agregado)

```bash
/plugin marketplace add jvelez79/claude-code-plugins
```

### 2. Instalar el plugin

```bash
/plugin install voice-notifications
```

### 3. Verificar instalación

```bash
/voice-notifications:config --list-voices
```

Si ves una lista de voces disponibles, la instalación fue exitosa.

## Uso

### Configuración básica

```bash
# Ver configuración actual
/voice-notifications:config

# Habilitar notificaciones de voz
/voice-notifications:config --enable

# Deshabilitar notificaciones de voz
/voice-notifications:config --disable

# Listar voces disponibles
/voice-notifications:config --list-voices

# Cambiar voz
/voice-notifications:config --voice "es-ES-Standard-B"

# Ajustar volumen (0.0 a 1.0)
/voice-notifications:config --volume 0.6

# Ajustar velocidad de habla (0.5 a 2.0)
/voice-notifications:config --speed 1.2

# Configurar múltiples opciones a la vez
/voice-notifications:config --voice "es-MX-Standard-A" --volume 0.7 --speed 1.1
```

### Funcionamiento automático

Una vez instalado y habilitado, el plugin funciona automáticamente:

1. **Tareas completadas**: Cuando Claude termina una tarea, escucharás:
   > "La tarea ha sido completada: [descripción breve]"

2. **Requiere atención**: Cuando Claude necesita tu input:
   > "Claude necesita tu atención: [pregunta o contexto]"

3. **Errores detectados**: Cuando ocurre un error:
   > "Ha ocurrido un error: [tipo de error]"

## Configuración avanzada

El archivo de configuración se encuentra en:
```
plugins/voice-notifications/.claude-plugin/settings.json
```

Estructura:
```json
{
  "enabled": true,
  "voice": "es-ES-Standard-A",
  "volume": 0.8,
  "speed": 1.0
}
```

Campos:
- **enabled** (boolean): Habilitar/deshabilitar el plugin
- **voice** (string): Identificador de voz de Chatterbox
- **volume** (number 0.0-1.0): Volumen de reproducción
- **speed** (number 0.5-2.0): Velocidad de habla

## Voces disponibles

El plugin soporta las siguientes voces en español (según disponibilidad en Chatterbox):

### España (es-ES)
- `es-ES-Standard-A` (Femenina) - **Default**
- `es-ES-Standard-B` (Masculina)
- `es-ES-Standard-C` (Femenina)
- `es-ES-Standard-D` (Femenina)
- `es-ES-Wavenet-A` (Femenina, alta calidad)
- `es-ES-Wavenet-B` (Masculina, alta calidad)
- `es-ES-Wavenet-C` (Femenina, alta calidad)
- `es-ES-Wavenet-D` (Femenina, alta calidad)

### México (es-MX)
- `es-MX-Standard-A` (Femenina)
- `es-MX-Standard-B` (Masculina)
- `es-MX-Wavenet-A` (Femenina, alta calidad)
- `es-MX-Wavenet-B` (Masculina, alta calidad)

### Estados Unidos (es-US)
- `es-US-Standard-A` (Femenina)
- `es-US-Standard-B` (Masculina)
- `es-US-Wavenet-A` (Femenina, alta calidad)
- `es-US-Wavenet-B` (Masculina, alta calidad)

Nota: Las voces Wavenet ofrecen mayor calidad pero pueden requerir más recursos.

## Troubleshooting

### Chatterbox no instalado

**Error**: `Error: chatterbox no instalado. Ejecuta: pip install chatterbox`

**Solución**:
```bash
pip install chatterbox
```

### Sin dispositivo de audio

**Error**: `Error: Sistema sin dispositivo de audio o driver no disponible`

**Solución**:
- Verificar que tu sistema tenga un dispositivo de audio configurado
- En Linux, puede ser necesario instalar: `sudo apt install pulseaudio`
- Verificar que el volumen del sistema no esté en mudo

### jq no disponible

**Warning**: `jq no disponible, usando fallback con grep`

**Solución** (opcional, el plugin funciona sin jq pero menos robustamente):
```bash
# macOS
brew install jq

# Linux
sudo apt install jq
```

### Notificaciones no suenan

1. Verificar que el plugin esté habilitado:
   ```bash
   /voice-notifications:config
   ```

2. Verificar que Chatterbox esté instalado:
   ```bash
   python3 -c "import chatterbox; print('OK')"
   ```

3. Verificar logs en stderr al ejecutar tareas en Claude Code

4. Probar manualmente el script TTS:
   ```bash
   cd plugins/voice-notifications
   ./scripts/speak.py --text "Prueba de voz"
   ```

### Settings.json corrupto

Si el archivo de configuración se corrompe:

```bash
cd plugins/voice-notifications
./scripts/init-settings.sh
```

O eliminar y dejar que se recree:
```bash
rm plugins/voice-notifications/.claude-plugin/settings.json
/voice-notifications:config --enable
```

## Arquitectura

```
Claude Code Agent
    ↓
Hook Triggered (Stop / Notification)
    ↓
hooks/{stop,notification}-hook.sh
    ↓ (lee estado y contexto)
    ↓
scripts/speak.py (Chatterbox TTS)
    ↓
Audio Output (Sistema)
```

### Componentes

1. **Hooks**:
   - `stop-hook.sh`: Intercepta el fin de sesión del agente
   - `notification-hook.sh`: Intercepta notificaciones del sistema

2. **Script TTS**:
   - `speak.py`: Interfaz con Chatterbox TTS para sintetizar voz

3. **Configuración**:
   - `settings.json`: Preferencias del usuario
   - `hooks.json`: Registro de hooks en Claude Code

4. **Comandos**:
   - `config.md`: Comando para configurar el plugin

## Desarrollo

### Estructura del proyecto

```
plugins/voice-notifications/
├── .claude-plugin/
│   ├── plugin.json          # Metadata del plugin
│   └── settings.json        # Configuración del usuario
├── hooks/
│   ├── hooks.json           # Registro de hooks
│   ├── stop-hook.sh         # Hook para tareas completadas
│   └── notification-hook.sh # Hook para notificaciones
├── scripts/
│   ├── speak.py             # Script Python para Chatterbox TTS
│   └── init-settings.sh     # Script de inicialización
├── commands/
│   └── config.md            # Comando de configuración
├── README.md                # Este archivo
├── SPEC.md                  # Especificación técnica
└── CLAUDE.md                # Guía para Claude Code
```

### Testing manual

1. **Test Hook Stop**:
   ```
   Ejecutar tarea simple: "Crea un archivo test.txt"
   → Debería sonar: "La tarea ha sido completada: [descripción]"
   ```

2. **Test Hook Notification**:
   ```
   Crear escenario que requiera input del usuario
   → Debería sonar: "Claude necesita tu atención: [mensaje]"
   ```

3. **Test Configuración**:
   ```bash
   /voice-notifications:config --disable
   # Ejecutar tarea → NO debería sonar

   /voice-notifications:config --enable
   # Ejecutar tarea → SÍ debería sonar
   ```

4. **Test Cambio de voz**:
   ```bash
   /voice-notifications:config --voice "es-ES-Standard-B"
   # Ejecutar tarea → Debería usar la nueva voz
   ```

## Licencia

MIT License - Ver archivo LICENSE para detalles.

## Autor

**jvelez79**

## Contribuciones

Contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una branch para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la branch (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Soporte

Si encuentras problemas o tienes sugerencias:

- Abre un issue en: https://github.com/jvelez79/claude-code-plugins/issues
- Etiqueta con `plugin:voice-notifications`

## Roadmap

Futuras mejoras planeadas:

- Cola de mensajes para evitar solapamiento de audios
- Notificaciones visuales como fallback
- Soporte multiidioma automático
- Integración con sistema de notificaciones del OS
- Transcripts de audio guardados
- Detección inteligente de errores con LLM
- Triggers personalizables

## Referencias

- [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) - Biblioteca de síntesis de voz
- [Claude Code](https://claude.com/claude-code) - CLI oficial de Claude
- [Plugin Marketplace](https://github.com/jvelez79/claude-code-plugins) - Repositorio de plugins
