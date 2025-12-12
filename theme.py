"""
Модуль для настройки темы интерфейса.

Обеспечивает темную тему для tkinter и matplotlib.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

try:
    import ttkthemes

    HAS_TTKTHEMES = True
except ImportError:
    HAS_TTKTHEMES = False


class ThemeManager:
    """Класс для управления темой интерфейса."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Инициализирует менеджер темы.

        Параметры:
            root (tk.Tk): Корневое окно tkinter.
        """
        self.root = root

    def setup_dark_theme(self) -> None:
        """
        Настраивает темную тему для интерфейса и графиков.
        """
        # Темная тема для tkinter
        self.root.configure(bg="#2b2b2b")

        style = ttk.Style()

        # Попытка использовать ttkthemes, если доступен
        if HAS_TTKTHEMES:
            try:
                style.theme_use("equilux")
            except Exception:
                style.theme_use("clam")
        else:
            style.theme_use("clam")

        # Базовые цвета темной темы
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        entry_bg = "#404040"
        button_bg = "#404040"
        button_active = "#505050"
        border_color = "#555555"

        # Настройка цветов для темной темы
        style.configure("TFrame", background=bg_color)
        style.configure(
            "TLabelFrame",
            background=bg_color,
            foreground=fg_color,
            bordercolor=border_color,
            relief="solid",
            borderwidth=1,
        )
        style.configure("TLabelFrame.Label", background=bg_color, foreground=fg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure(
            "TButton", background=button_bg, foreground=fg_color, bordercolor=border_color
        )
        style.map(
            "TButton",
            background=[("active", button_active), ("pressed", "#606060")],
            bordercolor=[("active", "#666666")],
        )
        style.configure(
            "TEntry",
            fieldbackground=entry_bg,
            foreground=fg_color,
            bordercolor=border_color,
            insertcolor=fg_color,
            selectbackground="#606060",
            selectforeground=fg_color,
        )
        style.map("TEntry", fieldbackground=[("focus", entry_bg)], bordercolor=[("focus", "#777777")])
        style.configure(
            "TCombobox",
            fieldbackground=entry_bg,
            foreground=fg_color,
            bordercolor=border_color,
            arrowcolor=fg_color,
            selectbackground="#606060",
            selectforeground=fg_color,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", entry_bg)],
            selectbackground=[("readonly", "#606060")],
            bordercolor=[("focus", "#777777")],
        )
        style.configure(
            "TCheckbutton",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=bg_color,
            indicatorbackground=bg_color,
            bordercolor=border_color,
            focuscolor="",
        )
        style.map(
            "TCheckbutton",
            background=[("active", bg_color), ("selected", bg_color)],
            indicatorbackground=[("selected", "#606060"), ("!selected", bg_color)],
            bordercolor=[("focus", "#777777")],
        )

        # Темная тема для matplotlib
        plt.style.use("dark_background")

