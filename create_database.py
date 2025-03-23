import json
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)

def check_winner(board: list) -> str | None:
    """
    勝者をチェックする
    """
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
    """
    盤面が埋まっているかチェックする
    """
    return all(cell != " " for row in board for cell in row)

def board_to_string(board: list) -> str:
    """
    盤面を文字列に変換する
    """
    return "".join(cell if cell != " " else " " for row in board for cell in row) # 修正

def string_to_board(board_str: str) -> list:
    """
    文字列を盤面に変換する
    """
    board = []
    for i in range(0, 9, 3):
        board.append(list(board_str[i:i+3]))
    return board

def get_opponent(player: str) -> str:
    """
    対戦相手を取得する
    """
    return "O" if player == "X" else "X"

def minimax(board: list, depth: int, is_maximizing: bool, player: str, database: dict) -> int:
    """
    Minimax アルゴリズム
    """
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
                score = minimax(board, depth + 1, False, player, database)
                board[row][col] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for i in range(9):
            row, col = i // 3, i % 3
            if board[row][col] == " ":
                board[row][col] = get_opponent(player)
                score = minimax(board, depth + 1, True, player, database)
                board[row][col] = " "
                best_score = min(score, best_score)
        return best_score

def create_database(board: list, player: str, database: dict):
    """
    データベースを作成する
    """
    board_str = board_to_string(board) # 修正
    if board_str in database: # 修正
        return

    winner = check_winner(board)
    if winner:
        database[board_str] = {"best_move": -1, "result": winner} # 修正
        logging.info(f"create_database: board_str: {board_str}, result: {winner}") # 修正
        return
    if is_board_full(board):
        database[board_str] = {"best_move": -1, "result": "draw"} # 修正
        logging.info(f"create_database: board_str: {board_str}, result: draw") # 修正
        return

    best_score = float("-inf")
    best_move = -1
    for i in range(9):
        row, col = i // 3, i % 3
        if board[row][col] == " ":
            board[row][col] = player
            score = minimax(board, 0, False, player, database)
            board[row][col] = " "
            if score > best_score:
                best_score = score
                best_move = i

    database[board_str] = {"best_move": best_move, "result": "continue"} # 修正
    logging.info(f"create_database: board_str: {board_str}, best_move: {best_move}") # 修正

    for i in range(9):
        row, col = i // 3, i % 3
        if board[row][col] == " ":
            board[row][col] = player
            create_database(board, get_opponent(player), database)
            board[row][col] = " "

def main():
    """
    メイン関数
    """
    database = {}
    empty_board = [[" " for _ in range(3)] for _ in range(3)]
    create_database(empty_board, "X", database)

    with open("tictactoe_database.json", "w") as f:
        json.dump(database, f, indent=4)

if __name__ == "__main__":
    main()
