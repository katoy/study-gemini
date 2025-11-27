import requests
import json

SERVER_URL = "http://127.0.0.1:8000"

def display_board(board_state):
    print("\n--- Tic Tac Toe Board ---")
    board = board_state["board"]
    display_cells = []
    for r_idx, row in enumerate(board):
        display_row = []
        for c_idx, cell in enumerate(row):
            if cell == " ":
                # Calculate the corresponding number for the empty cell (1-9)
                display_row.append(str(r_idx * 3 + c_idx + 1))
            else:
                display_row.append(cell)
        display_cells.append(display_row)

    for row in display_cells:
        print("| " + " | ".join(row) + " |")
    print("-------------------------\n")
    if board_state["winner"]:
        if board_state["winner"] == "draw":
            print("Game Over: It's a draw!")
        else:
            print(f"Game Over: Player {board_state['winner']} wins!")
    elif board_state["game_over"]:
        print("Game Over.") # Should not happen if winner is None and game_over is True without draw
    else:
        print(f"Current Player: {board_state['current_player']}")

def get_user_move():
    while True:
        try:
            move_num = int(input("Enter your move (1-9): "))
            if 1 <= move_num <= 9:
                row = (move_num - 1) // 3
                col = (move_num - 1) % 3
                return row, col
            else:
                print("Invalid input. Please enter a number between 1 and 9.")
        except ValueError:
            print("Invalid input format. Please enter a single number.")

def main():
    print("Starting new Tic Tac Toe game...")
    try:
        response = requests.post(f"{SERVER_URL}/game/start")
        response.raise_for_status()
        game_state = response.json()
        display_board(game_state)
    except requests.exceptions.RequestException as e:
        print(f"Error starting game: {e}")
        return

    while not game_state["game_over"]:
        row, col = get_user_move()
        try:
            response = requests.post(f"{SERVER_URL}/game/move", json={"row": row, "col": col})
            response.raise_for_status()
            game_state = response.json()
            display_board(game_state)
        except requests.exceptions.RequestException as e:
            print(f"Error making move: {e}")
            if response.status_code == 400: # Invalid move
                print("This move is not valid. Please try again.")
            continue # Allow user to try again

if __name__ == "__main__":
    main()
