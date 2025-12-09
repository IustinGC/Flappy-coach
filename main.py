from flap import FlappyGame


def main():
    # 1. Initialize the Game
    game = FlappyGame()

    print("Game Session Started.")
    print("Controls: Space to Jump, 'R' to Restart.")

    running = True
    while running:

        # 2. Get the current Game State
        # You can use these variables for your Support Agent later.
        state = game.get_state()

        # Example: Print only when dead to avoid spamming console
        if not state['is_alive'] and state['game_active']:
            # This is where your agent might decide to speak
            pass

        # 3. Step the Game
        # passing nothing means "Read the Human Keyboard Input"
        running = game.frame_step()


if __name__ == "__main__":
    main()