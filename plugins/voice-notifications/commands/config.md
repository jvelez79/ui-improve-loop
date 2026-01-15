---
name: config
description: Configurar notificaciones de voz (habilitar/deshabilitar, cambiar voz, ajustar volumen y velocidad)
argument-hint: [--enable|--disable] [--voice nombre_voz] [--volume 0-1] [--speed 0.5-2.0] [--list-voices]
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

### `--voice <nombre_voz>`
Cambia la voz utilizada para las notificaciones.
- Validación: El nombre debe ser una string no vacía
- Recomendación: Sugerir ejecutar `--list-voices` primero
- Acción: Establece `voice: "<nombre_voz>"` en settings.json

### `--volume <valor>`
Ajusta el volumen de las notificaciones (0.0 a 1.0).
- Validación: Debe ser un número entre 0.0 y 1.0
- Acción: Establece `volume: <valor>` en settings.json

### `--speed <valor>`
Ajusta la velocidad de habla (0.5 a 2.0).
- Validación: Debe ser un número entre 0.5 y 2.0
- Acción: Establece `speed: <valor>` en settings.json

### `--list-voices`
Lista las voces disponibles en Chatterbox TTS.
- Acción: Ejecutar `${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices` usando Bash tool
- Mostrar el output al usuario

## Validaciones

Antes de escribir al archivo, verifica:

1. **enabled**: Debe ser booleano (true/false)
2. **voice**: Debe ser string no vacía
3. **volume**: Debe ser número entre 0.0 y 1.0
4. **speed**: Debe ser número entre 0.5 y 2.0

Si alguna validación falla:
- **NO escribas** el archivo
- Informa al usuario del error
- Sugiere el valor correcto

## Estructura del settings.json

```json
{
  "enabled": true,
  "voice": "es-ES-Standard-A",
  "volume": 0.8,
  "speed": 1.0
}
```

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

### Ejemplo 2: Cambiar voz

```
Usuario: /voice-notifications:config --voice "es-ES-Standard-B"
```

Tu proceso:
1. Read settings.json
2. Modificar objeto: `{..."voice": "es-ES-Standard-B"...}`
3. Write de vuelta
4. Confirmar: "Voz cambiada a: es-ES-Standard-B"

### Ejemplo 3: Ajustar volumen y velocidad

```
Usuario: /voice-notifications:config --volume 0.6 --speed 1.2
```

Tu proceso:
1. Read settings.json
2. Validar: 0.0 <= 0.6 <= 1.0 ✓, 0.5 <= 1.2 <= 2.0 ✓
3. Modificar objeto: `{..."volume": 0.6, "speed": 1.2...}`
4. Write de vuelta
5. Confirmar: "Configuración actualizada: volumen=0.6, velocidad=1.2"

### Ejemplo 4: Listar voces

```
Usuario: /voice-notifications:config --list-voices
```

Tu proceso:
1. Bash: `${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices`
2. Capturar output
3. Mostrar al usuario la lista de voces disponibles

### Ejemplo 5: Sin argumentos

```
Usuario: /voice-notifications:config
```

Tu proceso:
1. Read settings.json
2. Mostrar configuración actual al usuario:
   ```
   Configuración actual:
   - Habilitado: true
   - Voz: es-ES-Standard-A
   - Volumen: 0.8
   - Velocidad: 1.0

   Uso: /voice-notifications:config [opciones]
   Opciones disponibles: --enable, --disable, --voice, --volume, --speed, --list-voices
   ```

## Edge cases

### Settings.json no existe
Si el archivo no existe al intentar leer:
1. Crear el archivo con valores default:
   ```json
   {
     "enabled": true,
     "voice": "es-ES-Standard-A",
     "volume": 0.8,
     "speed": 1.0
   }
   ```
2. Aplicar los cambios solicitados
3. Informar al usuario: "Archivo de configuración creado con valores default."

### Settings.json corrupto
Si el JSON no es válido:
1. Informar al usuario del error
2. Preguntar si desea sobrescribir con valores default
3. Si confirma, crear nuevo archivo con defaults

### speak.py no ejecutable
Si `--list-voices` falla porque speak.py no es ejecutable o no existe:
1. Informar al usuario del error
2. Sugerir verificar la instalación del plugin

## Notas importantes

- **SIEMPRE** preserva los valores no modificados al escribir settings.json
- **NO** elimines campos existentes
- **NO** agregues campos nuevos no especificados en el schema
- **USA** la variable `${CLAUDE_PLUGIN_ROOT}` para construir paths
- **CONFIRMA** cada cambio con un mensaje claro al usuario
- **MANEJA** errores gracefully y proporciona mensajes útiles
