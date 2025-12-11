import time
import pygame
from speech_tools import Environment

def test_state_switching():
    pygame.init()
    pygame.mixer.init()
    
    print("--- Initializing Environment ---")
    env = Environment()
    
    print("--- STARTING STATE MACHINE TEST ---")
    
    # State flags for the test
    speech_triggered = False
    listen_triggered = False
    agent_was_speaking = False

    # Run for ~15 seconds (450 frames)
    for frame in range(450):
        # 1. CRITICAL: Update the environment every frame
        env.update()

        # 2. Monitor State Changes (Visual Feedback)
        current_speaking_state = env.is_speaking
        
        # Detect Edge: Just started speaking
        if current_speaking_state and not agent_was_speaking:
            print(f"\n[STATE CHANGE] 🔴 Agent is now BUSY (Frame {frame})")
            agent_was_speaking = True
            
        # Detect Edge: Just finished speaking
        if not current_speaking_state and agent_was_speaking:
            print(f"\n[STATE CHANGE] 🟢 Agent finished speaking. Channel CLEAR (Frame {frame})")
            agent_was_speaking = False

        # --- Trigger 1: Speak at Frame 10 ---
        if frame == 10:
            print(f"\n[TRIGGER] 🗣️ Telling Agent to Speak (Frame {frame})...")
            # Long sentence to ensure it overlaps with Frame 100
            env.speak_to_user("I am currently speaking to test the audio locking mechanism.")
            speech_triggered = True

        # --- Trigger 2: Try to Listen (Smart Polling) ---
        # We start wanting to listen at Frame 100
        if frame >= 100 and not listen_triggered:
            
            # ATTEMPT to listen
            started = env.listen_to_user(duration=4)
            
            if started:
                print(f"\n[SUCCESS] 👂 Listen request ACCEPTED at Frame {frame}!")
                listen_triggered = True
            else:
                # If rejected, we wait for the next frame (Polling)
                if frame % 30 == 0: # Log only occasionally to avoid spam
                    print(f"[WAITING] Listen rejected (Agent is busy)... Frame {frame}")

        # --- Check for STT Results ---
        user_text = env.get_latest_input()
        if user_text:
            print(f"\n[RESULT] 📝 Main Loop received: '{user_text}'")

        # Frame pacing
        time.sleep(0.033)
        if frame % 10 == 0: print(f".", end="", flush=True)

    print("\n--- TEST COMPLETE ---")
    pygame.quit()

if __name__ == "__main__":
    test_state_switching()