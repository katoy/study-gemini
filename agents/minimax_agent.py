# --- agents/minimax_agent.py ---
from .base_agent import BaseAgent
import random

class MinimaxAgent(BaseAgent):
    def get_move(self, board):
        """
        Minimax アルゴリズムを使用して、最適な手を決定します。
        """
        print("--- get_move ---")
        print("Current Board:")
        for row in board:
            print(row)

        best_score = -float('inf')
        best_move = None
        best_moves = []

        # すべての空いているマスを試す
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    board[row][col] = self.player  # 自分の手を仮に置く
                    score = self.minimax(board, 0, False)  # 相手のターンで評価
                    board[row][col] = " "  # 盤面を元に戻す
                    print(f"  Move: ({row}, {col}), Score: {score}")

                    # より良い手が見つかった場合、更新
                    if score > best_score:
                        best_moves = [(row, col)]
                        best_score = score
                    elif score == best_score:
                        best_moves.append((row, col))

        if best_moves:
            best_move = random.choice(best_moves)
        else:
            best_move = None

        print(f"best_moves: {best_moves}")
        print(f"Best Move: {best_move}")
        return best_move

    def minimax(self, board, depth, is_maximizing):
        """
        Minimax アルゴリズムの再帰関数。

        Args:
            board: 現在の盤面。
            depth: 現在の探索の深さ。
            is_maximizing: 最大化プレイヤー（自分）のターンかどうか。

        Returns:
            盤面の評価値。
        """
        print(f"  minimax(depth={depth}, is_maximizing={is_maximizing})")
        print("    Current Board:")
        for row in board:
            print("   ", row)

        # 勝敗判定
        result = self.check_winner(board)
        if result == self.player:
            print(f"    Result: {result} (Win), Score: {100 - depth}")
            return 100 - depth  # 自分の勝ち：早く勝つほど高評価
        elif result != " " and result != None and result != "draw":
            print(f"    Result: {result} (Lose), Score: {-100 + depth}")
            return -100 + depth  # 相手の勝ち：遅く負けるほど高評価
        elif result == "draw":
            print(f"    Result: Draw, Score: 0")
            return 0  # 引き分け

        # 最大化プレイヤーのターン
        if is_maximizing:
            best_score = -float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.player
                        score = self.minimax(board, depth + 1, False)  # 次は相手のターン
                        board[row][col] = " "
                        print(f"    Max: Move: ({row}, {col}), Score: {score}")
                        best_score = max(best_score, score)
            print(f"    Max: Best Score: {best_score}")
            return best_score

        # 最小化プレイヤーのターン
        else:
            best_score = float('inf')
            opponent = "O" if self.player == "X" else "X"
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = opponent
                        score = self.minimax(board, depth + 1, False)  # 次は相手のターン
                        board[row][col] = " "
                        print(f"    Min: Move: ({row}, {col}), Score: {score}")
                        best_score = min(best_score, score)
            print(f"    Min: Best Score: {best_score}")
            return best_score
