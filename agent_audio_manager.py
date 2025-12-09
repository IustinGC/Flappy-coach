import os
import random
import pygame

# Folder with your audio files:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "audio")
EXT = ".mp3"

print("[AgentSounds] SOUND_DIR =", SOUND_DIR)

# --- Global State ---
_intro_sound = None
_outro_sound = None
_pipe_loss_sounds = []
_ground_loss_sounds = []
_score_sounds = []
_win_sounds = []

_initialized = False

# --- NEW: Audio Queue & Channel ---
_agent_channel = None
_audio_queue = []  # A list to hold sounds waiting to be spoken


def _load_sound(filename: str):
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.exists(path):
        print(f"[AgentSounds] MISSING file: {path}")
        return None
    try:
        snd = pygame.mixer.Sound(path)
        return snd
    except pygame.error as e:
        print(f"[AgentSounds] Error loading {path}: {e}")
        return None


def _load_group(prefix: str, max_index: int):
    sounds = []
    for i in range(1, max_index + 1):
        filename = f"{prefix}{i}{EXT}"
        s = _load_sound(filename)
        if s is not None:
            sounds.append(s)
    return sounds


def init_agent_sounds():
    """Call once after pygame.mixer.init()."""
    global _initialized, _agent_channel
    global _intro_sound, _outro_sound
    global _pipe_loss_sounds, _ground_loss_sounds, _score_sounds, _win_sounds

    if _initialized:
        return

    if pygame.mixer.get_init() is None:
        pygame.mixer.init()

    # Reserve Channel 0 explicitly for the agent
    pygame.mixer.set_reserved(1)
    _agent_channel = pygame.mixer.Channel(0)

    # Load assets
    _intro_sound = _load_sound("intro_msg" + EXT)
    _outro_sound = _load_sound("outro_msg" + EXT)
    _pipe_loss_sounds = _load_group("pipe_loss_", 22)
    _ground_loss_sounds = _load_group("ground_loss_", 21)
    _score_sounds = _load_group("score_", 8)
    _win_sounds = _load_group("win_", 5)

    _initialized = True
    print("[AgentSounds] Initialization complete.")


def update_agent_audio():
    """
    CRITICAL: Place this in your main game loop!
    Checks if the agent has finished speaking. If so, plays the next sound in queue.
    """
    global _agent_channel, _audio_queue

    if _agent_channel is None:
        return

    # If the agent is silent AND we have sounds waiting...
    if not _agent_channel.get_busy() and len(_audio_queue) > 0:
        next_sound = _audio_queue.pop(0)  # Get the first sound
        print(f"[AgentSounds] Playing queued sound.")
        _agent_channel.play(next_sound)


def _queue_sound(sound, label: str, clear_queue_first: bool = False):
    """
    Handles the logic:
    1. If clear_queue_first=True, we wipe any pending sounds (e.g., High Score)
       so that this new important sound (Death) is the very next thing heard.
    2. We NEVER interrupt the current speaker. We always add to queue.
    """
    global _audio_queue, _agent_channel

    if sound is None:
        return

    # 1. Handle "Death overrides High Score" requirement
    if clear_queue_first:
        if len(_audio_queue) > 0:
            print(f"[AgentSounds] Priority Event ({label}): Cleared {_audio_queue} from queue.")
            _audio_queue.clear()

    # 2. Add to queue (or play immediately if queue is empty and channel is free)
    # We push to queue first to keep logic simple, let update() handle playback.
    _audio_queue.append(sound)

    # Try to play immediately if idle (triggers in this frame)
    update_agent_audio()


def _queue_random(sounds, label: str, clear_queue_first: bool = False):
    if not sounds:
        return
    snd = random.choice(sounds)
    _queue_sound(snd, label, clear_queue_first)


# ---------- Public helpers ----------

def play_intro():
    # Standard queue
    _queue_sound(_intro_sound, "intro")


def play_outro():
    _queue_sound(_outro_sound, "outro")


def play_pipe_loss():
    # Clear Queue = True. 
    # If "High Score" was just queued (from same frame), it gets deleted.
    # The current phrase finishes (channel is not stopped), then this plays.
    _queue_random(_pipe_loss_sounds, "pipe_loss", clear_queue_first=True)


def play_ground_loss():
    # Clear Queue = True.
    _queue_random(_ground_loss_sounds, "ground_loss", clear_queue_first=True)


def play_high_score():
    # Standard queue. 
    # If death happens immediately after, this entry will be wiped by the death function.
    _queue_random(_score_sounds, "high_score")


def play_game_win():
    _queue_random(_win_sounds, "game_win")