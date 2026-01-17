#!/usr/bin/env python3
"""
Voice Notifications - TTS Script
Interfaz con Chatterbox TTS para sintetizar y reproducir voz.
"""

import argparse
import json
import sys
import os
import tempfile
import subprocess
from pathlib import Path

# Verificar instalación de dependencias
try:
    import torch
    import torchaudio
    from chatterbox.tts import ChatterboxTTS
except ImportError as e:
    print(f"Error: Dependencia no instalada: {e}", file=sys.stderr)
    print("Ejecuta: pip install chatterbox-tts", file=sys.stderr)
    sys.exit(1)

# Cache global del modelo para evitar recarga
_model = None


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
        "volume": 0.8,
        "speed": 1.0
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


def get_device():
    """Detectar el mejor dispositivo disponible para inferencia."""
    if torch.backends.mps.is_available():
        return "mps"  # Mac M1/M2
    elif torch.cuda.is_available():
        return "cuda"  # NVIDIA GPU
    else:
        return "cpu"


def get_model():
    """
    Obtener el modelo TTS, cargándolo si es necesario.
    El modelo se cachea globalmente para evitar recarga en cada llamada.
    """
    global _model
    if _model is None:
        device = get_device()
        print(f"Debug: Cargando modelo Chatterbox en dispositivo '{device}'...", file=sys.stderr)
        _model = ChatterboxTTS.from_pretrained(device=device)
        print("Debug: Modelo cargado exitosamente", file=sys.stderr)
    return _model


def list_voices():
    """
    Mostrar información sobre voces en Chatterbox.
    Chatterbox usa voice cloning, no voces predefinidas.
    """
    print("Chatterbox TTS - Información de Voces")
    print("-" * 50)
    print()
    print("Chatterbox usa VOICE CLONING, no voces predefinidas.")
    print()
    print("Para usar una voz personalizada:")
    print("  1. Graba un audio de referencia (10-30 segundos)")
    print("  2. Guárdalo como archivo WAV")
    print("  3. Configura la ruta en settings.json:")
    print()
    print('     "audio_prompt_path": "/ruta/a/tu/voz.wav"')
    print()
    print("Sin audio de referencia, se usa la voz por defecto del modelo.")
    print()
    print("Más info: https://github.com/resemble-ai/chatterbox")


def speak(text, audio_prompt_path=None):
    """
    Sintetizar y reproducir texto usando Chatterbox TTS.

    Args:
        text: Texto a sintetizar
        audio_prompt_path: Ruta opcional a archivo WAV para voice cloning
    """
    if not text or text.strip() == "":
        print("Debug: Skipping empty message", file=sys.stderr)
        return

    # Truncar mensajes muy largos
    MAX_LENGTH = 500
    if len(text) > MAX_LENGTH:
        text = text[:150] + "..."
        print("Debug: Mensaje truncado a 150 caracteres", file=sys.stderr)

    # Cargar configuración
    settings = load_settings()

    # Verificar audio_prompt_path del settings si no se especificó
    if audio_prompt_path is None:
        audio_prompt_path = settings.get("audio_prompt_path")

    try:
        # Obtener modelo
        model = get_model()

        print(f"Debug: Generando audio para: '{text[:50]}...'", file=sys.stderr)

        # Generar audio
        if audio_prompt_path and os.path.exists(audio_prompt_path):
            print(f"Debug: Usando voice cloning con: {audio_prompt_path}", file=sys.stderr)
            wav = model.generate(text, audio_prompt_path=audio_prompt_path)
        else:
            wav = model.generate(text)

        # Guardar a archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        torchaudio.save(temp_path, wav, model.sr)
        print(f"Debug: Audio guardado en {temp_path}", file=sys.stderr)

        # Reproducir audio (macOS)
        print("Debug: Reproduciendo audio...", file=sys.stderr)
        subprocess.run(["afplay", temp_path], check=True)

        # Limpiar archivo temporal
        os.unlink(temp_path)
        print("Debug: Reproducción completada", file=sys.stderr)

    except FileNotFoundError:
        print("Error: 'afplay' no encontrado. Este script requiere macOS.", file=sys.stderr)
        print("Para Linux, instala 'aplay' o 'paplay' y modifica el script.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Error sintetizando voz: {e}", file=sys.stderr)
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
        "--audio-prompt",
        type=str,
        help="Ruta a archivo WAV para voice cloning (opcional)"
    )

    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="Mostrar información sobre voces"
    )

    args = parser.parse_args()

    # Routing de comandos
    if args.list_voices:
        list_voices()
    elif args.text:
        speak(args.text, args.audio_prompt)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
