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