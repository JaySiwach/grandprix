"""Python Grand Prix - entry point.  Run:  python main.py"""
import os
import sys

# make the project importable no matter where it is launched from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        import tkinter as tk
    except ImportError:
        sys.exit("Tkinter is not installed. On Debian/Ubuntu run: sudo apt install python3-tk")

    from game.game import Game

    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
