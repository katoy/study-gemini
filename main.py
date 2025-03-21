# --- main.py ---
import tkinter as tk
from tkinter import messagebox
from game_logic import TicTacToe
from gui import TicTacToeGUI

def main():
    root = tk.Tk()
    gui = TicTacToeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
