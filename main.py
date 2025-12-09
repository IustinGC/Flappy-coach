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

        # Warning: this prints a lot of lines
        print(f"Current game state: {state}")

        # 3. Step the Game
        # passing nothing means "Read the Human Keyboard Input"
        running = game.frame_step()


if __name__ == "__main__":
    main()