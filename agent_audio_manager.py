# agent_sounds.py

import os
import random
import pygame

# Folder with your audio files:
# .../Flappy_Coach/Flappy-coach/assets/audio/*.mp3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "audio")
EXT = ".mp3"

print("[AgentSounds] SOUND_DIR =", SOUND_DIR)

_intro_sound = None
_outro_sound = None
_pipe_loss_sounds = []
_ground_loss_sounds = []
_score_sounds = []
_win_sounds = []
_initialized = False


def _load_sound(filename: str):
    path = os.path.join(SOUND_DIR, filename)
    print(f"[AgentSounds] Trying to load: {path}")
    if not os.path.exists(path):
        print(f"[AgentSounds] MISSING file: {path}")
        return None
    try:
        snd = pygame.mixer.Sound(path)
        print(f"[AgentSounds] Loaded: {path}")
        return snd
    except pygame.error as e:
        print(f"[AgentSounds] Error loading {path}: {e}")
        return None


def _load_group(prefix: str, max_index: int):
    """Load files prefix_1..prefix_max_index (skipping missing ones)."""
    sounds = []
    for i in range(1, max_index + 1):
        filename = f"{prefix}{i}{EXT}"
        s = _load_sound(filename)
        if s is not None:
            sounds.append(s)
    if not sounds:
        print(f"[AgentSounds] WARNING: no sounds loaded for prefix '{prefix}'")
    return sounds


def init_agent_sounds():
    """Call once after pygame.mixer.init()."""
    global _initialized
    global _intro_sound, _outro_sound
    global _pipe_loss_sounds, _ground_loss_sounds, _score_sounds, _win_sounds

    if _initialized:
        return

    if pygame.mixer.get_init() is None:
        pygame.mixer.init()

    print("[AgentSounds] Initializing...")

    # Single files
    _intro_sound = _load_sound("intro_msg" + EXT)
    _outro_sound = _load_sound("outro_msg" + EXT)  # when you create it

    # Groups – adjust counts if you have fewer/more files
    _pipe_loss_sounds = _load_group("pipe_loss_", 22)
    _ground_loss_sounds = _load_group("ground_loss_", 21)
    _score_sounds = _load_group("score_", 8)
    _win_sounds = _load_group("win_", 5)

    _initialized = True
    print("[AgentSounds] Initialization complete.")


def _play(sound, label: str):
    if sound is None:
        print(f"[AgentSounds] No sound loaded for {label}")
        return
    print(f"[AgentSounds] Playing {label}")
    sound.play()


def _play_random(sounds, label: str):
    if not sounds:
        print(f"[AgentSounds] No sounds available for {label}")
        return
    snd = random.choice(sounds)
    print(f"[AgentSounds] Playing random {label}")
    snd.play()


# ---------- Public helpers you call from the game ----------

def play_intro():
    _play(_intro_sound, "intro")


def play_outro():
    _play(_outro_sound, "outro")


def play_pipe_loss():
    _play_random(_pipe_loss_sounds, "pipe_loss")


def play_ground_loss():
    _play_random(_ground_loss_sounds, "ground_loss")


def play_high_score():
    _play_random(_score_sounds, "high_score")


def play_game_win():
    _play_random(_win_sounds, "game_win")
