import time
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types  # <--- Required for Content/Part
from flap import FlappyGame
from speech_tools import Environment
from agent_def import flappy_agent

def main():
    # 1. Initialize Game & Environment
    game = FlappyGame()
    env = Environment()
    
    # 2. Initialize the Brain (Runner)
    # We give it an app_name for the session service
    runner = InMemoryRunner(agent=flappy_agent, app_name="flappy_bird_agent")

    # 3. Create a Session (One-time setup)
    # We use asyncio.run just for this setup step because create_session is async.
    # This ensures we have a valid session_id for the run() loop later.
    print("Initializing Agent Session...")
    session = asyncio.run(
        runner.session_service.create_session(
            app_name="flappy_bird_agent", 
            user_id="player_1"
        )
    )
    current_session_id = session.id

    print("--- Flappy Bird Agent Session Started ---")
    print("Controls: Space to Jump, 'R' to Restart.")

    running = True
    while running:
        # --- A. Update Audio Environment ---
        env.update()

        # --- B. Check for User Voice Input ---
        user_text = env.get_latest_input()
        
        if user_text:
            print(f"\n[USER] 🗣️ Said: {user_text}")
            
            # 1. Build Context
            state = game.get_state()
            context_str = (
                f"[Event: {'death' if state['loss_count'] > 0 else 'playing'}, "
                f"Score: {state['score']}] "
                f"User said: \"{user_text}\""
            )
            
            # 2. Package into ADK Content Type
            # The Runner expects a 'types.Content' object, not a string.
            agent_input = types.Content(
                role="user",
                parts=[types.Part(text=context_str)]
            )
            
            # 3. Run the Agent (Synchronous Block)
            try:
                print(f"[AGENT] 🧠 Thinking...")
                
                # FIX: Use keyword args (user_id, session_id, new_message)
                # FIX: Iterate over the result (it yields events)
                for event in runner.run(
                    user_id="player_1",
                    session_id=current_session_id,
                    new_message=agent_input
                ):
                    # We check if the event has text content from the agent
                    if event.content and event.content.parts:
                        part = event.content.parts[0]
                        if part.text:
                            response_text = part.text
                            # 4. Speak Response
                            env.speak_to_user(response_text)
                            # We break after the first text response to avoid duplicates
                            break 
                            
            except Exception as e:
                print(f"[ERROR] Agent failed to reply: {e}")

        # --- C. Agent Trigger Logic ---
        if game.agent_enabled:
            state = game.get_state()
            # TRIGGER: "Game Over" Screen
            if state['loss_count'] > 0 and not state['game_active']:
                 env.listen_to_user(duration=3.5)

        # --- D. Step the Game ---
        running = game.frame_step()

if __name__ == "__main__":
    main()