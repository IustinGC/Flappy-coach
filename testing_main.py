import time
import asyncio
import threading
import queue
from google.adk.runners import InMemoryRunner
from google.genai import types 
from flap import FlappyGame
from speech_tools import Environment
from agent_def import flappy_agent


# --- Helper Function for Threading ---
def background_agent_think(runner, session_id, agent_input, output_queue):
    """
    Runs the blocking network call in a separate thread.
    Puts the resulting text into the output_queue.
    """
    try:
        # Loop through events (synchronous but in a thread now)
        for event in runner.run(
            user_id="player_1",
            session_id=session_id,
            new_message=agent_input
        ):
            if event.content and event.content.parts:
                part = event.content.parts[0]
                if part.text:
                    # We found text! Put it in the queue and stop.
                    output_queue.put(part.text)
                    break
    except Exception as e:
        print(f"[THREAD ERROR] Agent failed: {e}")
        
def main():
    # 1. Initialize Game & Environment
    game = FlappyGame()
    env = Environment()
    
    # 2. Initialize Brain
    runner = InMemoryRunner(agent=flappy_agent, app_name="flappy_bird_agent")
    
    # 3. Queue for Async Thinking Results
    agent_response_queue = queue.Queue()

    # 4. Session Setup
    print("Initializing Agent Session...")
    session = asyncio.run(
        runner.session_service.create_session(
            app_name="flappy_bird_agent", 
            user_id="player_1"
        )
    )
    current_session_id = session.id

    print("--- Flappy Bird Agent Session Started ---")

    running = True
    while running:
        # --- A. Update Audio Environment ---
        env.update()

        # --- B. Check for User Voice Input ---
        user_text = env.get_latest_input()
        
        if user_text:
            print(f"\n[USER] 🗣️ Said: {user_text}")
            
            # Build Context
            state = game.get_state()
            context_str = (
                f"[Event: {'death' if state['loss_count'] > 0 else 'playing'}, "
                f"Score: {state['score']}] "
                f"User said: \"{user_text}\""
            )
            
            agent_input = types.Content(
                role="user",
                parts=[types.Part(text=context_str)]
            )
            
            # --- THE FIX: Threaded Thinking ---
            print(f"[AGENT] 🧠 Thinking (Background)...")
            t = threading.Thread(
                target=background_agent_think,
                args=(runner, current_session_id, agent_input, agent_response_queue),
                daemon=True
            )
            t.start()
            # The game loop CONTINUES immediately here!

        # --- C. Check for Agent Responses ---
        # Did the thread finish thinking?
        if not agent_response_queue.empty():
            try:
                response_text = agent_response_queue.get_nowait()
                print(f"[AGENT] 💡 Idea ready: {response_text}")
                env.speak_to_user(response_text)
            except queue.Empty:
                pass

        # --- D. Agent Trigger Logic ---
        if game.agent_enabled:
            state = game.get_state()
            if state['loss_count'] > 0 and not state['game_active']:
                 env.listen_to_user(duration=3.5)

        # --- E. Step the Game ---
        running = game.frame_step()

if __name__ == "__main__":
    main()