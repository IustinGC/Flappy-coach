"""Support agent introduction and ElevenLabs TTS helpers.

This module keeps the agent-specific logic separate from the game loop.
"""
from dataclasses import dataclass
import os
from typing import Optional

import requests


ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"


@dataclass
class ElevenLabsTTS:
    """Simple ElevenLabs Text-to-Speech client.

    Attributes:
        api_key: ElevenLabs API key. If not provided, it will be read from the
            ELEVENLABS_API_KEY environment variable.
        voice_id: ID of the ElevenLabs voice to use.
        model_id: Optional model identifier. ElevenLabs defaults work if this
            is omitted.
    """

    voice_id: str
    api_key: Optional[str] = None
    model_id: Optional[str] = None

    def synthesize(self, text: str, output_path: str) -> str:
        """Convert ``text`` to speech and save it to ``output_path``.

        Returns the path to the written audio file.
        """
        api_key = self.api_key or os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ElevenLabs API key missing. Set ELEVENLABS_API_KEY.")

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        payload = {"text": text}
        if self.model_id:
            payload["model_id"] = self.model_id

        response = requests.post(
            f"{ELEVENLABS_TTS_URL}/{self.voice_id}", headers=headers, json=payload
        )
        response.raise_for_status()

        with open(output_path, "wb") as audio_file:
            audio_file.write(response.content)

        return output_path


def build_introduction_message() -> str:
    """Return the default introduction message for the support agent."""

    return (
        "Hey! I am an agent designed to provide you support while you are playing "
        "Flappy Bird. Feel free to talk to me about your frustrations!"
    )


def synthesize_introduction(tts_client: ElevenLabsTTS, output_path: str) -> str:
    """Generate an audio file containing the agent introduction.

    Args:
        tts_client: Configured ElevenLabsTTS client.
        output_path: Path where the introduction audio should be written.

    Returns:
        The path to the written audio file.
    """

    intro_text = build_introduction_message()
    return tts_client.synthesize(intro_text, output_path)
