# --- gui.py ---
import tkinter as tk
from tkinter import messagebox
from game_logic import TicTacToe

class TicTacToeGUI:
    def __init__(self, master):
        self.master = master
        master.title("三目並べ")
        master.configure(bg="#333333")  # Dark background

        self.game = None
        self.buttons = []
        self.canvas = tk.Canvas(master, width=300, height=300, bg="#333333", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.create_board_lines()

        # 勝敗結果を表示するためのラベルを作成
        self.result_label = tk.Label(master, text="", bg="#333333", fg="yellow", font=("Arial", 20, "bold"))
        self.result_label.pack(pady=10)
        self.result_label.pack_forget()  # 初期状態では非表示

        # 設定を保持するためのインスタンス変数を追加
        self.selected_player = True  # デフォルトは先手
        self.selected_agent = "ランダム"  # デフォルトはランダム

        self.start_game_frame = tk.Frame(master, bg="#333333")
        self.start_game_frame.pack()

        self.player_label = tk.Label(self.start_game_frame, text="先手/後手:", bg="#333333", fg="#EEEEEE", font=("Arial", 14, "bold"))
        self.player_label.grid(row=0, column=0, padx=5, pady=5)

        self.player_var = tk.BooleanVar(value=True)
        self.player_first_radio = tk.Radiobutton(self.start_game_frame, text="先手", variable=self.player_var, value=True, bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.player_first_radio.grid(row=0, column=1, padx=5, pady=5)
        self.player_second_radio = tk.Radiobutton(self.start_game_frame, text="後手", variable=self.player_var, value=False, bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.player_second_radio.grid(row=0, column=2, padx=5, pady=5)

        self.agent_label = tk.Label(self.start_game_frame, text="エージェント:", bg="#333333", fg="#EEEEEE", font=("Arial", 14, "bold"))
        self.agent_label.grid(row=1, column=0, padx=5, pady=5)

        self.agent_var = tk.StringVar(value="ランダム")
        self.random_agent_radio = tk.Radiobutton(self.start_game_frame, text="ランダム", variable=self.agent_var, value="ランダム", bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.random_agent_radio.grid(row=1, column=1, padx=5, pady=5)
        self.minimax_agent_radio = tk.Radiobutton(self.start_game_frame, text="Minimax", variable=self.agent_var, value="Minimax", bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.minimax_agent_radio.grid(row=1, column=2, padx=5, pady=5)

        # ゲーム開始ボタンの文字色を黒に変更
        self.start_button = tk.Button(self.start_game_frame, text="ゲーム開始", command=self.start_game, bg="#444444", fg="black", font=("Arial", 14, "bold"))
        self.start_button.grid(row=2, column=0, columnspan=3, pady=10)

        # リスタートボタンを初期化時に作成し、非表示にする
        self.restart_button = tk.Button(self.master, text="リスタート", command=self.restart_game, bg="#444444", fg="black", font=("Arial", 14, "bold"))
        self.restart_button.pack(pady=10)
        self.restart_button.pack_forget()  # 初期状態では非表示

        # ゲーム情報を表示するフレームを作成
        self.game_info_frame = tk.Frame(master, bg="#333333")

        # 先手/後手とエージェントを表示するラベルを作成
        self.player_info_label = tk.Label(self.game_info_frame, text="", bg="#333333", fg="#EEEEEE", font=("Arial", 12, "bold"))
        self.player_info_label.pack(side="left", padx=10)
        self.agent_info_label = tk.Label(self.game_info_frame, text="", bg="#333333", fg="#EEEEEE", font=("Arial", 12, "bold"))
        self.agent_info_label.pack(side="left", padx=10)

    def create_board_lines(self):
        for i in range(1, 3):
            self.canvas.create_line(i * 100, 0, i * 100, 300, fill="white", width=3)
            self.canvas.create_line(0, i * 100, 300, i * 100, fill="white", width=3)

    def start_game(self):
        # 設定を保持
        self.selected_player = self.player_var.get()
        self.selected_agent = self.agent_var.get()

        player_first = self.player_var.get()
        agent_type = self.agent_var.get()
        self.game = TicTacToe(player_first, agent_type)

        # ラジオボタンを無効化
        self.player_first_radio.config(state="disabled")
        self.player_second_radio.config(state="disabled")
        self.random_agent_radio.config(state="disabled")
        self.minimax_agent_radio.config(state="disabled")

        self.start_game_frame.destroy()

        self.draw_board()
        if not player_first:
            self.agent_turn()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        # ゲーム開始時にリスタートボタンを表示
        self.restart_button.pack()
        self.start_button.destroy()
        # ゲーム情報を表示
        self.game_info_frame.pack(pady=10)
        self.update_game_info()

    def update_game_info(self):
        player_text = "先手" if self.player_var.get() else "後手"
        agent_text = self.agent_var.get()
        self.player_info_label.config(text=f"プレイヤー: {player_text}")
        self.agent_info_label.config(text=f"エージェント: {agent_text}")

    def on_canvas_click(self, event):
        if self.game.current_player == self.game.human_player:
            col = event.x // 100
            row = event.y // 100
            self.cell_clicked(row, col)

    def draw_board(self):
        self.canvas.delete("all")
        self.create_board_lines()
        for i in range(3):
            for j in range(3):
                x1, y1 = j * 100 + 10, i * 100 + 10
                x2, y2 = (j + 1) * 100 - 10, (i + 1) * 100 - 10
                if self.game.board[i][j] == "X":
                    self.draw_x(x1, y1, x2, y2)
                elif self.game.board[i][j] == "O":
                    self.draw_o(x1, y1, x2, y2)

    def draw_x(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, fill="red", width=5)
        self.canvas.create_line(x1, y2, x2, y1, fill="red", width=5)

    def draw_o(self, x1, y1, x2, y2):
        self.canvas.create_oval(x1, y1, x2, y2, outline="blue", width=5)

    def cell_clicked(self, row, col):
        if self.game.current_player == self.game.human_player:
            if self.game.make_move(row, col):
                self.draw_board()
                winner = self.game.check_winner()
                if winner:
                    self.game_over(winner)
                    return
                self.game.switch_player()
                self.agent_turn()

    def agent_turn(self):
        if self.game.current_player == self.game.agent_player:
            if self.game.agent_move():
                self.draw_board()
                winner = self.game.check_winner()
                if winner:
                    self.game_over(winner)
                    return
                self.game.switch_player()

    def game_over(self, winner):
        # 3目を示す直線を描画
        if self.game.winner_line:
            (row1, col1), (row2, col2) = self.game.winner_line
            x1, y1 = col1 * 100 + 50, row1 * 100 + 50
            x2, y2 = col2 * 100 + 50, row2 * 100 + 50
            self.canvas.create_line(x1, y1, x2, y2, fill="yellow", width=5)

        # 勝敗判定結果をラベルに表示
        if winner == "draw":
            self.result_label.config(text="引き分けです！")
        else:
            self.result_label.config(text=f"{winner}の勝ちです！")
        self.result_label.pack()

    def restart_game(self):
        self.restart_button.pack_forget()
        self.game_info_frame.pack_forget()
        self.result_label.pack_forget()  # 結果ラベルを非表示にする
        self.start_game_frame = tk.Frame(self.master, bg="#333333")
        self.start_game_frame.pack()

        self.player_label = tk.Label(self.start_game_frame, text="先手/後手:", bg="#333333", fg="#EEEEEE", font=("Arial", 14, "bold"))
        self.player_label.grid(row=0, column=0, padx=5, pady=5)

        # 保存された設定を反映
        self.player_var = tk.BooleanVar(value=self.selected_player)
        self.player_first_radio = tk.Radiobutton(self.start_game_frame, text="先手", variable=self.player_var, value=True, bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.player_first_radio.grid(row=0, column=1, padx=5, pady=5)
        self.player_second_radio = tk.Radiobutton(self.start_game_frame, text="後手", variable=self.player_var, value=False, bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.player_second_radio.grid(row=0, column=2, padx=5, pady=5)

        self.agent_label = tk.Label(self.start_game_frame, text="エージェント:", bg="#333333", fg="#EEEEEE", font=("Arial", 14, "bold"))
        self.agent_label.grid(row=1, column=0, padx=5, pady=5)

        # 保存された設定を反映
        self.agent_var = tk.StringVar(value=self.selected_agent)
        self.random_agent_radio = tk.Radiobutton(self.start_game_frame, text="ランダム", variable=self.agent_var, value="ランダム", bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.random_agent_radio.grid(row=1, column=1, padx=5, pady=5)
        self.minimax_agent_radio = tk.Radiobutton(self.start_game_frame, text="Minimax", variable=self.agent_var, value="Minimax", bg="#333333", fg="#EEEEEE", selectcolor="#555555", font=("Arial", 12, "bold"))
        self.minimax_agent_radio.grid(row=1, column=2, padx=5, pady=5)

        self.start_button = tk.Button(self.start_game_frame, text="ゲーム開始", command=self.start_game, bg="#444444", fg="black", font=("Arial", 14, "bold"))
        self.start_button.grid(row=2, column=0, columnspan=3, pady=10)
