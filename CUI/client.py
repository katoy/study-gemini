import sys
import os

# Add the parent directory to the Python path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from CUI.cui_display import display_board  # noqa: F401
from CUI.tic_tac_toe_client import TicTacToeClient

SERVER_URL = "http://127.0.0.1:8000"


def main():
    client = TicTacToeClient(SERVER_URL)
    while True:  # ループでゲームを再開
        client.play_single_game()

        play_again = input("Game over. Play again? (y/n): ").strip().lower()
        if play_again != 'y':
            break


if __name__ == "__main__":
    main()
