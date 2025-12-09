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
_agent_channel = None

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
    # This prevents other game sounds (SFX) from accidentally using this channel
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
    No-op: Kept for compatibility with main.py calls. 
    We no longer need to check queues or timers here.
    """
    pass


def _attempt_play_sound(sound, label: str):
    """
    The Core Logic:
    1. Check if the agent is ALREADY speaking.
    2. If YES: Drop the new sound (ignore it completely).
    3. If NO: Play the new sound immediately.
    """
    global _agent_channel

    if sound is None or _agent_channel is None:
        return

    # Check if the channel is currently playing audio
    if _agent_channel.get_busy():
        # Agent is talking. Do not interrupt. Do not queue.
        # print(f"[AgentSounds] Ignored '{label}' - Agent is busy.")
        return

    # Channel is free; play the sound.
    print(f"[AgentSounds] Playing: {label}")
    _agent_channel.play(sound)


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