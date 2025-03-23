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
        self.selected_player = None  # True: Human first, False: Human second
        self.selected_agent = None  # "ランダム" or "Minimax"

        self.settings_ui = SettingsUI(self, master)
        self.board_drawer = BoardDrawer(self, self.canvas)
        self.game_info_ui = GameInfoUI(self, master)

        # Frame for control buttons (displayed always)
        self.control_buttons_frame = tk.Frame(master, bg="#333333")
        self.restart_same_button = tk.Button(
            self.control_buttons_frame,
            text="同じ設定で再開",
            command=self.restart_game_same_settings,
            bg="#444444",
            fg="black",
            font=("Arial", 14, "bold"),
        )
        self.restart_same_button.pack(side=tk.LEFT, padx=5)
        self.restart_reset_button = tk.Button(
            self.control_buttons_frame,
            text="条件再設定",
            command=self.restart_game_with_settings,
            bg="#444444",
            fg="black",
            font=("Arial", 14, "bold"),
        )
        self.restart_reset_button.pack(side=tk.LEFT, padx=5)
        self.control_buttons_frame.pack(pady=10)

        self.settings_ui.build_settings_ui() # 移動

    def start_game(self):
        """Starts the game."""
        self.selected_player = self.settings_ui.player_var.get()
        self.selected_agent = self.settings_ui.agent_var.get()
        self.game = TicTacToe(self.selected_player, self.selected_agent)
        # self.settings_ui.start_game_frame.destroy() # 削除
        self.board_drawer.draw_board()
        # If the human is second, the agent goes first
        if not self.selected_player:
            self.agent_turn()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.game_info_ui.show_game_info()

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
        self.master.update_idletasks()
        self.master.update()

    def restart_game_same_settings(self):
        """Restarts the game with the same settings."""
        self.result_label.pack_forget()
        self.board_drawer.remove_winner_highlight()
        self.game = TicTacToe(self.selected_player, self.selected_agent)
        self.board_drawer.draw_board()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.game_info_ui.update_game_info()
        if not self.selected_player:
            self.agent_turn()

    def restart_game_with_settings(self):
        """Restarts the game with new settings."""
        self.result_label.pack_forget()
        self.canvas.unbind("<Button-1>")
        self.canvas.delete("all")
        self.board_drawer.remove_winner_highlight()
        self.board_drawer.create_board_lines()
        self.settings_ui.build_settings_ui()
