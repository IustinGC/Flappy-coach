# game_logger.py
from ast import literal_eval
"""
Game logger.

Internal structure during runtime:
    session_log = {
        1: {
            "game_id": 1,
            "start_time": ...,
            "end_time": ...,
            ...
        },
        2: { ... },
        ...
    }

When saving, we convert this to a flat dict:
    {
        1: "ID: 1\nStart: ...\nEnd: ...\nDuration (ticks): ...\nScore: ...\n...",
        2: "ID: 2\nStart: ...\n...",
        ...
    }

and write that dict literal to the log file.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import time


def init_session(log_path: str) -> Tuple[Dict[int, Any], str]:
    """
    Create an empty log file and return (session_log, log_path).
    Call once when a NEW PLAYER starts.
    """
    path = Path(log_path)
    path.write_text("{}", encoding="utf-8")
    return {}, log_path


def start_game(session_log: Dict[int, Any],
               high_score_before: int,
               loss_count_before: int) -> int:
    """
    Create a new summary entry for a game and return its numeric game_id.
    """
    game_id = len(session_log) + 1

    session_log[game_id] = {
        "game_id": game_id,
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
    return game_id


def finish_game(session_log: Dict[int, Any],
                game_id: int,
                duration_ticks: int,
                final_score: int,
                high_score_after: int,
                loss_count_after: int,
                death_cause: str) -> None:
    """
    Fill the summary for a game at the end (death).
    """
    g = session_log[game_id]
    g["end_time"] = time.time()
    g["duration_ticks"] = int(duration_ticks)
    g["final_score"] = int(final_score)
    g["high_score_after"] = int(high_score_after)
    g["loss_count_after"] = int(loss_count_after)
    g["death_cause"] = str(death_cause)


def _format_game_summary(g: Dict[str, Any]) -> str:
    """
    Return a nice multi-line string for a single game, to be stored as the dict value.
    """
    start_ts = g.get("start_time")
    end_ts = g.get("end_time")

    if start_ts is not None:
        start_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_ts))
    else:
        start_str = "-"

    if end_ts is not None:
        end_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_ts))
    else:
        end_str = "-"

    duration = g.get("duration_ticks", 0)
    score = g.get("final_score")
    hs_before = g.get("high_score_before")
    hs_after = g.get("high_score_after")
    loss_before = g.get("loss_count_before")
    loss_after = g.get("loss_count_after")
    cause = g.get("death_cause")

    return (
        f"ID: {g.get('game_id')}\n"
        f"Start: {start_str}\n"
        f"End: {end_str}\n"
        f"Duration (ticks): {duration}\n"
        f"Score: {score}\n"
        f"High score before: {hs_before}\n"
        f"High score after: {hs_after}\n"
        f"Losses before: {loss_before}\n"
        f"Losses after: {loss_after}\n"
        f"Death cause: {cause}\n"
        f"---"
    )


def save_session(log_path: str, session_log: Dict[int, Any]) -> None:
    """
    Convert the internal nested dict to a flat dict {game_id: summary_string}
    and write that dict literal to file.
    """
    flat: Dict[int, str] = {}

    for game_id, g in session_log.items():
        flat[game_id] = _format_game_summary(g)

    Path(log_path).write_text(repr(flat), encoding="utf-8")


def session_output():
    with open("session_log.txt", "r", encoding="utf-8") as f:
        data = literal_eval(f.read())  # turns the dict literal into a real dict

    for game_id, summary in data.items():
        print(summary)  # this will render the \n as real newlines
        print()  # extra blank line between games
