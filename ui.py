"""
Модуль для создания пользовательского интерфейса.

Обеспечивает создание всех виджетов интерфейса приложения.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable


class UIBuilder:
    """Класс для построения пользовательского интерфейса."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Инициализирует построитель интерфейса.

        Параметры:
            root (tk.Tk): Корневое окно tkinter.
        """
        self.root = root
        self.vars: Dict[str, tk.StringVar] = {}

    def create_ui(
        self,
        load_file_callback: Callable,
        update_plots_callback: Callable,
        reset_settings_callback: Callable,
    ) -> Dict[str, tk.StringVar]:
        """
        Создает весь пользовательский интерфейс.

        Параметры:
            load_file_callback (Callable): Функция для загрузки файла.
            update_plots_callback (Callable): Функция для обновления графиков.
            reset_settings_callback (Callable): Функция для сброса настроек.

        Возвращает:
            Dict[str, tk.StringVar]: Словарь с переменными интерфейса.
        """
        # Настройка grid для всего окна
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Верхняя панель с кнопкой загрузки
        self._create_top_panel(load_file_callback)

        # Контейнер для графиков
        graphs_container = ttk.Frame(self.root)
        graphs_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)

        # Панель настроек
        self._create_settings_panel(update_plots_callback, reset_settings_callback)

        return self.vars

    def _create_top_panel(self, load_file_callback: Callable) -> None:
        """
        Создает верхнюю панель с кнопкой загрузки.

        Параметры:
            load_file_callback (Callable): Функция для загрузки файла.
        """
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(
            top_frame, text="Загрузить WAV файл", command=load_file_callback
        ).pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(top_frame, text="Файл не загружен")
        self.file_label.pack(side=tk.LEFT, padx=10)

    def _create_settings_panel(
        self, update_plots_callback: Callable, reset_settings_callback: Callable
    ) -> None:
        """
        Создает панель настроек.

        Параметры:
            update_plots_callback (Callable): Функция для обновления графиков.
            reset_settings_callback (Callable): Функция для сброса настроек.
        """
        settings_container = tk.Frame(self.root, bg="#2b2b2b", relief="solid", bd=1)
        settings_container.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Заголовок панели
        settings_label = tk.Label(
            settings_container,
            text="Настройки",
            bg="#2b2b2b",
            fg="#ffffff",
            font=("TkDefaultFont", 9, "bold"),
        )
        settings_label.pack(anchor="w", padx=20, pady=(10, 5))

        # Фрейм для содержимого
        settings_frame = tk.Frame(settings_container, bg="#2b2b2b")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Контейнер для колонок
        columns_container = tk.Frame(settings_frame, bg="#2b2b2b")
        columns_container.pack(fill=tk.X, pady=5)

        # Создание колонок с настройками
        self._create_settings_columns(columns_container)

        # Кнопки
        buttons_frame = tk.Frame(columns_container, bg="#2b2b2b")
        buttons_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            buttons_frame, text="Обновить графики", command=update_plots_callback
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame, text="Сбросить настройки", command=reset_settings_callback
        ).pack(side=tk.LEFT, padx=5)

    def _create_settings_columns(self, parent: tk.Frame) -> None:
        """
        Создает колонки с настройками.

        Параметры:
            parent (tk.Frame): Родительский фрейм.
        """
        # Колонка 1: Время
        col1 = tk.Frame(parent, bg="#2b2b2b")
        col1.pack(side=tk.LEFT, padx=10)
        self._create_setting_row(col1, "Начало времени (с):", "t_start", "0", width=16)
        self._create_setting_row(col1, "Конец времени (с):", "t_end", "1.0", width=16)

        # Колонка 2: Окно
        col2 = tk.Frame(parent, bg="#2b2b2b")
        col2.pack(side=tk.LEFT, padx=10)
        self._create_setting_row(col2, "Размер окна:", "nperseg", "1024", width=12)
        self._create_setting_combo(
            col2,
            "Функция окна:",
            "window",
            "hann",
            ["hann", "hamming", "blackman", "bartlett", "boxcar"],
            width=12,
        )

        # Колонка 3: Частота и перекрытие
        col3 = tk.Frame(parent, bg="#2b2b2b")
        col3.pack(side=tk.LEFT, padx=10)
        self._create_setting_row(col3, "Макс. частота (Гц):", "freq_limit", "20000", width=15)
        self._create_setting_row(col3, "Перекрытие (%):", "noverlap_percent", "90", width=15)

        # Колонка 4: Режим и масштабирование
        col4 = tk.Frame(parent, bg="#2b2b2b")
        col4.pack(side=tk.LEFT, padx=10)
        self._create_setting_combo(
            col4,
            "Режим:",
            "mode",
            "magnitude",
            ["magnitude", "psd", "phase", "angle", "complex"],
            width=16,
        )
        self._create_setting_combo(
            col4, "Масштабирование:", "scaling", "density", ["density", "spectrum"], width=16
        )

        # Колонка 5: Диапазон дБ
        col5 = tk.Frame(parent, bg="#2b2b2b")
        col5.pack(side=tk.LEFT, padx=10)
        self._create_setting_row(col5, "Мин. дБ:", "db_min", "-50", width=8)
        self._create_setting_row(col5, "Макс. дБ:", "db_max", "0", width=8)

        # Скрытые переменные
        self.vars["shading"] = tk.StringVar(value="gouraud")
        self.vars["cmap"] = tk.StringVar(value="inferno")
        self.vars["smooth_window"] = tk.StringVar(value="5")

    def _create_setting_row(
        self, parent: tk.Frame, label_text: str, var_name: str, default_value: str, width: int = 12
    ) -> None:
        """
        Создает строку с настройкой (Entry).

        Параметры:
            parent (tk.Frame): Родительский фрейм.
            label_text (str): Текст метки.
            var_name (str): Имя переменной.
            default_value (str): Значение по умолчанию.
            width (int): Ширина метки.
        """
        row = tk.Frame(parent, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label_text, bg="#2b2b2b", fg="#ffffff", width=width, anchor="w").pack(
            side=tk.LEFT
        )
        self.vars[var_name] = tk.StringVar(value=default_value)
        ttk.Entry(row, textvariable=self.vars[var_name], width=12).pack(side=tk.LEFT, padx=5)

    def _create_setting_combo(
        self,
        parent: tk.Frame,
        label_text: str,
        var_name: str,
        default_value: str,
        values: list,
        width: int = 12,
    ) -> None:
        """
        Создает строку с настройкой (Combobox).

        Параметры:
            parent (tk.Frame): Родительский фрейм.
            label_text (str): Текст метки.
            var_name (str): Имя переменной.
            default_value (str): Значение по умолчанию.
            values (list): Список значений для выбора.
            width (int): Ширина метки.
        """
        row = tk.Frame(parent, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label_text, bg="#2b2b2b", fg="#ffffff", width=width, anchor="w").pack(
            side=tk.LEFT
        )
        self.vars[var_name] = tk.StringVar(value=default_value)
        combo = ttk.Combobox(row, textvariable=self.vars[var_name], values=values, width=10, state="readonly")
        combo.pack(side=tk.LEFT, padx=5)

    def update_file_label(self, text: str) -> None:
        """
        Обновляет метку с именем файла.

        Параметры:
            text (str): Текст для отображения.
        """
        self.file_label.config(text=text)

