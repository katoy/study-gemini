"""
minimax_agent.py: Minimax エージェントを実装します。
"""

from agents.base_agent import BaseAgent


class MinimaxAgent(BaseAgent):
    """
    Minimax アルゴリズムを使用して手を決定するエージェントです。
    """

    def __init__(self, player: str):
        """
        MinimaxAgent を初期化します。

        Args:
            player (str): このエージェントが表すプレイヤー ("X" または "O")。
        """
        super().__init__(player)

    def get_move(self, board: list) -> tuple[int, int] | None:
        """
        Minimax アルゴリズムを使用して、エージェントの手を取得します。

        Args:
            board (list): 現在のゲーム盤。

        Returns:
            tuple[int, int] | None: 手の (行, 列)。
        """
        best_score = float("-inf")  # 最良のスコアを負の無限大で初期化
        best_move = None  # 最良の手を None で初期化

        # すべての空いているセルを反復処理
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    # 手を試す
                    board[row][col] = self.player
                    # この手のスコアを取得
                    score = self.minimax(board, 0, False)
                    # 手を元に戻す
                    board[row][col] = " "

                    # 必要に応じて最良の手を更新
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

        return best_move

    def minimax(self, board: list, depth: int, is_maximizing: bool) -> int:
        """
        Minimax アルゴリズム。

        Args:
            board (list): 現在のゲーム盤。
            depth (int): 現在の探索の深さ。
            is_maximizing (bool): 最大化プレイヤーのターンなら True。

        Returns:
            int: 現在の盤面状態のスコア。
        """
        # 終端状態（勝ち、負け、引き分け）を確認
        winner = self.check_winner(board)
        if winner == self.player:
            return 100 - depth  # より早く勝つことを優先
        if winner == self.get_opponent(self.player):
            return -100 + depth  # より遅く負けることをペナルティ
        if self.is_board_full(board):
            return 0  # 引き分け

        # 最大化プレイヤーのターン（エージェント）
        if is_maximizing:
            best_score = float("-inf")
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.player
                        score = self.minimax(board, depth + 1, False)
                        board[row][col] = " "
                        best_score = max(score, best_score)
            return best_score

        # 最小化プレイヤーのターン（対戦相手）
        else:
            best_score = float("inf")
            for row in range(3):
                for col in range(3):
                    if board[row][col] == " ":
                        board[row][col] = self.get_opponent(self.player)
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = " "
                        best_score = min(score, best_score)
            return best_score

    def check_winner(self, board: list) -> str | None:
        """
        プレイヤーが勝ったかどうかを確認します。

        Args:
            board (list): 現在のゲーム盤。

        Returns:
            str | None: プレイヤーが勝った場合は "X" または "O"、それ以外の場合は None。
        """
        # 行を確認
        for row in board:
            if row[0] == row[1] == row[2] != " ":
                return row[0]

        # 列を確認
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != " ":
                return board[0][col]

        # 対角線を確認
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]

        return None

    def is_board_full(self, board: list) -> bool:
        """
        盤面が埋まっているかどうかを確認します。

        Args:
            board (list): 現在のゲーム盤。

        Returns:
            bool: 盤面が埋まっている場合は True、それ以外の場合は False。
        """
        return all(cell != " " for row in board for cell in row)

    def get_opponent(self, player: str) -> str:
        """
        指定されたプレイヤーの対戦相手を取得します。

        Args:
            player (str): プレイヤー ("X" または "O")。

        Returns:
            str: 対戦相手 ("X" または "O")。
        """
        return "O" if player == "X" else "X"
