#!/usr/bin/env python3
"""
Main entry point for the Tic Tac Toe game.
This script initializes the GUI application.
"""

import tkinter as tk
import argparse

from gui import TicTacToeGUI


def main() -> None:
    """
    Creates the main window and starts the Tic Tac Toe game loop.

    Parses command line arguments to determine if the machine should play first.
    """
    parser = argparse.ArgumentParser(description="三目並べゲーム")
    parser.add_argument(
        "--machine-first",
        "-m",
        action="store_true",
        help="ゲーム開始時にマシンを先手にする",
    )
    args = parser.parse_args()

    root = tk.Tk()
    TicTacToeGUI(root, machine_first=args.machine_first)
    root.mainloop()


if __name__ == "__main__":
    main()
