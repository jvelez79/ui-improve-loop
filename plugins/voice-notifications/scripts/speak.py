#!/usr/bin/env python3
"""
Voice Notifications - TTS Script
Soporta múltiples engines TTS:
- system: macOS 'say' / Linux 'espeak' (instantáneo)
- chatterbox: Chatterbox-Turbo neural TTS (alta calidad)
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod


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
        "tts_engine": "system",  # "system" o "chatterbox"
        "voice": "Mónica",
        "rate": 200,
        "chatterbox": {
            "device": "mps",
            "voice_sample": None,
            "exaggeration": 1.0
        },
        "fallback_to_system": True
    }

    try:
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge con defaults para retrocompatibilidad
                merged = {**default_settings, **settings}
                # Merge nested chatterbox config
                if "chatterbox" in settings:
                    merged["chatterbox"] = {**default_settings["chatterbox"], **settings["chatterbox"]}
                return merged
        else:
            print("[voice-notifications:speak] Warning: settings.json no encontrado, usando valores default", file=sys.stderr)
            return default_settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"[voice-notifications:speak] Warning: Error leyendo settings.json: {e}. Usando valores default", file=sys.stderr)
        return default_settings


class TTSEngine(ABC):
    """Clase base abstracta para motores TTS."""

    @abstractmethod
    def speak(self, text: str, **kwargs) -> None:
        """
        Sintetizar y reproducir texto.

        Args:
            text: Texto a sintetizar
            **kwargs: Parámetros específicos del engine
        """
        pass

    @abstractmethod
    def list_voices(self) -> None:
        """Listar voces disponibles para este engine."""
        pass


class SystemTTS(TTSEngine):
    """Motor TTS usando comandos del sistema (say/espeak)."""

    def __init__(self, settings: dict):
        self.settings = settings

    def speak(self, text: str, voice: str = None, rate: int = None) -> None:
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

        # Usar configuración si no se especificaron parámetros
        voice = voice or self.settings.get("voice", "Jorge")
        rate = rate or self.settings.get("rate", 200)

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

        except FileNotFoundError:
            if sys.platform == "darwin":
                print("[voice-notifications:speak] Error: comando 'say' no encontrado", file=sys.stderr)
            else:
                print("[voice-notifications:speak] Error: espeak no instalado. Instala con: sudo apt install espeak", file=sys.stderr)
            sys.exit(1)

        except subprocess.CalledProcessError as e:
            print(f"[voice-notifications:speak] Error ejecutando TTS: {e}", file=sys.stderr)
            sys.exit(1)

    def list_voices(self) -> None:
        """Listar voces disponibles en el sistema."""
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


class ChatterboxTurboTTS(TTSEngine):
    """Motor TTS usando Chatterbox-Turbo (neural TTS de alta calidad)."""

    _instance = None
    _model = None
    _device = None

    def __new__(cls, settings: dict):
        """Singleton para reutilizar modelo cargado."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: dict):
        self.settings = settings

    def _detect_device(self) -> str:
        """
        Detectar dispositivo de aceleración disponible.

        Returns:
            "mps" | "cuda" | "cpu"
        """
        try:
            import torch

            # Verificar MPS (Apple Silicon)
            if torch.backends.mps.is_available():
                return "mps"

            # Verificar CUDA
            if torch.cuda.is_available():
                return "cuda"

            # Fallback a CPU
            return "cpu"

        except ImportError:
            print("[voice-notifications:speak] Warning: PyTorch no instalado, usando CPU", file=sys.stderr)
            return "cpu"

    def _load_model(self) -> None:
        """
        Cargar modelo Chatterbox-Turbo (lazy loading).
        Solo se ejecuta una vez por sesión.
        """
        if self._model is not None:
            return  # Ya cargado

        try:
            import torch
            from chatterbox.tts_turbo import ChatterboxTurboTTS as ChatterboxModel

            print("[voice-notifications:speak] Cargando modelo Chatterbox-Turbo (solo primera vez)...", file=sys.stderr)

            # Obtener device configurado o auto-detectar
            configured_device = self.settings.get("chatterbox", {}).get("device", "mps")
            actual_device = self._detect_device()

            # Si el device configurado no está disponible, usar el detectado
            if configured_device != actual_device:
                print(f"[voice-notifications:speak] Device '{configured_device}' no disponible, usando '{actual_device}'", file=sys.stderr)
                device = actual_device
            else:
                device = configured_device

            # Cargar modelo
            self._model = ChatterboxModel.from_pretrained(device=device)
            self._device = device

            print(f"[voice-notifications:speak] Modelo cargado en device: {device}", file=sys.stderr)

        except ImportError as e:
            raise ImportError(f"Chatterbox-Turbo no instalado. Instala con: pip install git+https://github.com/resemble-ai/chatterbox.git") from e

        except Exception as e:
            raise RuntimeError(f"Error cargando modelo Chatterbox-Turbo: {e}") from e

    def _play_audio(self, wav, sample_rate: int = 24000) -> None:
        """
        Reproducir audio usando sounddevice.

        Args:
            wav: Array de audio (numpy o torch tensor)
            sample_rate: Sample rate del audio
        """
        try:
            import sounddevice as sd
            import numpy as np

            # Convertir a numpy si es tensor de torch
            if hasattr(wav, 'numpy'):
                wav_np = wav.cpu().numpy() if wav.is_cuda or (hasattr(wav, 'is_mps') and wav.is_mps) else wav.numpy()
            else:
                wav_np = np.array(wav)

            # Reproducir
            sd.play(wav_np, sample_rate)
            sd.wait()

        except ImportError:
            raise ImportError("sounddevice no instalado. Instala con: pip install sounddevice")

        except Exception as e:
            raise RuntimeError(f"Error reproduciendo audio: {e}") from e

    def speak(self, text: str, **kwargs) -> None:
        """
        Sintetizar y reproducir texto usando Chatterbox-Turbo.

        Args:
            text: Texto a sintetizar
            **kwargs: Parámetros ignorados (para compatibilidad)
        """
        if not text or text.strip() == "":
            return

        # Truncar mensajes muy largos
        MAX_LENGTH = 500
        if len(text) > MAX_LENGTH:
            text = text[:150] + "..."

        # Cargar modelo (lazy loading)
        self._load_model()

        # Generar audio
        chatterbox_config = self.settings.get("chatterbox", {})
        exaggeration = chatterbox_config.get("exaggeration", 1.0)
        voice_sample = chatterbox_config.get("voice_sample")

        try:
            # Verificar si hay voice sample para cloning
            if voice_sample and Path(voice_sample).exists():
                import torchaudio
                ref_wav, ref_sr = torchaudio.load(voice_sample)
                wav = self._model.generate(
                    text=text,
                    reference_audio=ref_wav,
                    exaggeration=exaggeration
                )
            else:
                # Usar voz default del modelo
                wav = self._model.generate(
                    text=text,
                    exaggeration=exaggeration
                )

            # Reproducir audio
            self._play_audio(wav, self._model.sr)

        except Exception as e:
            raise RuntimeError(f"Error generando/reproduciendo audio: {e}") from e

    def list_voices(self) -> None:
        """Listar voces disponibles para Chatterbox-Turbo."""
        print("Chatterbox-Turbo TTS")
        print("-" * 50)
        print()
        print("Chatterbox-Turbo usa voice cloning para generar voces naturales.")
        print()
        print("Opciones:")
        print("  1. Voz default del modelo (sin configuración adicional)")
        print("  2. Voice cloning con audio de referencia")
        print()
        print("Para usar voice cloning:")
        print("  - Graba 5-10 segundos de audio de referencia (.wav o .mp3)")
        print("  - Configura en settings.json:")
        print('    "chatterbox": {')
        print('      "voice_sample": "/path/to/reference.wav"')
        print('    }')
        print()
        print("Ajustar expresividad (opcional):")
        print('  "chatterbox": {')
        print('    "exaggeration": 1.0  // 0.0 = monotone, 2.0 = dramatic')
        print('  }')


def get_tts_engine(settings: dict) -> TTSEngine:
    """
    Factory function para obtener el motor TTS según configuración.

    Args:
        settings: Configuración cargada desde settings.json

    Returns:
        Instancia de TTSEngine (SystemTTS o ChatterboxTurboTTS)
    """
    engine_type = settings.get("tts_engine", "system")
    fallback_to_system = settings.get("fallback_to_system", True)

    if engine_type == "chatterbox":
        try:
            return ChatterboxTurboTTS(settings)
        except (ImportError, RuntimeError) as e:
            print(f"[voice-notifications:speak] Error con Chatterbox-Turbo: {e}", file=sys.stderr)

            if fallback_to_system:
                print("[voice-notifications:speak] Usando TTS del sistema como fallback", file=sys.stderr)
                return SystemTTS(settings)
            else:
                print("[voice-notifications:speak] Fallback deshabilitado, abortando", file=sys.stderr)
                sys.exit(1)

    # Default: system TTS
    return SystemTTS(settings)


def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Voice Notifications TTS - Sintetiza texto a voz usando sistema TTS o Chatterbox-Turbo"
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Texto a sintetizar y reproducir"
    )

    parser.add_argument(
        "--voice",
        type=str,
        help="Nombre de la voz (solo para system TTS, ej: Mónica, Paulina)"
    )

    parser.add_argument(
        "--rate",
        type=int,
        help="Velocidad en palabras por minuto (solo para system TTS, default: 200)"
    )

    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="Mostrar voces disponibles"
    )

    args = parser.parse_args()

    # Cargar settings
    settings = load_settings()

    # Obtener engine
    try:
        engine = get_tts_engine(settings)
    except Exception as e:
        print(f"[voice-notifications:speak] Error inicializando TTS engine: {e}", file=sys.stderr)
        sys.exit(1)

    # Ejecutar acción
    if args.list_voices:
        engine.list_voices()
    elif args.text:
        try:
            # Para SystemTTS, pasar voice/rate si especificados
            if isinstance(engine, SystemTTS):
                engine.speak(args.text, voice=args.voice, rate=args.rate)
            else:
                # Para Chatterbox, ignorar voice/rate
                engine.speak(args.text)
        except Exception as e:
            print(f"[voice-notifications:speak] Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
