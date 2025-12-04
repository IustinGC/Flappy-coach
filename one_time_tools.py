import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from dotenv import load_dotenv
import config

api_key = config.API_KEY
voice_id = config.VOICE_ID
client = ElevenLabs(api_key=api_key)

# Script definition. Dictionary format for simplicity: "filename": "the actual text"
script = {
    "intro_msg": "Hey! I am an agent designed to provide you support while you are playing Flappy Bird. Feel free to talk to me about your frustrations!",

    "outro_msg": "Very well. You've done great! Thanks for playing and relying on me during this test. The humans will now give you a short survey about your experience. Have a great day!",

    # --- Pipe loss: empathic support ---
    "pipe_loss_1": "Ouch, that pipe came out of nowhere. Anyone would be frustrated by that.",
    "pipe_loss_2": "You clipped the pipe by a pixel. That kind of loss feels really unfair.",
    "pipe_loss_3": "You were so close to slipping through that gap. It makes sense if that stings.",
    "pipe_loss_4": "That pipe timing is brutal. Feeling annoyed at it is completely valid.",
    "pipe_loss_5": "You hit the pipe again, but that doesn’t mean you’re bad. It just means the game is unforgiving.",
    "pipe_loss_6": "You grazed the pipe — that’s the kind of tiny mistake that can feel way bigger than it is.",
    "pipe_loss_7": "Running into the pipe like that can feel like all your focus was for nothing. It’s okay to be upset.",
    "pipe_loss_8": "The pipes punish even the smallest missteps. No wonder this is getting on your nerves.",
    "pipe_loss_9": "You lined it up almost perfectly, and the pipe still won. It’s normal to feel discouraged by that.",
    "pipe_loss_10": "The pipes don’t leave much room for error. Your frustration fits the situation.",
    "pipe_loss_11": "That collision with the pipe looked harsh. It’s okay if your first reaction is just, ‘Seriously?’",
    "pipe_loss_12": "You threaded through so many pipes before that one. Losing there is bound to feel disappointing.",
    "pipe_loss_13": "The pipe got you again, but it also means you were pushing into the hard part of the run.",
    "pipe_loss_14": "That was a tough gap to hit. Being annoyed with it doesn’t mean you’re overreacting.",
    "pipe_loss_15": "You crashed into the pipe, but you also got yourself all the way there. That effort still counts.",
    "pipe_loss_16": "You made it so far through the pipes before that one mistake. It’s okay if that feels heavy.",
    "pipe_loss_17": "Another pipe, another hit. It makes sense if you’re starting to feel worn down by it.",
    "pipe_loss_18": "You were almost past that obstacle when it went wrong. That ‘almost’ can be really painful.",
    "pipe_loss_19": "The timing on those pipes is demanding. Your brain is doing a lot, even if the result isn’t what you wanted.",
    "pipe_loss_20": "You’ve taken a lot of hits from these pipes. Your tiredness and irritation are completely understandable.",
    "pipe_loss_21": "You keep challenging the same obstacle and sometimes it wins. That repetition is exhausting, and that’s okay to admit.",
    "pipe_loss_22": "That pipe punished you quickly. It’s okay if you need to just sigh and stare at the screen for a second.",

    # --- Ground loss: empathic support ---
    "ground_loss_1": "Falling into the ground like that is such a deflating way to lose. It’s okay to feel drained by it.",
    "ground_loss_2": "You slowly dropped to the ground there — that kind of slow fail can feel especially heavy.",
    "ground_loss_3": "Hitting the ground after fighting gravity for so long can feel like all your effort slipped away.",
    "ground_loss_4": "You just sank down. That sort of ending can feel more sad than dramatic, and that’s okay.",
    "ground_loss_5": "Gravity wins sometimes. It’s normal if that makes you feel like you’re not in control.",
    "ground_loss_6": "Watching the bird fall like that can be weirdly emotional. You’re allowed to feel that.",
    "ground_loss_7": "You didn’t crash into anything flashy, you just fell. That ‘quiet’ loss can still sting.",
    "ground_loss_8": "You were trying to stay up and still ended up on the ground. Feeling disappointed makes sense.",
    "ground_loss_9": "The ground loss is so final — it just stops. It’s okay if that feels a bit hopeless in the moment.",
    "ground_loss_10": "You slowly lost height there. It’s normal if you’re thinking, ‘Why can’t I just keep it together?’",
    "ground_loss_11": "Dropping into the ground like that can make you feel clumsy, even though the game is genuinely hard.",
    "ground_loss_12": "It wasn’t a dramatic crash, just a fall. Those subtle failures can be the most frustrating.",
    "ground_loss_13": "You kept trying to flap, and still hit the ground. That can really chip away at your patience.",
    "ground_loss_14": "Falling out of the sky like that is a harsh reminder that the game doesn’t cut you any slack.",
    "ground_loss_15": "You drifted down until there was nowhere else to go. It’s okay if that feels a bit like giving up, even though it isn’t.",
    "ground_loss_16": "Hitting the ground again can make it feel like nothing is improving. That’s a heavy feeling to sit with.",
    "ground_loss_17": "You spent all that time staying alive and then just dropped. It makes sense if that feels unfair to you.",
    "ground_loss_18": "Sometimes it’s not a big mistake, just a slow fall. Those can hurt in a quiet, persistent way.",
    "ground_loss_19": "You fell, but you also kept the run going up to that point. That effort doesn’t disappear just because of the ending.",
    "ground_loss_20": "Seeing the bird slide into the ground can make you feel like you’re failing, but you’re still here trying.",
    "ground_loss_21": "You hit the ground this time, but it doesn’t erase all the small bits of control you showed on the way down.",

    # --- High score: praising support ---
    "score_1": "New high score! Nice job, that took persistence.",
    "score_2": "You beat your record! That’s really impressive.",
    "score_3": "New personal best! All those attempts are starting to pay off.",
    "score_4": "Hey, that’s a new high score! You’ve earned a moment to feel proud.",
    "score_5": "You just went further than before — proof that you’re improving.",
    "score_6": "Look at that, a new record. You stuck with it, even when it was annoying.",
    "score_7": "That run was great. You pushed past where you usually give up.",
    "score_8": "New high score unlocked! It’s okay to actually enjoy this win for a bit.",

    # --- Game win: strong praise / closure inside a run ---
    "win_1": "You actually beat the game! That’s seriously impressive.",
    "win_2": "You reached the goal! That took focus and persistence.",
    "win_3": "You did it. You made it all the way through — nicely done.",
    "win_4": "That’s a full clear. You kept going despite all those crashes.",
    "win_5": "You won the game. It’s not just luck, you really adapted and improved.",
}

# make the folder if it doesn't exist
if not os.path.exists("assets/audio"):
    os.makedirs("assets/audio")

# time to loop through the script and save the files
print("Generating audio assets...")

for filename, text in script.items():
    print(f"Generating: {filename}...")

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2"
    )

    save_path = f"assets/audio/{filename}.mp3"
    save(audio, save_path)

print("All done! files have been saved in 'assets/audio/'.")