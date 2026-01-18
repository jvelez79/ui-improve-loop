# Voice Notifications Plugin

Plugin de Claude Code que proporciona notificaciones de voz en español usando TTS de alta calidad. El plugin intercepta eventos del ciclo de vida del agente para informar al usuario sobre el estado de las tareas sin necesidad de monitorear visualmente la terminal.

## Características

- Dos motores TTS disponibles:
  - **System TTS**: TTS nativo del sistema (macOS `say` / Linux `espeak`) - instantáneo (<100ms)
  - **Chatterbox-Turbo**: Neural TTS de alta calidad - latencia ~300-500ms con voz natural
- Alertas cuando Claude necesita atención del usuario
- Detección automática de errores con mensajes contextuales
- Configuración flexible (motor, voz, velocidad, dispositivo de aceleración)
- Mensajes en español naturales y concisos
- Ejecución no bloqueante (background)
- Fallback automático: Si Chatterbox-Turbo falla, usa TTS sistema

## Requisitos

### Sistema (obligatorio)

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

### TTS del sistema (obligatorio)

- **macOS**: Incluido por defecto (comando `say`)
- **Linux**: Instalar espeak
  ```bash
  sudo apt install espeak
  ```

### Chatterbox-Turbo (opcional)

Para obtener calidad de voz superior al TTS sistema:

- **Python 3.8+**
- **Apple Silicon (M1/M2/M3/M4)** para aceleración MPS, o **GPU CUDA**
- **2 GB de RAM libre** (modelo es ~350MB)

Ver sección "Instalación de Chatterbox-Turbo" más abajo

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

## Instalación de Chatterbox-Turbo (Opcional)

Para obtener mejor calidad de voz que el TTS del sistema, puedes instalar Chatterbox-Turbo:

### Paso 1: Instalar PyTorch con soporte MPS (macOS Apple Silicon)

```bash
pip install torch torchvision
```

### Paso 2: Instalar Chatterbox-Turbo desde source

```bash
pip install git+https://github.com/resemble-ai/chatterbox.git
```

### Paso 3: Instalar sounddevice para reproducción de audio

```bash
pip install sounddevice
```

### Paso 4: Autenticar con Hugging Face

El modelo Chatterbox-Turbo requiere autenticación con Hugging Face:

1. Crear cuenta en https://huggingface.co si no tienes una
2. Crear token de acceso en https://huggingface.co/settings/tokens (tipo "Read")
3. Autenticarse:

```bash
pip install huggingface_hub
huggingface-cli login
# Pegar el token cuando lo solicite
```

### Paso 5: Verificar instalación

```bash
python3 -c "from chatterbox.tts_turbo import ChatterboxTurboTTS; print('OK')"
```

Si imprime "OK", la instalación fue exitosa.

### Paso 6: Configurar plugin para usar Chatterbox

```bash
/voice-notifications:config --engine chatterbox --device mps
```

### Benchmark de Latencia

Esperado en Apple M4 Pro:
- **Primera ejecución**: ~2-3s (carga de modelo)
- **Ejecuciones subsiguientes**: ~300-500ms (generación + reproducción)

### Fallback Automático

Si Chatterbox-Turbo no está instalado o falla, el plugin automáticamente usa el TTS del sistema (say/espeak) si `fallback_to_system` está habilitado (default).

## Uso

### Configuración básica

```bash
# Ver configuración actual
/voice-notifications:config

# Habilitar/deshabilitar notificaciones de voz
/voice-notifications:config --enable
/voice-notifications:config --disable

# Seleccionar motor TTS
/voice-notifications:config --engine system       # TTS sistema (default)
/voice-notifications:config --engine chatterbox   # Chatterbox-Turbo (requiere instalación)

# Configurar device para Chatterbox-Turbo
/voice-notifications:config --device mps   # Apple Silicon (recomendado)
/voice-notifications:config --device cpu   # CPU genérico (más lento)
/voice-notifications:config --device cuda  # GPU NVIDIA

# Listar voces disponibles (varía según engine)
/voice-notifications:config --list-voices

# Cambiar voz (solo para TTS sistema)
/voice-notifications:config --voice Paulina

# Ajustar velocidad de habla (solo para TTS sistema, 80-300 palabras/min)
/voice-notifications:config --rate 180

# Configurar fallback
/voice-notifications:config --fallback-enable   # Default, recomendado
/voice-notifications:config --fallback-disable  # Falla si Chatterbox no disponible

# Configuración completa para Chatterbox
/voice-notifications:config --engine chatterbox --device mps --fallback-enable
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

Campos:
- **enabled** (boolean): Habilitar/deshabilitar el plugin
- **tts_engine** (string): Motor TTS a usar ("system" o "chatterbox")
- **voice** (string): Nombre de la voz del sistema (solo para TTS sistema)
- **rate** (number 80-300): Velocidad de habla en palabras por minuto (solo para TTS sistema)
- **chatterbox** (object): Configuración de Chatterbox-Turbo
  - **device** (string): Dispositivo de aceleración ("mps", "cpu", o "cuda")
  - **voice_sample** (string|null): Path a audio de referencia para voice cloning (opcional)
  - **exaggeration** (number 0.0-2.0): Nivel de expresividad (0.0=monotone, 2.0=dramatic)
- **fallback_to_system** (boolean): Usar TTS sistema si Chatterbox falla (recomendado: true)

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

### Chatterbox-Turbo

Chatterbox-Turbo usa voice cloning para generar voces naturales.

**Opciones:**
1. **Voz default del modelo** (sin configuración adicional)
2. **Voice cloning con audio de referencia** (avanzado)

Para usar voice cloning:
1. Graba 5-10 segundos de audio de referencia (.wav o .mp3)
2. Configura en settings.json:
   ```json
   {
     "chatterbox": {
       "voice_sample": "/path/to/reference.wav"
     }
   }
   ```

Ajustar expresividad (opcional):
```json
{
  "chatterbox": {
    "exaggeration": 1.0  // 0.0 = monotone, 2.0 = dramatic
  }
}
```

## Troubleshooting

### Chatterbox-Turbo: ImportError

**Error**: `Chatterbox-Turbo no instalado`

**Solución**:
1. Instalar desde source:
   ```bash
   pip install git+https://github.com/resemble-ai/chatterbox.git
   ```
2. Verificar instalación:
   ```bash
   python3 -c "from chatterbox.tts_turbo import ChatterboxTurboTTS; print('OK')"
   ```

### Chatterbox-Turbo: Device no disponible

**Error**: `Device 'mps' no disponible, usando 'cpu'`

**Solución**:
- En sistemas sin Apple Silicon, usar CPU o CUDA:
  ```bash
  /voice-notifications:config --device cpu
  ```
- Verificar PyTorch MPS:
  ```bash
  python3 -c "import torch; print(torch.backends.mps.is_available())"
  ```

### Chatterbox-Turbo: sounddevice no instalado

**Error**: `sounddevice no instalado`

**Solución**:
```bash
pip install sounddevice
```

### Chatterbox-Turbo: Latencia alta

**Problema**: Primera ejecución toma 2-3s

**Explicación**: Es normal, el modelo se carga en primera ejecución (lazy loading). Ejecuciones subsiguientes son rápidas (~300-500ms).

### Chatterbox-Turbo: Memoria insuficiente

**Error**: `RuntimeError: Memoria insuficiente`

**Solución**:
1. Verificar RAM disponible (requiere ~2GB)
2. Usar CPU en lugar de MPS:
   ```bash
   /voice-notifications:config --device cpu
   ```
3. O usar TTS sistema:
   ```bash
   /voice-notifications:config --engine system
   ```

### General: Notificaciones

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
    ↓ (lee settings.json)
    ↓
scripts/speak.py
    ↓
┌─────────────────────────────────────────┐
│ Decision Engine                         │
│ ├─ tts_engine == "chatterbox"           │
│ │   ├─ Lazy load model (primera vez)    │
│ │   ├─ Generate audio con MPS           │
│ │   └─ Fallback a system si falla       │
│ └─ tts_engine == "system"               │
│     └─ say/espeak (actual)              │
└─────────────────────────────────────────┘
    ↓
Audio Output
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

## Comparación de Motores TTS

| Aspecto | System TTS | Chatterbox-Turbo |
|---------|------------|------------------|
| **Latencia** | <100ms | ~300-500ms (después de carga inicial) |
| **Calidad de voz** | Aceptable | Alta (natural, expresiva) |
| **Requisitos** | Sistema operativo | PyTorch + GPU/MPS |
| **Instalación** | Incluido | Manual (pip install) |
| **Configuración** | Voz, velocidad | Device, expresividad, voice cloning |
| **Uso de memoria** | Mínimo | ~350MB (modelo cargado) |
| **Fallback** | N/A | Automático a System TTS |

**Recomendación**:
- Usar **System TTS** para latencia mínima y simplicidad
- Usar **Chatterbox-Turbo** para calidad de voz superior (ideal para mensajes importantes)

## Roadmap

Futuras mejoras planeadas:

- Cola de mensajes para evitar solapamiento de audios
- Notificaciones visuales como fallback
- Integración con sistema de notificaciones del OS
- Triggers personalizables
- Streaming de audio para Chatterbox-Turbo (reducir latencia)

## Referencias

- [Claude Code](https://claude.com/claude-code) - CLI oficial de Claude
- [Plugin Marketplace](https://github.com/jvelez79/claude-code-plugins) - Repositorio de plugins
