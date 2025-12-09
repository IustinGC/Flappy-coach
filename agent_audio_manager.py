import os
import random
import pygame
import time

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
_agent_channel = None

# --- Scheduling State ---
_pending_sound = None  # The sound waiting to be played
_scheduled_play_time = 0.0  # The exact timestamp when it should start


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
    Called every frame by the game loop.
    Checks if a scheduled sound is ready to be played.
    """
    global _agent_channel, _pending_sound, _scheduled_play_time

    if _pending_sound is None:
        return

    # If enough time has passed since we scheduled the sound
    if time.time() >= _scheduled_time:
        # Verify one last time that the channel is actually free
        if not _agent_channel.get_busy():
            print("[AgentSounds] Delay over -> Playing now.")
            _agent_channel.play(_pending_sound)

        # Clear the schedule (it's either played or discarded if busy)
        _pending_sound = None


def _attempt_play_sound(sound, label: str):
    """
    1. If Agent is speaking -> Ignore.
    2. If Agent is 'thinking' (waiting to speak) -> Ignore.
    3. Otherwise -> Schedule the sound for a brief moment in the future.
    """
    global _agent_channel, _pending_sound, _scheduled_time

    if sound is None or _agent_channel is None:
        return

    # Check 1: Is the agent currently outputting audio?
    if _agent_channel.get_busy():
        return

    # Check 2: Is the agent currently "thinking" about a previous event?
    # (i.e., we already have a sound waiting in the delay buffer)
    if _pending_sound is not None:
        return

    # If free, schedule the sound
    _pending_sound = sound

    # Add a small random delay (e.g., 0.2 to 0.5 seconds)
    # This makes the agent feel like it's processing what happened
    delay = random.uniform(0.2, 0.5)
    _scheduled_time = time.time() + delay

    print(f"[AgentSounds] Event '{label}' accepted. Will speak in {round(delay, 2)}s...")


def _play_random(sounds, label: str):
    if not sounds:
        return
    snd = random.choice(sounds)
    _attempt_play_sound(snd, label)


# ---------- Public helpers ----------

def play_intro():
    _attempt_play_sound(_intro_sound, "intro")


def play_outro():
    _attempt_play_sound(_outro_sound, "outro")


def play_pipe_loss():
    _play_random(_pipe_loss_sounds, "pipe_loss")


def play_ground_loss():
    _play_random(_ground_loss_sounds, "ground_loss")


def play_high_score():
    _play_random(_score_sounds, "high_score")


def play_game_win():
    _play_random(_win_sounds, "game_win")