#!/usr/bin/env python3
"""
Voice Notifications - TTS Script
Usa el comando 'say' de macOS para síntesis de voz instantánea.
Fallback a espeak en Linux.
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path


def get_plugin_root():
    """Obtener el directorio raíz del plugin."""
    return Path(__file__).parent.parent


def load_settings():
    """
    Cargar configuración desde .claude-plugin/settings.json.
    Retorna valores default si el archivo no existe o está corrupto.
    """
    settings_path = get_plugin_root() / ".claude-plugin" / "settings.json"

    default_settings = {
        "enabled": True,
        "voice": "Mónica",  # Voz española de macOS
        "rate": 200         # Palabras por minuto
    }

    try:
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return {**default_settings, **settings}
        else:
            print("Warning: settings.json no encontrado, usando valores default", file=sys.stderr)
            return default_settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Error leyendo settings.json: {e}. Usando valores default", file=sys.stderr)
        return default_settings


def list_voices():
    """
    Listar voces disponibles en el sistema.
    En macOS muestra las voces del comando 'say'.
    """
    print("Voces disponibles para notificaciones de voz")
    print("-" * 50)
    print()

    if sys.platform == "darwin":
        print("Voces españolas en macOS:")
        print()
        try:
            result = subprocess.run(
                ["say", "-v", "?"],
                capture_output=True,
                text=True
            )
            # Filtrar voces españolas
            for line in result.stdout.split("\n"):
                if "es_" in line or "es-" in line:
                    print(f"  {line}")
            print()
            print("Uso: Configura 'voice' en settings.json con el nombre de la voz")
            print("Ejemplo: \"voice\": \"Jorge\"")
        except FileNotFoundError:
            print("Error: comando 'say' no encontrado", file=sys.stderr)
    else:
        print("Voces espeak (Linux):")
        try:
            result = subprocess.run(
                ["espeak", "--voices=es"],
                capture_output=True,
                text=True
            )
            print(result.stdout)
        except FileNotFoundError:
            print("espeak no instalado. Instala con: sudo apt install espeak", file=sys.stderr)


def speak(text: str, voice: str = None, rate: int = None):
    """
    Sintetizar y reproducir texto usando TTS del sistema.

    macOS: usa comando 'say'
    Linux: usa espeak como fallback

    Args:
        text: Texto a sintetizar
        voice: Nombre de la voz (ej: Mónica, Paulina)
        rate: Velocidad en palabras por minuto (macOS) o velocidad espeak (Linux)
    """
    if not text or text.strip() == "":
        return

    # Truncar mensajes muy largos
    MAX_LENGTH = 500
    if len(text) > MAX_LENGTH:
        text = text[:150] + "..."

    # Cargar configuración si no se especificaron parámetros
    settings = load_settings()
    voice = voice or settings.get("voice", "Jorge")
    rate = rate or settings.get("rate", 200)

    try:
        if sys.platform == "darwin":
            # macOS - usar comando 'say'
            cmd = ["say", "-v", voice, "-r", str(rate), text]
            subprocess.run(cmd, check=True)
        else:
            # Linux - usar espeak como fallback
            # espeak usa -s para velocidad (80-450, default 175)
            espeak_speed = min(450, max(80, rate))
            cmd = ["espeak", "-v", "es", "-s", str(espeak_speed), text]
            subprocess.run(cmd, check=True)

    except FileNotFoundError as e:
        if sys.platform == "darwin":
            print("Error: comando 'say' no encontrado", file=sys.stderr)
        else:
            print("Error: espeak no instalado. Instala con: sudo apt install espeak", file=sys.stderr)
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando TTS: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Voice Notifications TTS - Sintetiza texto a voz usando sistema TTS"
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Texto a sintetizar y reproducir"
    )

    parser.add_argument(
        "--voice",
        type=str,
        help="Nombre de la voz (ej: Mónica, Paulina)"
    )

    parser.add_argument(
        "--rate",
        type=int,
        help="Velocidad en palabras por minuto (default: 200)"
    )

    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="Mostrar voces disponibles"
    )

    args = parser.parse_args()

    if args.list_voices:
        list_voices()
    elif args.text:
        speak(args.text, args.voice, args.rate)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
