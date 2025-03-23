import tkinter as tk


class SettingsUI:
    """
    UI class for the game settings.
    """

    def __init__(self, gui, master):
        self.gui = gui
        self.master = master

    def build_settings_ui(self):
        """Builds the settings UI (first/second, agent selection)."""
        self.start_game_frame = tk.Frame(self.master, bg="#333333")
        self.start_game_frame.pack()

        self.player_label = tk.Label(
            self.start_game_frame,
            text="先手/後手:",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 14, "bold"),
        )
        self.player_label.grid(row=0, column=0, padx=5, pady=5)

        self.player_var = tk.BooleanVar(value=True)
        self.player_first_radio = tk.Radiobutton(
            self.start_game_frame,
            text="先手",
            variable=self.player_var,
            value=True,
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.player_first_radio.grid(row=0, column=1, padx=5, pady=5)
        self.player_second_radio = tk.Radiobutton(
            self.start_game_frame,
            text="後手",
            variable=self.player_var,
            value=False,
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.player_second_radio.grid(row=0, column=2, padx=5, pady=5)

        self.agent_label = tk.Label(
            self.start_game_frame,
            text="エージェント:",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 14, "bold"),
        )
        self.agent_label.grid(row=1, column=0, padx=5, pady=5)

        self.agent_var = tk.StringVar(value="ランダム")
        self.random_agent_radio = tk.Radiobutton(
            self.start_game_frame,
            text="ランダム",
            variable=self.agent_var,
            value="ランダム",
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.random_agent_radio.grid(row=1, column=1, padx=5, pady=5)
        self.minimax_agent_radio = tk.Radiobutton(
            self.start_game_frame,
            text="Minimax",
            variable=self.agent_var,
            value="Minimax",
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.minimax_agent_radio.grid(row=1, column=2, padx=5, pady=5)

        self.start_button = tk.Button(
            self.start_game_frame,
            text="ゲーム開始",
            command=self.gui.start_game,
            bg="#444444",
            fg="black",
            font=("Arial", 14, "bold"),
        )
        self.start_button.grid(row=2, column=0, columnspan=3, pady=10)
