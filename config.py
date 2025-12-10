VOICE_ID = "pNInz6obpgDQGcFmaJgB"
MODEL_ID = "eleven_multilingual_v2" # low latency model (allegedly, I have not played around with this)
GEMINI_MODEL = "gemini-2.5-flash"  # fast, big context window, and it's only 0.3 euros per million tokens
# gonna switch to "gemini-2.0-flash" if it gets too expensive (0.1 euros per million tokens)
GAME_LOSS_THRESHOLD = 5
GAME_TIME_THRESHOLD_SEC = 60

import os
from dotenv import load_dotenv
load_dotenv()

EL_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 