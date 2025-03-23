
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
        self.selected_player = None  # True: Human first, False: Human second
        self.selected_agent = None  # "ランダム" or "Minimax"

        self.settings_ui = SettingsUI(self, master)
        self.board_drawer = BoardDrawer(self, self.canvas)
        self.game_info_ui = GameInfoUI(self, master)
        self.restart_button = None
        self.control_buttons_frame = None
        self.stop_button = None
        self.saved_settings = None

        self.settings_ui.build_settings_ui()

    def start_game(self):
        """Starts the game."""
        if self.restart_button:
            self.restart_button.destroy()
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
        self.control_buttons_frame = tk.Frame(self.master, bg="#333333")
        self.restart_button = tk.Button(
            self.control_buttons_frame,
            text="リスタート",
            command=self.restart_game,
            bg="#444444",
            fg="black",
            font=("Arial", 14, "bold"),
        )
        self.restart_button.pack(side=tk.LEFT, padx=5)
        self.control_buttons_frame.pack(pady=10)
        self.master.update_idletasks()
        self.master.update()

    def restart_game(self):
        """Restarts the game with the same settings."""
        self.start_game()

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
