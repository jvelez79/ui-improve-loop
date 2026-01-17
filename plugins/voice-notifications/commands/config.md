---
name: config
description: Configurar notificaciones de voz (habilitar/deshabilitar, cambiar voz, ajustar velocidad)
argument-hint: [--enable|--disable] [--voice nombre_voz] [--rate 80-300] [--list-voices]
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
- macOS: Jorge, Paulina, Juan, Mónica (voces españolas del sistema)
- Linux: voces de espeak
- Validación: El nombre debe ser una string no vacía
- Recomendación: Sugerir ejecutar `--list-voices` primero
- Acción: Establece `voice: "<nombre_voz>"` en settings.json

### `--rate <valor>`
Ajusta la velocidad de habla (palabras por minuto).
- Validación: Debe ser un número entre 80 y 300
- Default: 200
- Acción: Establece `rate: <valor>` en settings.json

### `--list-voices`
Lista las voces españolas disponibles en el sistema.
- macOS: Usa comando `say -v '?'` filtrado por voces españolas
- Linux: Usa `espeak --voices=es`
- Acción: Ejecutar `${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices` usando Bash tool
- Mostrar el output al usuario

## Validaciones

Antes de escribir al archivo, verifica:

1. **enabled**: Debe ser booleano (true/false)
2. **voice**: Debe ser string no vacía
3. **rate**: Debe ser número entre 80 y 300

Si alguna validación falla:
- **NO escribas** el archivo
- Informa al usuario del error
- Sugiere el valor correcto

## Estructura del settings.json

```json
{
  "enabled": true,
  "voice": "Jorge",
  "rate": 200
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

### Ejemplo 2: Cambiar voz

```
Usuario: /voice-notifications:config --voice Paulina
```

Tu proceso:
1. Read settings.json
2. Modificar objeto: `{..."voice": "Paulina"...}`
3. Write de vuelta
4. Confirmar: "Voz cambiada a: Paulina"

### Ejemplo 3: Ajustar velocidad

```
Usuario: /voice-notifications:config --rate 180
```

Tu proceso:
1. Read settings.json
2. Validar: 80 <= 180 <= 300 ✓
3. Modificar objeto: `{..."rate": 180...}`
4. Write de vuelta
5. Confirmar: "Velocidad ajustada a: 180 palabras por minuto"

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
   - Voz: Jorge
   - Velocidad: 200 palabras/min

   Uso: /voice-notifications:config [opciones]
   Opciones disponibles: --enable, --disable, --voice, --rate, --list-voices
   ```

## Edge cases

### Settings.json no existe
Si el archivo no existe al intentar leer:
1. Crear el archivo con valores default:
   ```json
   {
     "enabled": true,
     "voice": "Jorge",
     "rate": 200
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
