from elevenlabs.client import ElevenLabs
import config

api_key = config.EL_API_KEY

if not api_key:
    print("Error: ELEVENLABS_API_KEY not found in .env file.")
    exit()

try:
    client = ElevenLabs(api_key=api_key)
    
    # fetch Subscription Info
    subscription = client.user.subscription.get()

    # extract Data
    used = subscription.character_count
    total = subscription.character_limit
    remaining = total - used
    reset_date = subscription.next_character_count_reset_unix

    print(f"\n---  ElevenLabs Credit Check ---")
    print(f"Used:      {used:,}")
    print(f"Total:     {total:,}")
    print(f"Remaining: {remaining:,}")
    print(f"------------------------------------")
    
    if remaining < 1000:
        print("--- Warning: You are running low on credits! ---")
    else:
        print("--- You have plenty of credits for testing. ---")

except Exception as e:
    print(f"Failed to check credits: {e}")