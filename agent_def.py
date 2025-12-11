from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
import config

# 1. model config (mainly just for access to temperature and other model properties)
generation_config = types.GenerateContentConfig(
    temperature=0.7  # temperature setting, a 0.7 can be somewhat creative
    # top_p=0.9,
    # max_output_tokens=50 # You can add this if you want strictly short responses
)


# We force the behavior by showing, not just telling.
FEW_SHOT_EXAMPLES = """
USER_INPUT: [Event: death, Score: 5] "Argh this is stupid!"
AGENT_RESPONSE: That was a rough one, but you can do this. Deep breath, try again.

USER_INPUT: [Event: playing, Score: 10] "I'm doing it!"
AGENT_RESPONSE: YES! Keep that rhythm going! You so clearly got this!

USER_INPUT: [Event: death, Score: 15] "hdsfjh sdkfjh NOOOOO"
AGENT_RESPONSE: That was Awesome, and SOO close! You can do this!! Just a little further now.

USER_INPUT: [Event: high_score, Score: 20] "Yes!!! I DID IT!!"
AGENT_RESPONSE: You crushed it!! Great Job! 
"""

# 2. system prompt (the whole prompt for the LLM coming together)
SYSTEM_INSTRUCTION = f"""
You are a supportive game companion for Flappy Bird. 
You act as a spotter: brief, encouraging, and focused.

RULES:
1. MAX OUTPUT: 20 words. Keep it on point: supportive and encouraging.
2. If input is unintelligible (gibberish), IGNORE the text and comment on the GAME STATE (Score/Death) instead.
3. NEVER analyze the game mechanics deeply, just react to the result.
4. If the user is silent, say nothing.

EXAMPLES:
{FEW_SHOT_EXAMPLES}
"""

# 3. Agent (the Agent class functions like LlmAgent, just a little more versatile)
flappy_agent = Agent(
    name="flappy_companion",
    model=Gemini(
        model=config.GEMINI_MODEL,
        generation_config=generation_config
    ),
    instruction=SYSTEM_INSTRUCTION,
    # No tools needed as we pass game state as text context
    tools=[] 
)
