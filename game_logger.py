# game_logger.py
"""
Very simple logger:
session_log = {
    "game_1": { ...summary... },
    "game_2": { ...summary... },
    ...
}
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import time


def init_session(log_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Create an empty text file and return (session_log, log_path).
    Call once when a NEW PLAYER starts.
    """
    path = Path(log_path)
    path.write_text("{}", encoding="utf-8")
    return {}, log_path


def start_game(session_log: Dict[str, Any],
               high_score_before: int,
               loss_count_before: int) -> str:
    """
    Create a new summary entry for a game and return its key, e.g. 'game_1'.
    """
    game_idx = len(session_log) + 1
    key = f"game_{game_idx}"

    session_log[key] = {
        "game_id": game_idx,
        "start_time": time.time(),
        "end_time": None,
        "duration_ticks": 0,
        "final_score": None,
        "high_score_before": int(high_score_before),
        "high_score_after": None,
        "loss_count_before": int(loss_count_before),
        "loss_count_after": None,
        "death_cause": None,
    }
    return key


def finish_game(session_log: Dict[str, Any],
                game_key: str,
                duration_ticks: int,
                final_score: int,
                high_score_after: int,
                loss_count_after: int,
                death_cause: str) -> None:
    """
    Fill the summary for a game at the end (death).
    """
    g = session_log[game_key]
    g["end_time"] = time.time()
    g["duration_ticks"] = int(duration_ticks)
    g["final_score"] = int(final_score)
    g["high_score_after"] = int(high_score_after)
    g["loss_count_after"] = int(loss_count_after)
    g["death_cause"] = str(death_cause)


def save_session(log_path: str, session_log: Dict[str, Any]) -> None:
    """
    Write the whole session_log dict to the text file as a Python dict literal.
    """
    Path(log_path).write_text(repr(session_log), encoding="utf-8")
