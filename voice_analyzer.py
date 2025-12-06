"""
Основной модуль приложения для анализа голосовых файлов.

Объединяет все компоненты приложения: интерфейс, обработку аудио, графики и настройки.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from typing import Optional, Dict

from settings import SettingsManager
from theme import ThemeManager
from ui import UIBuilder
from plotter import Plotter
from audio_processor import AudioProcessor


class VoiceAnalyzer:
    """Класс для анализа голосовых файлов с графическим интерфейсом."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Инициализирует приложение.

        Параметры:
            root (tk.Tk): Корневое окно tkinter.
        """
        self.root = root
        self.root.title("Анализатор голосовых файлов")
        self.root.geometry("1400x900")

        # Инициализация компонентов
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager(root)
        self.audio_processor = AudioProcessor()
        self.ui_builder = UIBuilder(root)

        # Настройка темы
        self.theme_manager.setup_dark_theme()

        # Создание интерфейса
        self.vars = self.ui_builder.create_ui(
            self._load_file, self._update_plots, self._reset_settings
        )

        # Создание построителя графиков
        graphs_frame = tk.Frame(self.root)
        graphs_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        self.plotter = Plotter(graphs_frame)

        # Загрузка настроек
        self._load_settings()

    def _load_settings(self) -> None:
        """Загружает настройки из файла конфигурации."""
        settings = self.settings_manager.load_settings()

        # Применяем настройки к переменным интерфейса
        for key, value in settings.items():
            if key in self.vars:
                self.vars[key].set(value)

    def _save_settings(self) -> None:
        """Сохраняет текущие настройки в файл конфигурации."""
        settings = {}
        for key, var in self.vars.items():
            settings[key] = var.get()

        self.settings_manager.save_settings(settings)

    def _reset_settings(self) -> None:
        """Сбрасывает все настройки на значения по умолчанию."""
        default_settings = self.settings_manager.get_default_settings()

        for key, value in default_settings.items():
            if key in self.vars:
                self.vars[key].set(value)

        self._save_settings()

    def _load_file(self) -> None:
        """Загружает WAV файл для анализа."""
        file_path = filedialog.askopenfilename(
            title="Выберите WAV файл",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            self.audio_processor.load_file(file_path)
            self.ui_builder.update_file_label(f"Файл: {file_path.split('/')[-1]}")

            # Устанавливаем по умолчанию первую секунду
            self.vars["t_start"].set("0")
            self.vars["t_end"].set("1.0")

            self._update_plots()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _get_parameters(self) -> Optional[Dict]:
        """
        Получает параметры из интерфейса.

        Возвращает:
            Optional[Dict]: Словарь с параметрами анализа или None при ошибке.
        """
        try:
            return {
                "t_start": float(self.vars["t_start"].get()),
                "t_end": float(self.vars["t_end"].get()),
                "nperseg": int(self.vars["nperseg"].get()),
                "freq_limit": float(self.vars["freq_limit"].get()),
                "window": self.vars["window"].get(),
                "scaling": self.vars["scaling"].get(),
                "mode": self.vars["mode"].get(),
                "cmap": self.vars["cmap"].get(),
                "shading": self.vars["shading"].get(),
                "noverlap_percent": float(self.vars["noverlap_percent"].get()),
                "db_min": float(self.vars["db_min"].get()),
                "db_max": float(self.vars["db_max"].get()),
                "smooth_window_ms": float(self.vars["smooth_window"].get()),
            }
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверное значение параметра: {str(e)}")
            return None

    def _update_plots(self) -> None:
        """Обновляет графики спектрограммы и громкости."""
        if self.audio_processor.data is None or self.audio_processor.sample_rate is None:
            return

        params = self._get_parameters()
        if params is None:
            return

        try:
            # Получение сегмента данных
            t_start = params["t_start"]
            t_end = params["t_end"]

            data_segment, start_idx, end_idx = self.audio_processor.get_segment(
                t_start, t_end
            )

            # Вычисление спектрограммы
            f, t, Sxx_dB = self.audio_processor.compute_spectrogram(data_segment, params)

            # Обновление графика спектрограммы
            self.plotter.update_spectrogram(f, t, Sxx_dB, t_start, params)

            # Вычисление огибающей громкости
            envelope = self.audio_processor.compute_volume_envelope(
                data_segment, params["smooth_window_ms"]
            )

            # Шкала времени для графика громкости
            time = np.linspace(t_start, t_end, len(envelope))

            # Обновление графика громкости
            self.plotter.update_volume(time, envelope, t_start, t_end)

            # Выравнивание графиков
            self.plotter.align_plots()

            # Сохранение настроек
            self._save_settings()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графиков: {str(e)}")


def main() -> None:
    """
    Запускает приложение.
    """
    root = tk.Tk()
    app = VoiceAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
