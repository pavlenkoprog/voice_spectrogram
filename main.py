"""
Точка входа в приложение.

Запускает главное окно приложения для анализа голосовых файлов.
"""

import tkinter as tk
from voice_analyzer import VoiceAnalyzer


def main() -> None:
    """
    Запускает приложение.
    """
    root = tk.Tk()
    app = VoiceAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

