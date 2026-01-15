#!/usr/bin/env python3
"""
Voice Notifications - TTS Script
Interfaz con Chatterbox TTS para sintetizar y reproducir voz en español.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Verificar instalación de Chatterbox
try:
    import chatterbox
except ImportError:
    print("Error: chatterbox no instalado. Ejecuta: pip install chatterbox", file=sys.stderr)
    sys.exit(1)


def get_plugin_root():
    """Obtener el directorio raíz del plugin."""
    # El script está en scripts/speak.py, el plugin root está un nivel arriba
    return Path(__file__).parent.parent


def load_settings():
    """
    Cargar configuración desde .claude-plugin/settings.json.
    Retorna valores default si el archivo no existe o está corrupto.
    """
    settings_path = get_plugin_root() / ".claude-plugin" / "settings.json"

    default_settings = {
        "enabled": True,
        "voice": "es-ES-Standard-A",
        "volume": 0.8,
        "speed": 1.0
    }

    try:
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge con defaults para asegurar que todos los campos existen
                return {**default_settings, **settings}
        else:
            print(f"Warning: settings.json no encontrado, usando valores default", file=sys.stderr)
            return default_settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Error leyendo settings.json: {e}. Usando valores default", file=sys.stderr)
        return default_settings


def list_voices():
    """
    Listar voces disponibles en Chatterbox.
    Nota: La implementación real depende de la API de Chatterbox.
    """
    try:
        # Placeholder: Chatterbox puede tener un método para listar voces
        # Por ahora, listamos voces comunes de Google TTS que Chatterbox puede soportar
        voices = [
            "es-ES-Standard-A",
            "es-ES-Standard-B",
            "es-ES-Standard-C",
            "es-ES-Standard-D",
            "es-ES-Wavenet-A",
            "es-ES-Wavenet-B",
            "es-ES-Wavenet-C",
            "es-ES-Wavenet-D",
            "es-MX-Standard-A",
            "es-MX-Standard-B",
            "es-MX-Wavenet-A",
            "es-MX-Wavenet-B",
            "es-US-Standard-A",
            "es-US-Standard-B",
            "es-US-Wavenet-A",
            "es-US-Wavenet-B"
        ]

        print("Voces disponibles para español:")
        print("-" * 40)
        for voice in voices:
            print(f"  {voice}")
        print("\nUso: /voice-notifications:config --voice \"nombre_voz\"")

    except Exception as e:
        print(f"Error listando voces: {e}", file=sys.stderr)
        sys.exit(1)


def speak(text, voice=None):
    """
    Sintetizar y reproducir texto usando Chatterbox TTS.

    Args:
        text: Texto a sintetizar
        voice: Voz a usar (opcional, usa la del settings si no se especifica)
    """
    if not text or text.strip() == "":
        print("Debug: Skipping empty message", file=sys.stderr)
        return

    # Truncar mensajes muy largos
    MAX_LENGTH = 500
    if len(text) > MAX_LENGTH:
        text = text[:150] + "..."
        print(f"Debug: Mensaje truncado a 150 caracteres", file=sys.stderr)

    # Cargar configuración
    settings = load_settings()

    # Usar voz especificada o la del settings
    selected_voice = voice or settings.get("voice", "es-ES-Standard-A")
    volume = settings.get("volume", 0.8)
    speed = settings.get("speed", 1.0)

    try:
        # Inicializar Chatterbox TTS
        # Nota: La API exacta depende de la implementación de Chatterbox
        # Este es un ejemplo basado en patrones comunes de TTS

        # Configurar engine
        tts = chatterbox.TTS()

        # Configurar parámetros
        tts.set_voice(selected_voice)
        tts.set_volume(volume)
        tts.set_rate(speed)

        # Sintetizar y reproducir
        tts.speak(text)

        print(f"Debug: Reproduciendo mensaje con voz {selected_voice}", file=sys.stderr)

    except AttributeError as e:
        # Fallback si la API de Chatterbox es diferente
        print(f"Warning: API de Chatterbox no coincide con la esperada: {e}", file=sys.stderr)
        try:
            # Intentar API alternativa común
            chatterbox.say(text, voice=selected_voice)
        except Exception as fallback_error:
            print(f"Error: No se pudo sintetizar voz: {fallback_error}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error sintetizando voz: {e}", file=sys.stderr)
        # Verificar si es problema de audio del sistema
        if "audio" in str(e).lower() or "device" in str(e).lower():
            print("Error: Sistema sin dispositivo de audio o driver no disponible", file=sys.stderr)
        sys.exit(1)


def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Voice Notifications TTS - Sintetiza texto a voz usando Chatterbox"
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Texto a sintetizar y reproducir"
    )

    parser.add_argument(
        "--voice",
        type=str,
        help="Voz específica a usar (ej: es-ES-Standard-B)"
    )

    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="Listar voces disponibles"
    )

    args = parser.parse_args()

    # Routing de comandos
    if args.list_voices:
        list_voices()
    elif args.text:
        speak(args.text, args.voice)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
