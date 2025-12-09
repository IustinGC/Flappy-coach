"""
support_responses.py

Hard-coded, non-LLM responses for the support agent.

This file is meant to be used by the ENVIRONMENT (not the Agent itself)
to react to game events like losses, new high scores, and game wins.

Typical usage:
    from support_responses import (
        AGENT_INTRO_MESSAGE,
        AGENT_OUTRO_MESSAGE,
        get_loss_response,
        get_high_score_response,
        get_game_win_response,
    )

    text_to_say = get_loss_response()
    # pass text_to_say to TTS
"""

from __future__ import annotations

import random


# --- Fixed messages (intro / outro) ---

AGENT_INTRO_MESSAGE: str = (
    "Hey! I am an agent designed to provide you support while you are "
    "playing Flappy Bird. Feel free to talk to me about your frustrations!"
)

AGENT_OUTRO_MESSAGE: str = (
    "Very well. You've done great! Thanks for playing and relying on me "
    "during this test. The humans will now give you a short survey about "
    "your experience. Have a great day!"
)


# --- Loss: empathic support ---

PIPE_LOSS_RESPONSES = [
    "Ouch, that pipe came out of nowhere. Anyone would be frustrated by that.",
    "You clipped the pipe by a pixel. That kind of loss feels really unfair.",
    "You were so close to slipping through that gap. It makes sense if that stings.",
    "That pipe timing is brutal. Feeling annoyed at it is completely valid.",
    "You hit the pipe again, but that doesn’t mean you’re bad. It just means the game is unforgiving.",
    "You grazed the pipe — that’s the kind of tiny mistake that can feel way bigger than it is.",
    "Running into the pipe like that can feel like all your focus was for nothing. It’s okay to be upset.",
    "The pipes punish even the smallest missteps. No wonder this is getting on your nerves.",
    "You lined it up almost perfectly, and the pipe still won. It’s normal to feel discouraged by that.",
    "The pipes don’t leave much room for error. Your frustration fits the situation.",
    "That collision with the pipe looked harsh. It’s okay if your first reaction is just, ‘Seriously?’",
    "You threaded through so many pipes before that one. Losing there is bound to feel disappointing.",
    "The pipe got you again, but it also means you were pushing into the hard part of the run.",
    "That was a tough gap to hit. Being annoyed with it doesn’t mean you’re overreacting.",
    "You crashed into the pipe, but you also got yourself all the way there. That effort still counts.",
    "You made it so far through the pipes before that one mistake. It’s okay if that feels heavy.",
    "Another pipe, another hit. It makes sense if you’re starting to feel worn down by it.",
    "You were almost past that obstacle when it went wrong. That ‘almost’ can be really painful.",
    "The timing on those pipes is demanding. Your brain is doing a lot, even if the result isn’t what you wanted.",
    "You’ve taken a lot of hits from these pipes. Your tiredness and irritation are completely understandable.",
    "You keep challenging the same obstacle and sometimes it wins. That repetition is exhausting, and that’s okay to admit.",
    "That pipe punished you quickly. It’s okay if you need to just sigh and stare at the screen for a second.",
]

GROUND_LOSS_RESPONSES = [
    "Falling into the ground like that is such a deflating way to lose. It’s okay to feel drained by it.",
    "You slowly dropped to the ground there — that kind of slow fail can feel especially heavy.",
    "Hitting the ground after fighting gravity for so long can feel like all your effort slipped away.",
    "You just sank down. That sort of ending can feel more sad than dramatic, and that’s okay.",
    "Gravity wins sometimes. It’s normal if that makes you feel like you’re not in control.",
    "Watching the bird fall like that can be weirdly emotional. You’re allowed to feel that.",
    "You didn’t crash into anything flashy, you just fell. That ‘quiet’ loss can still sting.",
    "You were trying to stay up and still ended up on the ground. Feeling disappointed makes sense.",
    "The ground loss is so final — it just stops. It’s okay if that feels a bit hopeless in the moment.",
    "You slowly lost height there. It’s normal if you’re thinking, ‘Why can’t I just keep it together?’",
    "Dropping into the ground like that can make you feel clumsy, even though the game is genuinely hard.",
    "It wasn’t a dramatic crash, just a fall. Those subtle failures can be the most frustrating.",
    "You kept trying to flap, and still hit the ground. That can really chip away at your patience.",
    "Falling out of the sky like that is a harsh reminder that the game doesn’t cut you any slack.",
    "You drifted down until there was nowhere else to go. It’s okay if that feels a bit like giving up, even though it isn’t.",
    "Hitting the ground again can make it feel like nothing is improving. That’s a heavy feeling to sit with.",
    "You spent all that time staying alive and then just dropped. It makes sense if that feels unfair to you.",
    "Sometimes it’s not a big mistake, just a slow fall. Those can hurt in a quiet, persistent way.",
    "You fell, but you also kept the run going up to that point. That effort doesn’t disappear just because of the ending.",
    "Seeing the bird slide into the ground can make you feel like you’re failing, but you’re still here trying.",
    "You hit the ground this time, but it doesn’t erase all the small bits of control you showed on the way down.",
]


# --- High score: praising support ---

HIGH_SCORE_RESPONSES = [
    "New high score! Nice job, that took persistence.",
    "You beat your record! That’s really impressive.",
    "New personal best! All those attempts are starting to pay off.",
    "Hey, that’s a new high score! You’ve earned a moment to feel proud.",
    "You just went further than before — proof that you’re improving.",
    "Look at that, a new record. You stuck with it, even when it was annoying.",
    "That run was great. You pushed past where you usually give up.",
    "New high score unlocked! It’s okay to actually enjoy this win for a bit.",
]


# --- Game win: strong praise / closure inside a run ---

GAME_WIN_RESPONSES = [
    "You actually beat the game! That’s seriously impressive.",
    "You reached the goal! That took focus and persistence.",
    "You did it. You made it all the way through — nicely done.",
    "That’s a full clear. You kept going despite all those crashes.",
    "You won the game. It’s not just luck, you really adapted and improved.",
]
