#!/usr/bin/env python3
"""
Main entry point for the Tic Tac Toe game.
"""

import tkinter as tk

from gui import TicTacToeGUI


def main():
    """
    Creates the main window and starts the Tic Tac Toe game.
    """
    root = tk.Tk()
    TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
