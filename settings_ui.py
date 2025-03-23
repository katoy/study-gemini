import tkinter as tk


class SettingsUI:
    """
    UI class for the game settings.
    """

    def __init__(self, gui, master):
        self.gui = gui
        self.master = master
        self.settings_frame = None  # 初期化をNoneに変更
        self.player_var = tk.BooleanVar(value=True)
        self.agent_var = tk.StringVar(value="ランダム")

    def build_settings_ui(self):
        """Builds the settings UI (first/second, agent selection)."""
        # settings_frame が存在する場合は、子ウィジェットをすべて削除
        if self.settings_frame:
            for widget in self.settings_frame.winfo_children():
                widget.destroy()
        else:
            self.settings_frame = tk.Frame(self.master, bg="#333333")
            self.settings_frame.pack()

        self.player_label = tk.Label(
            self.settings_frame,
            text="先手:",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 14, "bold"),
        )
        self.player_label.pack(pady=5)

        self.player_first_radio = tk.Radiobutton(
            self.settings_frame,
            text="あなた",
            variable=self.player_var,
            value=True,
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.player_first_radio.pack(pady=5)
        self.player_second_radio = tk.Radiobutton(
            self.settings_frame,
            text="マシン",
            variable=self.player_var,
            value=False,
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.player_second_radio.pack(pady=5)

        self.agent_label = tk.Label(
            self.settings_frame,
            text="エージェント:",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 14, "bold"),
        )
        self.agent_label.pack(pady=5)

        self.random_agent_radio = tk.Radiobutton(
            self.settings_frame,
            text="ランダム",
            variable=self.agent_var,
            value="ランダム",
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.random_agent_radio.pack(pady=5)
        self.minimax_agent_radio = tk.Radiobutton(
            self.settings_frame,
            text="Minimax",
            variable=self.agent_var,
            value="Minimax",
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.minimax_agent_radio.pack(pady=5)
        self.database_agent_radio = tk.Radiobutton(  # 追加
            self.settings_frame,  # 追加
            text="Database",  # 追加
            variable=self.agent_var,  # 追加
            value="Database",  # 追加
            bg="#333333",  # 追加
            fg="#EEEEEE",  # 追加
            selectcolor="#555555",  # 追加
            font=("Arial", 12, "bold"),  # 追加
        )  # 追加
        self.database_agent_radio.pack(pady=5)  # 追加

        self.buttons_frame = tk.Frame(self.settings_frame, bg="#333333")
        self.buttons_frame.pack(pady=10)

        self.start_button = tk.Button(
            self.buttons_frame,
            text="ゲーム開始",
            command=self.start_game,
            bg="#444444",
            fg="black",
            font=("Arial", 14, "bold"),
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            self.buttons_frame,
            text="ゲーム中断",
            command=self.gui.stop_game,
            bg="#444444",
            fg="black",
            font=("Arial", 14, "bold"),
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def start_game(self):
        self.gui.start_game()

    def save_settings(self):
        """Saves the current settings."""
        return self.player_var.get(), self.agent_var.get()

    def load_settings(self, settings):
        """Loads the settings."""
        player_setting, agent_setting = settings
        self.player_var.set(player_setting)
        self.agent_var.set(agent_setting)
