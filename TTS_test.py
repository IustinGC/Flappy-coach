from support_agent_responses import ElevenLabsTTS, synthesize_introduction

tts = ElevenLabsTTS(
    voice_id="d60rsXo2p0OwikDR5bS7",
    model_id="eleven_flash_v2_5",
)
audio_path = synthesize_introduction(tts, "assets/audio/agent_intro.mp3")
print(f"Saved intro to {audio_path}")