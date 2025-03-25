import random
import numpy as np
import json  # 追加
import os  # 追加
from agents.base_agent import BaseAgent

class QLearningAgent(BaseAgent):
    def __init__(self, player: str, learning_rate=0.8, discount_factor=0.9, exploration_rate=0.2, q_table_file="q_table.json"): # q_table_fileを追加
        super().__init__(player)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table_file = q_table_file # 追加
        self.q_table = {}  # Qテーブル
        self.load_q_table() # 追加

    def get_move(self, board: list) -> tuple[int, int] | None:
        state = self.board_to_string(board)
        if state not in self.q_table:
            self.q_table[state] = [0] * 9  # 初期化

        if random.uniform(0, 1) < self.exploration_rate:
            # 探索
            return self.get_random_move(board)
        else:
            # 利用
            available_moves = self.get_available_moves(board)
            if not available_moves:
                return None
            q_values = [self.q_table[state][i] if (i // 3, i % 3) in available_moves else float('-inf') for i in range(9)]
            best_move_index = np.argmax(q_values)
            return self.index_to_move(best_move_index)

    def update_q_table(self, state, action, reward, next_state):
        if next_state not in self.q_table:
            self.q_table[next_state] = [0] * 9

        current_q = self.q_table[state][action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (reward + self.discount_factor * max_next_q)
        self.q_table[state][action] = new_q

    def get_available_moves(self, board):
        available_moves = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    available_moves.append((row, col))
        return available_moves

    def board_to_string(self, board: list) -> str:
        return "".join(cell if cell != " " else " " for row in board for cell in row)

    def index_to_move(self, index: int) -> tuple[int, int]:
        return index // 3, index % 3

    def get_random_move(self, board: list) -> tuple[int, int] | None:
        available_moves = [
            (row, col)
            for row in range(3)
            for col in range(3)
            if board[row][col] == " "
        ]
        return random.choice(available_moves) if available_moves else None

    def save_q_table(self): # 追加
        """Qテーブルをファイルに保存する"""
        with open(self.q_table_file, "w") as f:
            json.dump(self.q_table, f)

    def load_q_table(self): # 追加
        """Qテーブルをファイルから読み込む"""
        if os.path.exists(self.q_table_file):
            with open(self.q_table_file, "r") as f:
                self.q_table = json.load(f)
