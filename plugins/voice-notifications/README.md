# Voice Notifications Plugin

Plugin de Claude Code que proporciona notificaciones de voz instantáneas en español usando el TTS nativo del sistema (macOS `say` / Linux espeak). El plugin intercepta eventos del ciclo de vida del agente para informar al usuario sobre el estado de las tareas sin necesidad de monitorear visualmente la terminal.

## Características

- Notificaciones de voz instantáneas (<100ms de latencia)
- Alertas cuando Claude necesita atención del usuario
- Detección automática de errores con mensajes contextuales
- Configuración flexible (habilitar/deshabilitar, cambiar voz, ajustar velocidad)
- Mensajes en español naturales y concisos
- Ejecución no bloqueante (background)
- Sin dependencias externas (usa TTS del sistema)

## Requisitos

### Sistema

- **Python 3.8+**
  ```bash
  python3 --version
  ```

- **jq** (opcional, para parsing JSON en bash)
  ```bash
  # macOS
  brew install jq

  # Linux (Ubuntu/Debian)
  sudo apt install jq
  ```

### TTS del sistema

- **macOS**: Incluido por defecto (comando `say`)
- **Linux**: Instalar espeak
  ```bash
  sudo apt install espeak
  ```

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
/voice-notifications:config --voice Paulina

# Ajustar velocidad de habla (80 a 300 palabras/min)
/voice-notifications:config --rate 180

# Configurar múltiples opciones a la vez
/voice-notifications:config --voice Jorge --rate 200
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
  "voice": "Jorge",
  "rate": 200
}
```

Campos:
- **enabled** (boolean): Habilitar/deshabilitar el plugin
- **voice** (string): Nombre de la voz del sistema
- **rate** (number 80-300): Velocidad de habla en palabras por minuto

## Voces disponibles

### macOS

Voces españolas incluidas en el sistema:

| Voz | Región | Tipo |
|-----|--------|------|
| Jorge | España | Masculina |
| Mónica | España | Femenina |
| Paulina | México | Femenina |
| Juan | México | Masculina |

Para ver todas las voces españolas disponibles:
```bash
say -v '?' | grep es_
```

Algunas voces pueden requerir descarga en **Ajustes del Sistema > Accesibilidad > Contenido hablado**.

### Linux (espeak)

Voces españolas de espeak:
```bash
espeak --voices=es
```

## Troubleshooting

### macOS: Voz no encontrada

**Error**: La voz especificada no está instalada

**Solución**:
1. Ir a **Ajustes del Sistema > Accesibilidad > Contenido hablado**
2. Descargar voces españolas adicionales
3. O usar una voz por defecto: `Jorge`, `Paulina`

### Linux: espeak no instalado

**Error**: `espeak no instalado`

**Solución**:
```bash
sudo apt install espeak
```

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

2. Verificar que el sistema tenga TTS:
   ```bash
   # macOS
   say "Prueba"

   # Linux
   espeak "Prueba"
   ```

3. Probar manualmente el script TTS:
   ```bash
   cd plugins/voice-notifications
   ./scripts/speak.py --text "Prueba de voz"
   ```

### Settings.json corrupto

Si el archivo de configuración se corrompe, eliminar y recrear:
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
scripts/speak.py
    ↓
macOS: say -v Jorge "mensaje"
Linux: espeak -v es "mensaje"
    ↓
Audio Output (<100ms)
```

### Componentes

1. **Hooks**:
   - `stop-hook.sh`: Intercepta el fin de sesión del agente
   - `notification-hook.sh`: Intercepta notificaciones del sistema

2. **Script TTS**:
   - `speak.py`: Interfaz con TTS nativo del sistema

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
│   └── speak.py             # Script Python para TTS del sistema
├── commands/
│   └── config.md            # Comando de configuración
├── README.md                # Este archivo
└── CLAUDE.md                # Guía para Claude Code
```

### Testing manual

1. **Test Hook Stop**:
   ```
   Ejecutar tarea simple: "Crea un archivo test.txt"
   → Debería sonar instantáneamente: "La tarea ha sido completada: [descripción]"
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
   /voice-notifications:config --voice Paulina
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
- Integración con sistema de notificaciones del OS
- Triggers personalizables

## Referencias

- [Claude Code](https://claude.com/claude-code) - CLI oficial de Claude
- [Plugin Marketplace](https://github.com/jvelez79/claude-code-plugins) - Repositorio de plugins
