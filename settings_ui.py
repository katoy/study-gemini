import tkinter as tk
from tkinter import ttk


from agent_discovery import get_agent_details


class SettingsUI:
    def __init__(self, gui, master):
        self.gui = gui
        self.master = master
        self.settings_frame = None
        self.player_var = tk.BooleanVar(value=True)
        self.agent_var = tk.StringVar()

        # 共通モジュールからエージェント詳細を取得
        self.agent_options_for_display, self.AGENT_CLASSES = get_agent_details()

        if self.agent_options_for_display:
            self.agent_var.set(self.agent_options_for_display[0])
        else:
            self.agent_var.set("エージェントなし")

    def build_settings_ui(self):
        """Builds the settings UI (first/second, agent selection)."""
        if self.settings_frame:
            for widget in self.settings_frame.winfo_children():
                widget.destroy()
        else:
            self.settings_frame = tk.Frame(self.master, bg="#333333")
            self.settings_frame.pack()

        self.player_frame = tk.LabelFrame(
            self.settings_frame,
            text="プレイヤーの順番",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 14, "bold"),
            labelanchor="n",
        )
        self.player_frame.pack(pady=10)

        self.player_first_radio = tk.Radiobutton(
            self.player_frame,
            text="あなた（先手）",
            variable=self.player_var,
            value=True,
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.player_first_radio.pack(side="left", padx=10)
        self.player_second_radio = tk.Radiobutton(
            self.player_frame,
            text="マシン（先手）",
            variable=self.player_var,
            value=False,
            bg="#333333",
            fg="#EEEEEE",
            selectcolor="#555555",
            font=("Arial", 12, "bold"),
        )
        self.player_second_radio.pack(side="left", padx=10)

        self.agent_frame = tk.LabelFrame(
            self.settings_frame,
            text="対戦エージェント",
            bg="#333333",
            fg="#EEEEEE",
            font=("Arial", 14, "bold"),
            labelanchor="n",
        )
        self.agent_frame.pack(pady=10)
        self.agent_combo = ttk.Combobox(
            self.agent_frame,
            textvariable=self.agent_var,
            values=self.agent_options_for_display,
            state="readonly",
            font=("Arial", 12),
        )
        self.agent_combo.pack(pady=5)
        if self.agent_options_for_display:
            self.agent_combo.current(0)

        # ボタンフレーム
        self.buttons_frame = tk.Frame(self.settings_frame, bg="#333333")
        self.buttons_frame.pack(pady=20)

        # ゲーム開始ボタン
        self.start_button = tk.Button(
            self.buttons_frame,
            text="ゲーム開始",
            command=self.start_game,
            bg="#808080",  # グレーに変更
            fg="black",  # 黒に変更
            font=("Arial", 16, "bold"),
            width=15,
            height=2,
        )
        self.start_button.pack(side="left", padx=20)

        # ゲーム中断ボタン
        self.stop_button = tk.Button(
            self.buttons_frame,
            text="ゲーム中断",
            command=self.gui.stop_game,
            bg="#808080",  # グレーに変更
            fg="black",  # 黒に変更
            font=("Arial", 12),
            width=10,
            height=1,
        )
        self.stop_button.pack(side="left", padx=20)

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
