from .base_agent import BaseAgent
import random
import logging

# ロガーの設定
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class MinimaxAgent(BaseAgent):
    def get_move(self, board):
        """
        Minimax アルゴリズムを使用して、最適な手を決定します。
        """
        logger.debug("--- get_move ---")
        logger.debug("Current Board:")
        for row in board:
            logger.debug(row)

        best_score = -float('inf')
        best_moves = []

        # すべての空いているマスを試す
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    board[row][col] = self.player  # 仮にエージェントの手を置く
                    # ここで次のターンは相手（最小化プレイヤー）のため False にする
                    score = self.minimax(board, 0, False)
                    board[row][col] = " "  # 元に戻す
                    logger.debug(f"  Move: ({row}, {col}), Score: {score}")

                    if score > best_score:
                        best_moves = [(row, col)]
                        best_score = score
                    elif score == best_score:
                        best_moves.append((row, col))

        best_move = random.choice(best_moves) if best_moves else None
        logger.debug(f"best_moves: {best_moves}")
        logger.debug(f"Best Move: {best_move}")
        return best_move

    def minimax(self, board, depth, is_maximizing):
        """
        Minimax アルゴリズムの再帰関数。

        Args:
            board: 現在の盤面。
            depth: 現在の探索の深さ。
            is_maximizing: 自分のターン（True）か相手のターン（False）か。

        Returns:
            盤面の評価値。
        """
        logger.debug(f"  minimax(depth={depth}, is_maximizing={is_maximizing})")
        logger.debug("    Current Board:")
        for row in board:
            logger.debug(f"   {row}")

        # 勝敗判定
        result = self.check_winner(board)
        if result == self.player:
            logger.debug(f"    Result: {result} (Win), Score: {100 - depth}")
            return 100 - depth  # 早く勝つほど高評価
        elif result is not None and result != " " and result != "draw":
            logger.debug(f"    Result: {result} (Lose), Score: {-100 + depth}")
            return -100 + depth  # 遅く負けるほど高評価
        elif result == "draw":
            logger.debug(f"    Result: Draw, Score: 0")
            return 0  # 引き分け

        # 最大化プレイヤーのターン（エージェントの手番）
        if is_maximizing:
            best_score = -float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.player
                        score = self.minimax(board, depth + 1, False)
                        board[row][col] = " "
                        logger.debug(f"    Max: Move: ({row}, {col}), Score: {score}")
                        best_score = max(best_score, score)
            logger.debug(f"    Max: Best Score: {best_score}")
            return best_score
        # 最小化プレイヤーのターン（相手の手番）
        else:
            best_score = float('inf')
            opponent = "O" if self.player == "X" else "X"
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = opponent
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = " "
                        logger.debug(f"    Min: Move: ({row}, {col}), Score: {score}")
                        best_score = min(best_score, score)
            logger.debug(f"    Min: Best Score: {best_score}")
            return best_score
