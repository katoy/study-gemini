# --- agents/minimax_agent.py ---
from .base_agent import BaseAgent

class MinimaxAgent(BaseAgent):
    def get_move(self, board):
        best_score = -float('inf')
        best_move = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = self.player
                    score = self.minimax(board, 0, False)
                    board[i][j] = " "
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        return best_move

    def minimax(self, board, depth, is_maximizing):
        result = self.check_winner(board)
        if result == self.player:
            return 1 - depth  # O が勝った場合は深さを考慮
        elif result != " " and result != None:
            return -1 + depth  # X が勝った場合は深さを考慮
        elif self.is_board_full(board):
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = self.player
                        score = self.minimax(board, depth + 1, False)
                        board[i][j] = " "
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            opponent = "O" if self.player == "X" else "X"
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = opponent
                        score = self.minimax(board, depth + 1, True)
                        board[i][j] = " "
                        best_score = min(score, best_score)
            return best_score
