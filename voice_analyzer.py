"""
Основной модуль приложения для анализа голосовых файлов.

Объединяет все компоненты приложения: интерфейс, обработку аудио, графики и настройки.
"""

import os
import datetime
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
            self._load_file,
            self._update_plots,
            self._reset_settings,
            self._get_audio_duration,
            self._save_spectrum,
            self._apply_csv_overlay,
            self._toggle_csv_overlay,
        )

        # Создание построителя графиков
        graphs_frame = tk.Frame(self.root)
        graphs_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        self.plotter = Plotter(graphs_frame)

        # Хранение последних данных спектрограммы для сохранения
        self.last_spectrogram_data: Optional[Dict] = None

        # Хранение наложенных данных из CSV
        self.csv_overlay_data: Optional[Dict] = None

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

    def _get_audio_duration(self) -> float:
        """
        Возвращает длительность загруженного аудио файла в секундах.

        Возвращает:
            float: Длительность в секундах или 0 если файл не загружен.
        """
        if (
            self.audio_processor.data is None
            or self.audio_processor.sample_rate is None
        ):
            return 0.0
        return len(self.audio_processor.data) / self.audio_processor.sample_rate

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
            # Используем os.path для корректной работы на всех ОС
            filename = os.path.basename(file_path)
            self.ui_builder.update_file_label(f"Файл: {filename}")
            
            # Устанавливаем по умолчанию первую секунду
            self.vars["t_start"].set("0")
            self.vars["t_end"].set("1.0")

            self._update_plots()
        except PermissionError:
            messagebox.showerror(
                "Ошибка доступа",
                f"Антивирус или система безопасности блокирует доступ к файлу.\n\n"
                f"Путь: {file_path}\n\n"
                f"Решение:\n"
                f"1. Добавьте приложение в исключения антивируса\n"
                f"2. Проверьте права доступа к файлу\n"
                f"3. Убедитесь, что файл не используется другим приложением"
            )
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить файл: {str(e)}\n\n"
                f"Убедитесь, что:\n"
                f"- Файл является корректным WAV файлом\n"
                f"- Файл не поврежден\n"
                f"- У вас есть права на чтение файла"
            )

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

            # Сохранение данных для возможности экспорта
            self.last_spectrogram_data = {
                "frequencies": f,
                "times": t + t_start,  # Времена с учетом смещения
                "spectrogram": Sxx_dB,
                "t_start": t_start,
                "t_end": t_end,
            }

            # Очищаем кэш наложения при изменении параметров
            self.plotter.overlay_cache = None

            # Обновление графика спектрограммы (с учетом наложенных данных и состояния чекбокса)
            overlay_data = None
            if self.csv_overlay_data and hasattr(self.ui_builder, 'csv_overlay_var') and self.ui_builder.csv_overlay_var.get():
                overlay_data = self.csv_overlay_data
            self.plotter.update_spectrogram(f, t, Sxx_dB, t_start, params, overlay_data)

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

    def _save_spectrum(self) -> None:
        """
        Сохраняет данные спектрограммы в файл CSV.
        """
        if self.last_spectrogram_data is None:
            messagebox.showwarning(
                "Предупреждение",
                "Нет данных для сохранения. Сначала загрузите файл и обновите графики."
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить спектрограмму",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            import csv

            f = self.last_spectrogram_data["frequencies"]
            t = self.last_spectrogram_data["times"]
            Sxx_dB = self.last_spectrogram_data["spectrogram"]

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Заголовок: первая строка с частотами
                header = ["Время/Частота"] + [f"{freq:.2f}" for freq in f]
                writer.writerow(header)

                # Данные: каждая строка - время, затем значения амплитуды для каждой частоты
                for i, time_val in enumerate(t):
                    row = [f"{time_val:.6f}"] + [f"{Sxx_dB[j, i]:.6f}" for j in range(len(f))]
                    writer.writerow(row)
        except PermissionError:
            messagebox.showerror(
                "Ошибка доступа",
                f"Антивирус или система безопасности блокирует сохранение файла.\n\n"
                f"Путь: {file_path}\n\n"
                f"Решение:\n"
                f"1. Добавьте приложение в исключения антивируса\n"
                f"2. Проверьте права доступа к папке\n"
                f"3. Выберите другую папку для сохранения"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def _apply_csv_overlay(self) -> None:
        """
        Загружает и накладывает CSV данные поверх текущей спектрограммы.
        Наложение начинается с начала обработанного аудио, временные метки CSV игнорируются.
        """
        if self.last_spectrogram_data is None:
            messagebox.showwarning(
                "Предупреждение",
                "Нет данных спектрограммы для наложения. Сначала загрузите WAV файл и обновите графики.",
            )
            return

        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл для наложения",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            import csv

            frequencies = []
            spectrogram_data = []
            csv_times = []  # Временные метки из CSV для расчета длительности

            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)

                # Читаем заголовок с частотами
                header = next(reader)
                if len(header) < 2 or header[0] != "Время/Частота":
                    raise ValueError(
                        "Неверный формат файла. Ожидается заголовок 'Время/Частота' в первой колонке."
                    )

                # Извлекаем частоты из заголовка (начиная со второй колонки)
                try:
                    frequencies = [float(freq) for freq in header[1:]]
                except ValueError as e:
                    raise ValueError(f"Ошибка при чтении частот из заголовка: {str(e)}")

                if len(frequencies) == 0:
                    raise ValueError("Не найдены частоты в заголовке файла")

                # Читаем данные (временные метки сохраняем для расчета длительности)
                for row in reader:
                    if len(row) < 2:
                        continue

                    try:
                        # Первая колонка - время (сохраняем для расчета длительности)
                        time_val = float(row[0])
                        csv_times.append(time_val)

                        # Остальные колонки - значения амплитуды
                        if len(row) - 1 != len(frequencies):
                            raise ValueError(
                                f"Несоответствие количества частот ({len(frequencies)}) "
                                f"и значений в строке ({len(row) - 1})"
                            )

                        amplitudes = [float(val) for val in row[1:]]
                        spectrogram_data.append(amplitudes)

                    except ValueError as e:
                        raise ValueError(f"Ошибка при чтении данных в строке {len(spectrogram_data) + 1}: {str(e)}")

            if len(spectrogram_data) == 0:
                raise ValueError("Файл не содержит данных")

            # Преобразуем в numpy массивы
            f = np.array(frequencies)
            Sxx_dB = np.array(spectrogram_data).T  # Транспонируем: строки = частоты, столбцы = время

            # Создаем временную сетку на основе основной спектрограммы
            # Временные метки CSV игнорируются, наложение начинается с начала основной спектрограммы
            t_main = self.last_spectrogram_data["times"]
            num_time_points_csv = Sxx_dB.shape[1]
            num_time_points_main = len(t_main)

            # Проверяем, помещаются ли данные CSV в временную область основной спектрограммы
            if num_time_points_csv > num_time_points_main:
                # Вычисляем длительность временной области основной спектрограммы
                t_main_duration = t_main[-1] - t_main[0]
                # Вычисляем длительность CSV данных по временным меткам из файла
                if len(csv_times) > 1:
                    csv_duration = csv_times[-1] - csv_times[0]
                else:
                    # Если только одна точка, используем средний шаг основной спектрограммы
                    if len(t_main) > 1:
                        avg_time_step = t_main_duration / (num_time_points_main - 1)
                        csv_duration = num_time_points_csv * avg_time_step
                    else:
                        csv_duration = t_main_duration

                messagebox.showwarning(
                    "Предупреждение",
                    f"Временная область на графике слишком короткая для полного отображения CSV данных.\n\n"
                    f"Длительность области графика: {t_main_duration:.3f} с\n"
                    f"Длительность CSV данных: {csv_duration:.3f} с\n\n"
                    f"Данные будут обрезаны и отображены только частично.\n"
                    f"Увеличьте временной диапазон (t_end - t_start) для полного отображения.",
                )

            # Обрезаем данные CSV, если они не помещаются
            if num_time_points_csv > num_time_points_main:
                Sxx_dB = Sxx_dB[:, :num_time_points_main]
                num_time_points_csv = num_time_points_main

            # Создаем временную сетку для наложения (начинается с начала основной спектрограммы)
            t_overlay = t_main[:num_time_points_csv]

            # Сохраняем данные для наложения
            self.csv_overlay_data = {
                "frequencies": f,
                "times": t_overlay,
                "spectrogram": Sxx_dB,
                "filename": os.path.basename(file_path),
            }

            # Включаем чекбокс после загрузки CSV
            if hasattr(self.ui_builder, 'csv_overlay_var'):
                self.ui_builder.csv_overlay_var.set(True)
                self.ui_builder.csv_overlay_checkbox.config(state="normal")

            # Обновляем графики с наложением
            if self.audio_processor.data is not None and self.audio_processor.sample_rate is not None:
                # Если есть загруженный аудио, обновляем графики
                self._update_plots()
            else:
                # Если нет аудио, но есть данные спектрограммы, обновляем только график
                params = self._get_parameters()
                if params is None:
                    return

                f_main = self.last_spectrogram_data["frequencies"]
                t_main_rel = self.last_spectrogram_data["times"] - self.last_spectrogram_data["t_start"]
                Sxx_dB_main = self.last_spectrogram_data["spectrogram"]
                t_start = self.last_spectrogram_data["t_start"]

                # Передаем данные только если чекбокс включен
                overlay_data = None
                if self.csv_overlay_data and hasattr(self.ui_builder, 'csv_overlay_var') and self.ui_builder.csv_overlay_var.get():
                    overlay_data = self.csv_overlay_data
                self.plotter.update_spectrogram(
                    f_main, t_main_rel, Sxx_dB_main, t_start, params, overlay_data
                )
                self.plotter.align_plots()

        except PermissionError:
            messagebox.showerror(
                "Ошибка доступа",
                f"Антивирус или система безопасности блокирует доступ к файлу.\n\n"
                f"Путь: {file_path}\n\n"
                f"Решение:\n"
                f"1. Добавьте приложение в исключения антивируса\n"
                f"2. Проверьте права доступа к файлу\n"
                f"3. Убедитесь, что файл не используется другим приложением"
            )
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении CSV файла: {str(e)}")
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить файл: {str(e)}\n\n"
                f"Убедитесь, что:\n"
                f"- Файл является корректным CSV файлом\n"
                f"- Файл был сохранен этой программой\n"
                f"- Файл не поврежден"
            )

    def _toggle_csv_overlay(self) -> None:
        """
        Переключает отображение наложенных CSV данных.
        Просто перерисовывает график без пересчета спектрограммы.
        """
        print("toggle_csv_overlay", datetime.datetime.now())

        if self.last_spectrogram_data is None:
            return

        print("get_parameters", datetime.datetime.now())
        # Получаем параметры для отображения
        params = self._get_parameters()
        if params is None:
            return
        print("params", datetime.datetime.now())

        # Используем уже вычисленные данные, не пересчитываем спектрограмму
        f = self.last_spectrogram_data["frequencies"]
        t = self.last_spectrogram_data["times"]
        Sxx_dB = self.last_spectrogram_data["spectrogram"]
        t_start = self.last_spectrogram_data["t_start"]
        t_relative = t - t_start
        print("data", datetime.datetime.now())

        # Передаем данные только если чекбокс включен
        overlay_data = None
        if (
            self.csv_overlay_data
            and hasattr(self.ui_builder, "csv_overlay_var")
            and self.ui_builder.csv_overlay_var.get()
        ):
            overlay_data = self.csv_overlay_data
        print("get overlay_data", datetime.datetime.now())

        # Просто перерисовываем график с уже имеющимися данными
        self.plotter.update_spectrogram(f, t_relative, Sxx_dB, t_start, params, overlay_data)
        print("update_spectrogram", datetime.datetime.now())
        self.plotter.align_plots()
        print("align_plots", datetime.datetime.now())


def main() -> None:
    """
    Запускает приложение.
    """
    root = tk.Tk()
    app = VoiceAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
