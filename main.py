import tkinter as tk
from game_app import start_game


def start_menu():
    root = tk.Tk()
    root.title("Game Main Menu")
    start_button = tk.Button(root, text="Start Game", command=lambda: on_start_game(root))
    start_button.pack()
    root.mainloop()


def on_start_game(root):
    root.destroy()
    if start_game():
        start_menu()


if __name__ == "__main__":
    start_menu()
