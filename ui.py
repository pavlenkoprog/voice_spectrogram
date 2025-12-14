"""
Модуль для создания пользовательского интерфейса.

Обеспечивает создание всех виджетов интерфейса приложения.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional
import webbrowser


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
        self.get_audio_duration: Optional[Callable[[], float]] = None

    def create_ui(
        self,
        load_file_callback: Callable,
        update_plots_callback: Callable,
        reset_settings_callback: Callable,
        get_audio_duration: Optional[Callable[[], float]] = None,
        save_spectrum_callback: Optional[Callable] = None,
        apply_csv_overlay_callback: Optional[Callable] = None,
        toggle_csv_overlay_callback: Optional[Callable] = None,
    ) -> Dict[str, tk.StringVar]:
        """
        Создает весь пользовательский интерфейс.

        Параметры:
            load_file_callback (Callable): Функция для загрузки файла.
            update_plots_callback (Callable): Функция для обновления графиков.
            reset_settings_callback (Callable): Функция для сброса настроек.
            get_audio_duration (Optional[Callable[[], float]]): Функция для получения длительности аудио.
            save_spectrum_callback (Optional[Callable]): Функция для сохранения спектрограммы.
            apply_csv_overlay_callback (Optional[Callable]): Функция для наложения CSV данных.
            toggle_csv_overlay_callback (Optional[Callable]): Функция для переключения отображения CSV данных.

        Возвращает:
            Dict[str, tk.StringVar]: Словарь с переменными интерфейса.
        """
        self.get_audio_duration = get_audio_duration

        # Настройка grid для всего окна
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Верхняя панель с кнопкой загрузки
        self._create_top_panel(
            load_file_callback,
            save_spectrum_callback,
            apply_csv_overlay_callback,
            toggle_csv_overlay_callback,
        )

        # Контейнер для графиков
        graphs_container = ttk.Frame(self.root)
        graphs_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)

        # Панель настроек
        self._create_settings_panel(update_plots_callback, reset_settings_callback)

        return self.vars

    def _create_top_panel(
        self,
        load_file_callback: Callable,
        save_spectrum_callback: Optional[Callable] = None,
        apply_csv_overlay_callback: Optional[Callable] = None,
        toggle_csv_overlay_callback: Optional[Callable] = None,
    ) -> None:
        """
        Создает верхнюю панель с кнопками загрузки и сохранения.

        Параметры:
            load_file_callback (Callable): Функция для загрузки WAV файла.
            save_spectrum_callback (Optional[Callable]): Функция для сохранения спектрограммы.
            apply_csv_overlay_callback (Optional[Callable]): Функция для наложения CSV данных.
            toggle_csv_overlay_callback (Optional[Callable]): Функция для переключения отображения CSV данных.
        """
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(
            top_frame, text="Загрузить WAV файл", command=load_file_callback
        ).pack(side=tk.LEFT, padx=5)

        if apply_csv_overlay_callback:
            ttk.Button(
                top_frame, text="Наложить CSV поверх", command=apply_csv_overlay_callback
            ).pack(side=tk.LEFT, padx=5)

        if toggle_csv_overlay_callback:
            # Чекбокс для включения/выключения отображения CSV данных
            self.csv_overlay_var = tk.BooleanVar(value=False)
            self.csv_overlay_checkbox = ttk.Checkbutton(
                top_frame,
                text="Показать CSV",
                variable=self.csv_overlay_var,
                command=toggle_csv_overlay_callback,
                state="disabled",  # По умолчанию отключен, пока не загружены CSV данные
            )
            self.csv_overlay_checkbox.pack(side=tk.LEFT, padx=5)

        if save_spectrum_callback:
            ttk.Button(
                top_frame, text="Сохранить спектр", command=save_spectrum_callback
            ).pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(top_frame, text="Файл не загружен")
        self.file_label.pack(side=tk.LEFT, padx=10)

        help_button = ttk.Button(
            top_frame,
            text="?",
            command=lambda: webbrowser.open("https://github.com/pavlenkoprog/voice_spectrogram"),
            width=3,
        )
        help_button.pack(side=tk.RIGHT, padx=5)

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
        self._create_setting_row(
            col1, "Начало времени (с):", "t_start", "0", width=16, validation_type="time_start"
        )
        self._create_setting_row(
            col1, "Конец времени (с):", "t_end", "1.0", width=16, validation_type="time_end"
        )

        # Колонка 2: Окно
        col2 = tk.Frame(parent, bg="#2b2b2b")
        col2.pack(side=tk.LEFT, padx=10)
        self._create_setting_row(
            col2, "Размер окна:", "nperseg", "1024", width=12, validation_type="positive_int"
        )
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
        self._create_setting_row(
            col3, "Макс. частота (Гц):", "freq_limit", "20000", width=15, validation_type="positive_float"
        )
        self._create_setting_row(
            col3, "Перекрытие (%):", "noverlap_percent", "90", width=15, validation_type="percent"
        )

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
        self._create_setting_row(
            col5, "Мин. дБ:", "db_min", "-50", width=8, validation_type="db_min"
        )
        self._create_setting_row(
            col5, "Макс. дБ:", "db_max", "0", width=8, validation_type="db_max"
        )

        # Скрытые переменные
        self.vars["shading"] = tk.StringVar(value="gouraud")
        self.vars["cmap"] = tk.StringVar(value="inferno")
        self.vars["smooth_window"] = tk.StringVar(value="5")

    def _create_setting_row(
        self,
        parent: tk.Frame,
        label_text: str,
        var_name: str,
        default_value: str,
        width: int = 12,
        validation_type: Optional[str] = None,
    ) -> None:
        """
        Создает строку с настройкой (Entry).

        Параметры:
            parent (tk.Frame): Родительский фрейм.
            label_text (str): Текст метки.
            var_name (str): Имя переменной.
            default_value (str): Значение по умолчанию.
            width (int): Ширина метки.
            validation_type (Optional[str]): Тип валидации.
        """
        row = tk.Frame(parent, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label_text, bg="#2b2b2b", fg="#ffffff", width=width, anchor="w").pack(
            side=tk.LEFT
        )
        self.vars[var_name] = tk.StringVar(value=default_value)
        entry = ttk.Entry(row, textvariable=self.vars[var_name], width=12)

        entry.pack(side=tk.LEFT, padx=5)

    def _validate_input(self, value: str, validation_type: str, var_name: str) -> bool:
        """
        Валидирует ввод в поле.

        Параметры:
            value (str): Вводимое значение.
            validation_type (str): Тип валидации.
            var_name (str): Имя переменной.

        Возвращает:
            bool: True если значение валидно, False иначе.
        """
        # Пустое значение разрешено (для редактирования)
        if value == "":
            return True

        # Валидация для времени начала
        if validation_type == "time_start":
            try:
                val = float(value)
                if val < 0:
                    return False
                # Проверка что начало < конца
                if "t_end" in self.vars:
                    try:
                        t_end = float(self.vars["t_end"].get())
                        if val >= t_end:
                            return False
                    except ValueError:
                        pass
                return True
            except ValueError:
                return False

        # Валидация для времени конца
        if validation_type == "time_end":
            try:
                val = float(value)
                # Проверка что конец > начала
                if "t_start" in self.vars:
                    try:
                        t_start = float(self.vars["t_start"].get())
                        if val <= t_start:
                            return False
                    except ValueError:
                        pass
                # Проверка что конец <= длительности аудио
                if self.get_audio_duration:
                    try:
                        max_duration = self.get_audio_duration()
                        if val > max_duration:
                            return False
                    except Exception:
                        pass
                return True
            except ValueError:
                return False

        # Валидация для положительных целых чисел
        if validation_type == "positive_int":
            try:
                val = int(value)
                return val > 0
            except ValueError:
                return False

        # Валидация для положительных чисел с плавающей точкой
        if validation_type == "positive_float":
            try:
                val = float(value)
                return val > 0
            except ValueError:
                return False

        # Валидация для процентов (0-99)
        if validation_type == "percent":
            try:
                val = float(value)
                return 0 <= val <= 99
            except ValueError:
                return False

        # Валидация для минимального дБ
        if validation_type == "db_min":
            try:
                val = float(value)
                # Проверка что мин < макс
                if "db_max" in self.vars:
                    try:
                        db_max = float(self.vars["db_max"].get())
                        if val >= db_max:
                            return False
                    except ValueError:
                        pass
                return True
            except ValueError:
                return False

        # Валидация для максимального дБ
        if validation_type == "db_max":
            try:
                val = float(value)
                # Проверка что макс > мин
                if "db_min" in self.vars:
                    try:
                        db_min = float(self.vars["db_min"].get())
                        if val <= db_min:
                            return False
                    except ValueError:
                        pass
                return True
            except ValueError:
                return False

        # По умолчанию разрешаем только числа
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _validate_on_focus_out(self, validation_type: str, var_name: str) -> None:
        """
        Валидирует и корректирует значение при потере фокуса.

        Параметры:
            validation_type (str): Тип валидации.
            var_name (str): Имя переменной.
        """
        if var_name not in self.vars:
            return

        value = self.vars[var_name].get()
        if value == "":
            return

        try:
            val = float(value)

            # Коррекция для времени начала
            if validation_type == "time_start":
                if val < 0:
                    self.vars[var_name].set("0")
                    return
                if "t_end" in self.vars:
                    try:
                        t_end = float(self.vars["t_end"].get())
                        if val >= t_end:
                            self.vars[var_name].set(str(max(0, t_end - 0.1)))
                    except ValueError:
                        pass

            # Коррекция для времени конца
            elif validation_type == "time_end":
                if "t_start" in self.vars:
                    try:
                        t_start = float(self.vars["t_start"].get())
                        if val <= t_start:
                            self.vars[var_name].set(str(t_start + 0.1))
                    except ValueError:
                        pass
                if self.get_audio_duration:
                    try:
                        max_duration = self.get_audio_duration()
                        if val > max_duration:
                            self.vars[var_name].set(str(max_duration))
                    except Exception:
                        pass

            # Коррекция для процентов
            elif validation_type == "percent":
                if val < 0:
                    self.vars[var_name].set("0")
                elif val > 99:
                    self.vars[var_name].set("99")

            # Коррекция для минимального дБ
            elif validation_type == "db_min":
                if "db_max" in self.vars:
                    try:
                        db_max = float(self.vars["db_max"].get())
                        if val >= db_max:
                            self.vars[var_name].set(str(db_max - 1))
                    except ValueError:
                        pass

            # Коррекция для максимального дБ
            elif validation_type == "db_max":
                if "db_min" in self.vars:
                    try:
                        db_min = float(self.vars["db_min"].get())
                        if val <= db_min:
                            self.vars[var_name].set(str(db_min + 1))
                    except ValueError:
                        pass

        except ValueError:
            # Если значение не число, устанавливаем значение по умолчанию
            default_values = {
                "t_start": "0",
                "t_end": "1.0",
                "nperseg": "1024",
                "freq_limit": "20000",
                "noverlap_percent": "90",
                "db_min": "-50",
                "db_max": "0",
            }
            if var_name in default_values:
                self.vars[var_name].set(default_values[var_name])

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

