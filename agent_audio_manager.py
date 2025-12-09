import os
import random
import pygame
import time

# --- Configuration & Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "audio")


# Helper to keep the dictionary clean
def get_path(filename):
    return os.path.join(SOUND_DIR, filename)


# --- The Dictionary Structure ---
# Mapped to the specific texts provided in support_responses.py
AGENT_AUDIO_PATHS = {
    "LOSS": {
        "PIPE": {
            "p_loss_01": get_path("pipe_loss_1.mp3"),
            "p_loss_02": get_path("pipe_loss_2.mp3"),
            "p_loss_03": get_path("pipe_loss_3.mp3"),
            "p_loss_04": get_path("pipe_loss_4.mp3"),
            "p_loss_05": get_path("pipe_loss_5.mp3"),
            "p_loss_06": get_path("pipe_loss_6.mp3"),
            "p_loss_07": get_path("pipe_loss_7.mp3"),
            "p_loss_08": get_path("pipe_loss_8.mp3"),
            "p_loss_09": get_path("pipe_loss_9.mp3"),
            "p_loss_10": get_path("pipe_loss_10.mp3"),
            "p_loss_11": get_path("pipe_loss_11.mp3"),
            "p_loss_12": get_path("pipe_loss_12.mp3"),
            "p_loss_13": get_path("pipe_loss_13.mp3"),
            "p_loss_14": get_path("pipe_loss_14.mp3"),
            "p_loss_15": get_path("pipe_loss_15.mp3"),
            "p_loss_16": get_path("pipe_loss_16.mp3"),
            "p_loss_17": get_path("pipe_loss_17.mp3"),
            "p_loss_18": get_path("pipe_loss_18.mp3"),
            "p_loss_19": get_path("pipe_loss_19.mp3"),
            "p_loss_20": get_path("pipe_loss_20.mp3"),
            "p_loss_21": get_path("pipe_loss_21.mp3"),
            "p_loss_22": get_path("pipe_loss_22.mp3"),
        },
        "GROUND": {
            "g_loss_01": get_path("ground_loss_1.mp3"),
            "g_loss_02": get_path("ground_loss_2.mp3"),
            "g_loss_03": get_path("ground_loss_3.mp3"),
            "g_loss_04": get_path("ground_loss_4.mp3"),
            "g_loss_05": get_path("ground_loss_5.mp3"),
            "g_loss_06": get_path("ground_loss_6.mp3"),
            "g_loss_07": get_path("ground_loss_7.mp3"),
            "g_loss_08": get_path("ground_loss_8.mp3"),
            "g_loss_09": get_path("ground_loss_9.mp3"),
            "g_loss_10": get_path("ground_loss_10.mp3"),
            "g_loss_11": get_path("ground_loss_11.mp3"),
            "g_loss_12": get_path("ground_loss_12.mp3"),
            "g_loss_13": get_path("ground_loss_13.mp3"),
            "g_loss_14": get_path("ground_loss_14.mp3"),
            "g_loss_15": get_path("ground_loss_15.mp3"),
            "g_loss_16": get_path("ground_loss_16.mp3"),
            "g_loss_17": get_path("ground_loss_17.mp3"),
            "g_loss_18": get_path("ground_loss_18.mp3"),
            "g_loss_19": get_path("ground_loss_19.mp3"),
            "g_loss_20": get_path("ground_loss_20.mp3"),
            "g_loss_21": get_path("ground_loss_21.mp3"),
        }
    },
    "ACHIEVEMENT": {
        "HIGH_SCORE": {
            "hs_01": get_path("score_1.mp3"),
            "hs_02": get_path("score_2.mp3"),
            "hs_03": get_path("score_3.mp3"),
            "hs_04": get_path("score_4.mp3"),
            "hs_05": get_path("score_5.mp3"),
            "hs_06": get_path("score_6.mp3"),
            "hs_07": get_path("score_7.mp3"),
            "hs_08": get_path("score_8.mp3"),
        },
        "WIN": {
            "win_01": get_path("win_1.mp3"),
            "win_02": get_path("win_2.mp3"),
            "win_03": get_path("win_3.mp3"),
            "win_04": get_path("win_4.mp3"),
            "win_05": get_path("win_5.mp3"),
        }
    },
    "MISC": {
        "intro": get_path("intro_msg.mp3"),
        "outro": get_path("outro_msg.mp3")
    }
}

# --- Global State ---
_intro_sound = None
_outro_sound = None

_pipe_loss_sounds = []
_ground_loss_sounds = []
_score_sounds = []
_win_sounds = []

_initialized = False
_agent_channel = None

# --- Scheduling State (for non-blocking delays) ---
_pending_sound = None  # The sound waiting to be played
_scheduled_play_time = 0.0  # The exact timestamp when it should start


def _load_sound(abs_path: str):
    """Loads a single sound file from an absolute path."""
    if not os.path.exists(abs_path):
        # print(f"[AgentSounds] MISSING file: {abs_path}")
        return None
    try:
        snd = pygame.mixer.Sound(abs_path)
        return snd
    except pygame.error as e:
        print(f"[AgentSounds] Error loading {abs_path}: {e}")
        return None


def _load_from_dict(path_dict):
    """Iterates over a dictionary of paths and returns a list of loaded sounds."""
    loaded_sounds = []
    # Sorting keys ensures p_loss_01 is loaded before p_loss_02, etc.
    for key in sorted(path_dict.keys()):
        path = path_dict[key]
        snd = _load_sound(path)
        if snd is not None:
            loaded_sounds.append(snd)
    return loaded_sounds


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

    # --- Load Sounds from Dictionary ---
    print("[AgentSounds] Loading audio assets...")

    # Misc
    _intro_sound = _load_sound(AGENT_AUDIO_PATHS["MISC"]["intro"])
    _outro_sound = _load_sound(AGENT_AUDIO_PATHS["MISC"]["outro"])

    # Losses
    _pipe_loss_sounds = _load_from_dict(AGENT_AUDIO_PATHS["LOSS"]["PIPE"])
    _ground_loss_sounds = _load_from_dict(AGENT_AUDIO_PATHS["LOSS"]["GROUND"])

    # Achievements
    _score_sounds = _load_from_dict(AGENT_AUDIO_PATHS["ACHIEVEMENT"]["HIGH_SCORE"])
    _win_sounds = _load_from_dict(AGENT_AUDIO_PATHS["ACHIEVEMENT"]["WIN"])

    _initialized = True
    print(
        f"[AgentSounds] Loaded: {_pipe_loss_sounds.__len__()} pipe, {_ground_loss_sounds.__len__()} ground, {_score_sounds.__len__()} score, {_win_sounds.__len__()} win.")


def update_agent_audio():
    """
    Called every frame by the game loop.
    Checks if a scheduled sound is ready to be played.
    """
    global _agent_channel, _pending_sound, _scheduled_play_time

    if _pending_sound is None:
        return

    # If enough time has passed since we scheduled the sound
    if time.time() >= _scheduled_play_time:
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
    global _agent_channel, _pending_sound, _scheduled_play_time

    if sound is None or _agent_channel is None:
        return

    # Check 1: Is the agent currently outputting audio?
    if _agent_channel.get_busy():
        return

    # Check 2: Is the agent currently "thinking" about a previous event?
    if _pending_sound is not None:
        return

    # If free, schedule the sound
    _pending_sound = sound

    # This makes the agent feel like it's processing what happened
    delay = random.uniform(0.2, 0.5)
    _scheduled_play_time = time.time() + delay

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