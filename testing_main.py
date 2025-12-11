import time
import asyncio
import threading
import queue
import pygame
from google.adk.runners import InMemoryRunner
from google.genai import types 
from flap import FlappyGame
from speech_tools import Environment
from agent_def import flappy_agent
import agent_audio_manager 

# --- Worker Thread (1 recurring channel for the agent, not creating new threads every time) ---
def agent_worker(runner, session_id, input_queue, output_queue):
    async def processing_loop():
        print(" [System] Agent Brain Online (Background Thread)")
        while True:
            loop = asyncio.get_running_loop()
            try:
                msg_context = await loop.run_in_executor(None, input_queue.get)
            except Exception:
                break
            if msg_context is None: break

            try:
                agent_input = types.Content(role="user", parts=[types.Part(text=msg_context)])
                async for event in runner.run_async(user_id="player_1", session_id=session_id, new_message=agent_input):
                    if event.content and event.content.parts:
                        part = event.content.parts[0]
                        if part.text:
                            output_queue.put(part.text)
                            break 
            except Exception as e:
                print(f"[Worker] Agent Brain Error: {e}")
    asyncio.run(processing_loop())

def main():
    game = FlappyGame()
    env = Environment()
    runner = InMemoryRunner(agent=flappy_agent, app_name="flappy_bird_agent")
    
    agent_input_queue = queue.Queue()
    agent_output_queue = queue.Queue()

    print("Initializing Agent Session...")
    session = asyncio.run(runner.session_service.create_session(app_name="flappy_bird_agent", user_id="player_1"))
    
    t = threading.Thread(target=agent_worker, args=(runner, session.id, agent_input_queue, agent_output_queue), daemon=True)
    t.start()

    print("--- Flappy Bird Agent Session Started ---")

    # --- Safe Shutdown State ---
    shutdown_timer = None 

    running = True
    while running:
        # --- Update Environment ---
        env.update()
        
        # BRIDGE: Tell Reflex System if LLM is busy, so it doesn't talk over or interupt
        is_thinking = not agent_input_queue.empty() or not agent_output_queue.empty()
        agent_audio_manager.set_llm_busy_state(env.is_speaking or is_thinking)

        # --- Check for User Voice Input ---
        # If we are shutting down, stop listening to the user.
        if shutdown_timer is None:
            user_text = env.get_latest_input()
        else:
            user_text = None

        if user_text:
            print(f"\n[USER] 🗣️ Said: {user_text}")
            clean_text = user_text.strip().lower()

            # --- FILTER 1: Ghost Inputs ---
            if clean_text.startswith("(") or len(clean_text) < 2:
                print(f"[SYSTEM] Ignoring ghost input: {clean_text}")
                user_text = None 
            
            # --- FILTER 2: Stop Command ---
            stop_phrases = ["i want to stop", "stop now", "end the game", "i'm done"]
            if any(phrase in clean_text for phrase in stop_phrases):
                print("[SYSTEM] Stop command detected. Shutting down in 5s...")
                # 1. Play Outro
                agent_audio_manager.play_outro()
                # 2. Disable Agent (Stop listening)
                game.agent_enabled = False 
                # 3. Start The Safe Shutdown Timer
                # We give it 7 seconds for the audio to play out smoothly.
                shutdown_timer = time.time() + 7.0
                
                user_text = None 
            
            # --- Process Valid Input ---
            if user_text:
                state = game.get_state()
                context_str = (
                    f"[Event: {'death' if state['loss_count'] > 0 else 'playing'}, "
                    f"Score: {state['score']}] "
                    f"User said: \"{user_text}\""
                )
                print(f"[AGENT] Sending to LLM...")
                agent_input_queue.put(context_str)

        # --- Check for LLM Output ---
        if shutdown_timer is None: # Don't speak new ideas if shutting down
            if not agent_output_queue.empty():
                if not pygame.mixer.Channel(0).get_busy():
                    try:
                        response_text = agent_output_queue.get_nowait()
                        print(f"[AGENT] Idea ready: {response_text}")
                        env.speak_to_user(response_text)
                    except queue.Empty:
                        pass

        # --- Agent Trigger Logic ---
        if game.agent_enabled and shutdown_timer is None:
            state = game.get_state()
            if state['loss_count'] > 0 and not state['game_active']:
                 env.listen_to_user(duration=4.5)

        # --- Step the Game ---
        if running:
            running = game.frame_step()
            
        # --- Handle Safe Shutdown ---
        if shutdown_timer is not None:
            # If the timer has expired, NOW we close the window.
            if time.time() > shutdown_timer:
                print("[SYSTEM] Audio finished. Exiting safely.")
                running = False

    # pygame cleanup
    pygame.quit()

if __name__ == "__main__":
    main()