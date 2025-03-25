# gui.py
import tkinter as tk

from game_logic import TicTacToe
from settings_ui import SettingsUI
from board_drawer import BoardDrawer
from game_info_ui import GameInfoUI


class TicTacToeGUI:
    """
    GUI class for the Tic Tac Toe game.
    """

    def __init__(self, master):
        """
        Initializes the TicTacToeGUI.

        Args:
            master (tk.Tk): The root window.
        """
        self.master = master
        master.title("三目並べ")
        master.configure(bg="#333333")

        self.canvas = tk.Canvas(
            master, width=300, height=300, bg="#333333", highlightthickness=0
        )
        self.canvas.pack(pady=20)

        self.result_label = tk.Label(
            master,
            text="",
            bg="#333333",
            fg="yellow",
            font=("Arial", 20, "bold"),
        )
        self.result_label.pack(pady=10)
        self.result_label.pack_forget()

        # Settings to be saved (used on restart)
        self.selected_player = None  # True: Human select, False: Machine select
        self.selected_agent = None  # "ランダム" or "Minimax" or "Database" or "QLearning"

        self.settings_ui = SettingsUI(self, master)
        self.board_drawer = BoardDrawer(self, self.canvas)
        self.game_info_ui = GameInfoUI(self, master)
        self.control_buttons_frame = None
        self.stop_button = None
        self.saved_settings = None

        self.settings_ui.build_settings_ui()

    def start_game(self):
        """Starts the game."""
        if self.control_buttons_frame:
            self.control_buttons_frame.destroy()
        self.selected_player = self.settings_ui.player_var.get()
        self.selected_agent = self.settings_ui.agent_var.get()
        self.game = TicTacToe(self.selected_player, self.selected_agent)
        self.board_drawer.draw_board()
        self.game_info_ui.show_game_info()
        self.board_drawer.remove_winner_highlight()
        self.canvas.delete("all")
        self.board_drawer.create_board_lines()
        self.result_label.pack_forget()

        # If the human is second, the agent goes first
        if not self.selected_player:
            self.agent_first_move()

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.control_buttons_frame = tk.Frame(self.master, bg="#333333")
        self.control_buttons_frame.pack(pady=10)

    def train_q_learning_agent(self):
        """強化学習エージェントを学習させる"""
        num_episodes = 10000  # 学習回数
        for episode in range(num_episodes):
            self.game = TicTacToe(False, "QLearning")  # 学習時はエージェント同士の対戦
            while not self.game.game_over:
                self.agent_turn_for_training()
            self.update_q_table_after_game()
            print(f"学習中: {episode+1}/{num_episodes}")
        # 学習完了後、人間の操作を受け付ける
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.control_buttons_frame = tk.Frame(self.master, bg="#333333")
        self.control_buttons_frame.pack(pady=10)

    def agent_turn_for_training(self):
        """学習用のエージェントのターン"""
        if self.game.current_player == self.game.agent_player:
            current_state = self.game.agent.board_to_string(self.game.board)
            move = self.game.agent.get_move(self.game.board)
            if move is not None:
                row, col = move
                action = row * 3 + col
                self.game.make_move(row, col)
                self.game.switch_player()
                next_state = self.game.agent.board_to_string(self.game.board)
                winner = self.game.check_winner()
                if winner == self.game.agent_player:
                    reward = 100
                elif winner == self.game.get_opponent(self.game.agent_player):
                    reward = -100
                elif winner == "draw":
                    reward = 0
                else:
                    reward = 0
                self.game.agent.update_q_table(current_state, action, reward, next_state)

    def update_q_table_after_game(self):
        """ゲーム終了後にQテーブルを更新する"""
        winner = self.game.check_winner()
        if winner == self.game.agent_player:
            reward = 100
        elif winner == self.game.get_opponent(self.game.agent_player):
            reward = -100
        elif winner == "draw":
            reward = 0
        else:
            reward = 0

        # 最後の状態と行動に対する報酬を更新
        current_state = self.game.agent.board_to_string(self.game.board)
        if self.game.agent.get_available_moves(self.game.board):
            move = self.game.agent.get_move(self.game.board)
            if move is not None:
                row, col = move
                action = row * 3 + col
                self.game.agent.update_q_table(current_state, action, reward, current_state)

    def agent_first_move(self):
        """Handles the agent's first move."""
        if self.game.current_player == self.game.agent_player:
            self.game.agent_move()
            self.board_drawer.draw_board()
            self.game.switch_player()

    def on_canvas_click(self, event):
        """Handles the canvas click event."""
        if self.game.current_player == self.game.human_player:
            col = event.x // 100
            row = event.y // 100
            self.cell_clicked(row, col)

    def cell_clicked(self, row, col):
        """Handles a cell click event."""
        # ゲームが終了している場合は処理をスキップ
        if self.game.game_over:
            return
        if self.game.current_player == self.game.human_player:
            if self.game.make_move(row, col):
                self.board_drawer.draw_board()
                winner = self.game.check_winner()
                if winner:
                    self.game_over(winner)
                    return
                self.game.switch_player()
                self.agent_turn()

    def agent_turn(self):
        """Handles the agent's turn."""
        if self.game.current_player == self.game.agent_player:
            if self.game.agent_move():
                self.board_drawer.draw_board()
                winner = self.game.check_winner()
                if winner:
                    self.game_over(winner)
                    return
                self.game.switch_player()

    def game_over(self, winner):
        """Handles the game over state."""
        self.canvas.unbind("<Button-1>")
        if self.game.winner_line:
            self.board_drawer.highlight_winner_cells(self.game.winner_line)
        if winner == "draw":
            self.result_label.config(text="引き分けです！")
        else:
            self.result_label.config(text=f"{winner}の勝ちです！")
        self.result_label.pack()
        if self.control_buttons_frame:
            self.control_buttons_frame.destroy()
        self.master.update_idletasks()
        self.master.update()

    def stop_game(self):
        """Stops the game and returns to the settings screen."""
        self.canvas.unbind("<Button-1>")
        self.board_drawer.remove_winner_highlight()
        self.result_label.pack_forget()
        if self.control_buttons_frame:
            self.control_buttons_frame.destroy()
        self.saved_settings = self.settings_ui.save_settings()
        if self.settings_ui.settings_frame:
            self.settings_ui.settings_frame.pack()
        self.settings_ui.build_settings_ui()
        self.settings_ui.load_settings(self.saved_settings)
