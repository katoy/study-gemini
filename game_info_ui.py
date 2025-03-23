import tkinter as tk


class GameInfoUI:
    """
    UI class for the game information.
    """

    def __init__(self, gui, master):
        self.gui = gui
        self.master = master
        self.game_info_frame = tk.Frame(master, bg="#333333")
        self.player_info_label = tk.Label(
            self.game_info_frame,
            text="",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 12, "bold"),
        )
        self.player_info_label.pack(side="left", padx=10)
        self.agent_info_label = tk.Label(
            self.game_info_frame,
            text="",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 12, "bold"),
        )
        self.agent_info_label.pack(side="left", padx=10)

    def show_game_info(self):
        self.game_info_frame.pack(pady=10)
        self.update_game_info()

    def update_game_info(self):
        """Updates the game information labels."""
        player_text = (
            "先手: あなた" if self.gui.selected_player else "後手: あなた"
        )
        agent_text = f"エージェント: {self.gui.selected_agent}"
        self.player_info_label.config(text=player_text)
        self.agent_info_label.config(text=agent_text)
