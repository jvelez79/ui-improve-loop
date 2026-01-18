---
name: config
description: Configurar notificaciones de voz (motor TTS, voz, velocidad, dispositivo)
argument-hint: [--engine system|chatterbox] [--device mps|cpu|cuda] [--enable|--disable] [--voice nombre] [--rate 80-300] [--fallback-enable|--fallback-disable] [--list-voices]
allowed-tools:
  - Read
  - Write
  - Bash
---

# Comando de Configuración: Voice Notifications

Este comando permite al usuario configurar las notificaciones de voz del plugin.

## Tu responsabilidad

Cuando el usuario ejecute este comando, debes:

1. **Leer la configuración actual** desde `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/settings.json`
2. **Modificar los valores** según los argumentos proporcionados
3. **Validar los valores** antes de escribir
4. **Escribir la configuración actualizada** de vuelta al archivo
5. **Confirmar al usuario** los cambios realizados

## Argumentos disponibles

### `--enable`
Habilita las notificaciones de voz.
- Acción: Establece `enabled: true` en settings.json

### `--disable`
Deshabilita las notificaciones de voz.
- Acción: Establece `enabled: false` en settings.json

### `--engine <system|chatterbox>`
Selecciona el motor TTS a usar.
- **system**: TTS del sistema (macOS 'say' / Linux 'espeak') - instantáneo
- **chatterbox**: Chatterbox-Turbo neural TTS - alta calidad, requiere instalación
- Validación: Debe ser "system" o "chatterbox"
- Default: "system"
- Acción: Establece `tts_engine: "<valor>"` en settings.json

### `--device <mps|cpu|cuda>`
Configura el dispositivo de aceleración para Chatterbox-Turbo.
- **mps**: Apple Silicon (M1/M2/M3/M4) - recomendado para macOS
- **cpu**: CPU genérico - más lento pero funciona en cualquier sistema
- **cuda**: GPU NVIDIA - para Linux/Windows con GPU
- Validación: Debe ser "mps", "cpu" o "cuda"
- Default: "mps"
- Nota: Solo aplica cuando `tts_engine == "chatterbox"`
- Acción: Establece `chatterbox.device: "<valor>"` en settings.json

### `--voice <nombre_voz>`
Cambia la voz utilizada para las notificaciones (solo para TTS sistema).
- macOS: Jorge, Paulina, Juan, Mónica (voces españolas del sistema)
- Linux: voces de espeak
- Validación: El nombre debe ser una string no vacía
- Recomendación: Sugerir ejecutar `--list-voices` primero
- Nota: Para Chatterbox-Turbo, usar voice cloning (ver README)
- Acción: Establece `voice: "<nombre_voz>"` en settings.json

### `--rate <valor>`
Ajusta la velocidad de habla (palabras por minuto, solo para TTS sistema).
- Validación: Debe ser un número entre 80 y 300
- Default: 200
- Nota: Chatterbox-Turbo no usa este parámetro
- Acción: Establece `rate: <valor>` en settings.json

### `--fallback-enable`
Habilita fallback automático a TTS sistema si Chatterbox-Turbo falla.
- Acción: Establece `fallback_to_system: true` en settings.json
- Recomendado: Mantener habilitado para robustez

### `--fallback-disable`
Deshabilita fallback automático.
- Acción: Establece `fallback_to_system: false` en settings.json
- Uso: Solo si deseas que falle explícitamente cuando Chatterbox no está disponible

### `--list-voices`
Lista las voces disponibles según el motor TTS configurado.
- Si `tts_engine == "system"`: Lista voces del sistema (say/espeak)
- Si `tts_engine == "chatterbox"`: Muestra información sobre voice cloning
- Acción: Ejecutar `${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices` usando Bash tool
- Mostrar el output al usuario

## Validaciones

Antes de escribir al archivo, verifica:

1. **enabled**: Debe ser booleano (true/false)
2. **tts_engine**: Debe ser "system" o "chatterbox"
3. **voice**: Debe ser string no vacía
4. **rate**: Debe ser número entre 80 y 300
5. **chatterbox.device**: Debe ser "mps", "cpu" o "cuda"
6. **chatterbox.exaggeration**: Número entre 0.0 y 2.0 (si presente)
7. **chatterbox.voice_sample**: Path válido a archivo o null (si presente)
8. **fallback_to_system**: Debe ser booleano (true/false)

Si alguna validación falla:
- **NO escribas** el archivo
- Informa al usuario del error
- Sugiere el valor correcto

## Estructura del settings.json

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

## Voces españolas disponibles en macOS

| Voz | Región | Descripción |
|-----|--------|-------------|
| Jorge | España | Voz masculina española |
| Paulina | México | Voz femenina mexicana |
| Juan | México | Voz masculina mexicana |
| Mónica | España | Voz femenina española |

Nota: Las voces disponibles pueden variar según la versión de macOS. Usa `--list-voices` para ver las voces instaladas.

## Flujo de ejecución

### Ejemplo 1: Deshabilitar notificaciones

```
Usuario: /voice-notifications:config --disable
```

Tu proceso:
1. Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/settings.json`
2. Modificar objeto: `{"enabled": false, ...otros valores sin cambiar...}`
3. Write de vuelta al archivo
4. Confirmar: "Notificaciones de voz deshabilitadas."

### Ejemplo 2: Cambiar a Chatterbox-Turbo

```
Usuario: /voice-notifications:config --engine chatterbox
```

Tu proceso:
1. Read settings.json
2. Modificar objeto: `{..."tts_engine": "chatterbox"...}`
3. Write de vuelta
4. Confirmar: "Motor TTS cambiado a: Chatterbox-Turbo. Nota: Requiere instalación de dependencias (ver README)."

### Ejemplo 3: Configurar device para Chatterbox

```
Usuario: /voice-notifications:config --device cpu
```

Tu proceso:
1. Read settings.json
2. Verificar que el objeto `chatterbox` existe (crear si no)
3. Modificar objeto: `{..."chatterbox": {"device": "cpu", ...otros valores...}...}`
4. Write de vuelta
5. Confirmar: "Dispositivo de aceleración para Chatterbox-Turbo configurado a: cpu"

### Ejemplo 4: Cambiar voz (TTS sistema)

```
Usuario: /voice-notifications:config --voice Paulina
```

Tu proceso:
1. Read settings.json
2. Modificar objeto: `{..."voice": "Paulina"...}`
3. Write de vuelta
4. Confirmar: "Voz cambiada a: Paulina (solo aplica para TTS sistema)"

### Ejemplo 5: Ajustar velocidad

```
Usuario: /voice-notifications:config --rate 180
```

Tu proceso:
1. Read settings.json
2. Validar: 80 <= 180 <= 300 ✓
3. Modificar objeto: `{..."rate": 180...}`
4. Write de vuelta
5. Confirmar: "Velocidad ajustada a: 180 palabras por minuto (solo aplica para TTS sistema)"

### Ejemplo 6: Habilitar fallback

```
Usuario: /voice-notifications:config --fallback-enable
```

Tu proceso:
1. Read settings.json
2. Modificar objeto: `{..."fallback_to_system": true...}`
3. Write de vuelta
4. Confirmar: "Fallback a TTS sistema habilitado. Si Chatterbox-Turbo falla, usará say/espeak automáticamente."

### Ejemplo 7: Listar voces

```
Usuario: /voice-notifications:config --list-voices
```

Tu proceso:
1. Bash: `${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices`
2. Capturar output
3. Mostrar al usuario la lista de voces disponibles (el output variará según tts_engine)

### Ejemplo 8: Sin argumentos

```
Usuario: /voice-notifications:config
```

Tu proceso:
1. Read settings.json
2. Mostrar configuración actual al usuario:
   ```
   Configuración actual:
   - Habilitado: true
   - Motor TTS: system
   - Voz: Jorge (solo para TTS sistema)
   - Velocidad: 200 palabras/min (solo para TTS sistema)
   - Device Chatterbox: mps
   - Fallback habilitado: true

   Uso: /voice-notifications:config [opciones]
   Opciones disponibles:
     --enable, --disable
     --engine <system|chatterbox>
     --device <mps|cpu|cuda>
     --voice <nombre>
     --rate <80-300>
     --fallback-enable, --fallback-disable
     --list-voices
   ```

### Ejemplo 9: Configuración completa para Chatterbox

```
Usuario: /voice-notifications:config --engine chatterbox --device mps --fallback-enable
```

Tu proceso:
1. Read settings.json
2. Modificar múltiples valores:
   - `tts_engine: "chatterbox"`
   - `chatterbox.device: "mps"`
   - `fallback_to_system: true`
3. Write de vuelta
4. Confirmar cambios múltiples al usuario

## Edge cases

### Settings.json no existe
Si el archivo no existe al intentar leer:
1. Crear el archivo con valores default (incluyendo nuevos campos):
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
2. Aplicar los cambios solicitados
3. Informar al usuario: "Archivo de configuración creado con valores default."

### Settings.json antiguo (sin campos nuevos)
Si el archivo existe pero no tiene `tts_engine`, `chatterbox`, o `fallback_to_system`:
1. Leer valores existentes
2. Agregar campos faltantes con defaults
3. Aplicar cambios solicitados
4. Write de vuelta
5. Informar: "Configuración actualizada con nuevos campos (retrocompatibilidad)"

### Settings.json corrupto
Si el JSON no es válido:
1. Informar al usuario del error
2. Preguntar si desea sobrescribir con valores default
3. Si confirma, crear nuevo archivo con defaults completos

### speak.py no ejecutable
Si `--list-voices` falla porque speak.py no es ejecutable o no existe:
1. Informar al usuario del error
2. Sugerir verificar la instalación del plugin

### Configurar --device sin tener Chatterbox instalado
Si el usuario configura `--device` pero Chatterbox-Turbo no está instalado:
1. Aplicar el cambio igualmente (puede instalarlo después)
2. Informar: "Device configurado. Nota: Chatterbox-Turbo no detectado. Ver README para instalación."

## Notas importantes

- **SIEMPRE** preserva los valores no modificados al escribir settings.json
- **NO** elimines campos existentes
- **ASEGÚRATE** de mantener la estructura de `chatterbox` como objeto anidado
- **USA** la variable `${CLAUDE_PLUGIN_ROOT}` para construir paths
- **CONFIRMA** cada cambio con un mensaje claro al usuario
- **MANEJA** errores gracefully y proporciona mensajes útiles
- **SUGIERE** ejecutar `--list-voices` después de cambiar `--engine`
- **RECUERDA** que `voice` y `rate` solo aplican a TTS sistema
