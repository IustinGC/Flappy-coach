# Flappy Coach

Simple Flappy Bird-inspired game experiments with an emotional support agent.

## Support agent TTS introduction

1. Install dependencies (the TTS helper only requires `requests` in addition to
   the existing game dependencies).
2. Set your ElevenLabs API key in the environment:
   ```bash
   export ELEVENLABS_API_KEY="<your-api-key>"
   ```
   The key only needs permission to call the ElevenLabs Text-to-Speech endpoint
   used by the helper: `POST https://api.elevenlabs.io/v1/text-to-speech/<voice-id>`.
3. Use the helper module to synthesize the agent introduction audio:
   ```python
   from support_agent_introduction import ElevenLabsTTS, synthesize_introduction

   tts = ElevenLabsTTS(voice_id="<elevenlabs-voice-id>")
   audio_path = synthesize_introduction(tts, "agent_intro.mp3")
   print(f"Saved intro to {audio_path}")
   ```
   Optionally, pass `model_id` to `ElevenLabsTTS` if you want to target a
   specific ElevenLabs model.

The introduction text is available via `build_introduction_message()` when you
need it without audio.