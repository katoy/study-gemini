import sqlite3
import logging
import json

# ロギング設定
logging.basicConfig(level=logging.INFO)

def check_winner(board: list) -> str | None:
    for row in board:
        if row[0] == row[1] == row[2] != " ":
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != " ":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None

def is_board_full(board: list) -> bool:
    return all(cell != " " for row in board for cell in row)

def board_to_string(board: list) -> str:
    return "".join(cell if cell != " " else " " for row in board for cell in row)

def get_opponent(player: str) -> str:
    return "O" if player == "X" else "X"

def minimax(board: list, depth: int, is_maximizing: bool, player: str) -> int:
    winner = check_winner(board)
    if winner == player:
        return 100 - depth
    if winner == get_opponent(player):
        return -100 + depth
    if is_board_full(board):
        return 0

    if is_maximizing:
        best_score = float("-inf")
        for i in range(9):
            row, col = i // 3, i % 3
            if board[row][col] == " ":
                board[row][col] = player
                score = minimax(board, depth + 1, False, player)
                board[row][col] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for i in range(9):
            row, col = i // 3, i % 3
            if board[row][col] == " ":
                board[row][col] = get_opponent(player)
                score = minimax(board, depth + 1, True, player)
                board[row][col] = " "
                best_score = min(score, best_score)
        return best_score

def insert_to_db(cursor, board_str, best_move, result):
    cursor.execute('''
        INSERT OR REPLACE INTO tictactoe (board, best_move, result)
        VALUES (?, ?, ?)
    ''', (board_str, best_move, result))

def create_database(board: list, player: str, cursor, seen: set, perfect_moves: dict):
    board_str = board_to_string(board)
    if board_str in seen:
        return
    seen.add(board_str)

    winner = check_winner(board)
    if winner:
        insert_to_db(cursor, board_str, -1, winner)
        logging.info(f"勝敗あり: {board_str} → {winner}")
        perfect_moves[board_str] = -1
        return
    if is_board_full(board):
        insert_to_db(cursor, board_str, -1, "draw")
        logging.info(f"引き分け: {board_str}")
        perfect_moves[board_str] = -1
        return

    best_score = float("-inf")
    best_move = -1
    for i in range(9):
        row, col = i // 3, i % 3
        if board[row][col] == " ":
            board[row][col] = player
            score = minimax(board, 0, False, player)
            board[row][col] = " "
            if score > best_score:
                best_score = score
                best_move = i

    insert_to_db(cursor, board_str, best_move, "continue")
    logging.info(f"登録: {board_str} → best_move: {best_move}")
    perfect_moves[board_str] = best_move

    for i in range(9):
        row, col = i // 3, i % 3
        if board[row][col] == " ":
            board[row][col] = player
            create_database(board, get_opponent(player), cursor, seen, perfect_moves)
            board[row][col] = " "

def main():
    conn = sqlite3.connect("tictactoe.db")
    cursor = conn.cursor()

    # テーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tictactoe (
            board TEXT PRIMARY KEY,
            best_move INTEGER,
            result TEXT
        )
    ''')

    empty_board = [[" " for _ in range(3)] for _ in range(3)]
    seen = set()
    perfect_moves = {}
    create_database(empty_board, "X", cursor, seen, perfect_moves)

    conn.commit()
    conn.close()
    print("✅ データベースファイル tictactoe.db を生成しました。")

    # perfect_moves を JSON ファイルに保存
    with open("perfect_moves.json", "w") as f:
        json.dump(perfect_moves, f)
    print("✅ perfect_moves.json を生成しました。")

if __name__ == "__main__":
    main()
