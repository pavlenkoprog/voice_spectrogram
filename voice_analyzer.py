"""
Основной модуль приложения для анализа голосовых файлов.

Объединяет все компоненты приложения: интерфейс, обработку аудио, графики и настройки.
"""

import os
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
            self._load_csv,
            self._apply_csv_overlay,
            self._remove_csv_overlay,
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

            # Обновление графика спектрограммы (с учетом наложенных данных)
            overlay_data = self.csv_overlay_data if self.csv_overlay_data else None
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

            messagebox.showinfo("Успех", f"Спектрограмма сохранена в файл:\n{file_path}")
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

    def _load_csv(self) -> None:
        """
        Загружает данные спектрограммы из CSV файла в переменную для наложения.
        """
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл со спектрограммой",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            import csv

            frequencies = []
            times = []
            spectrogram_data = []

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

                # Читаем данные
                for row in reader:
                    if len(row) < 2:
                        continue

                    try:
                        # Первая колонка - время
                        time_val = float(row[0])
                        times.append(time_val)

                        # Остальные колонки - значения амплитуды
                        if len(row) - 1 != len(frequencies):
                            raise ValueError(
                                f"Несоответствие количества частот ({len(frequencies)}) "
                                f"и значений в строке ({len(row) - 1})"
                            )

                        amplitudes = [float(val) for val in row[1:]]
                        spectrogram_data.append(amplitudes)

                    except ValueError as e:
                        raise ValueError(f"Ошибка при чтении данных в строке {len(times) + 1}: {str(e)}")

            if len(times) == 0:
                raise ValueError("Файл не содержит данных")

            # Преобразуем в numpy массивы
            f = np.array(frequencies)
            t = np.array(times)
            Sxx_dB = np.array(spectrogram_data).T  # Транспонируем: строки = частоты, столбцы = время

            # Определяем временной диапазон
            t_start = float(t[0])
            t_end = float(t[-1])

            # Сохраняем данные для наложения
            self.csv_overlay_data = {
                "frequencies": f,
                "times": t,
                "spectrogram": Sxx_dB,
                "t_start": t_start,
                "t_end": t_end,
                "filename": os.path.basename(file_path),
            }

            messagebox.showinfo(
                "Успех",
                f"CSV файл загружен:\n{os.path.basename(file_path)}\n\n"
                f"Используйте кнопку 'Наложить CSV поверх' для отображения.",
            )

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

    def _apply_csv_overlay(self) -> None:
        """
        Накладывает загруженные CSV данные поверх текущей спектрограммы.
        """
        if self.csv_overlay_data is None:
            messagebox.showwarning(
                "Предупреждение", "Нет загруженных CSV данных. Сначала загрузите CSV файл."
            )
            return

        if self.last_spectrogram_data is None:
            messagebox.showwarning(
                "Предупреждение",
                "Нет данных спектрограммы для наложения. Сначала загрузите WAV файл и обновите графики.",
            )
            return

        # Обновляем графики с наложением
        if self.audio_processor.data is not None and self.audio_processor.sample_rate is not None:
            # Если есть загруженный аудио, обновляем графики
            self._update_plots()
        else:
            # Если нет аудио, но есть данные спектрограммы, обновляем только график
            params = self._get_parameters()
            if params is None:
                return

            f = self.last_spectrogram_data["frequencies"]
            t = self.last_spectrogram_data["times"]
            Sxx_dB = self.last_spectrogram_data["spectrogram"]
            t_start = self.last_spectrogram_data["t_start"]
            t_relative = t - t_start

            self.plotter.update_spectrogram(f, t_relative, Sxx_dB, t_start, params, self.csv_overlay_data)
            self.plotter.align_plots()

        messagebox.showinfo(
            "Успех",
            f"CSV данные наложены поверх спектрограммы:\n{self.csv_overlay_data['filename']}",
        )

    def _remove_csv_overlay(self) -> None:
        """
        Удаляет наложенные CSV данные.
        """
        if self.csv_overlay_data is None:
            messagebox.showinfo("Информация", "Нет наложенных CSV данных для удаления.")
            return

        self.csv_overlay_data = None

        # Обновляем графики без наложения
        if self.audio_processor.data is not None and self.audio_processor.sample_rate is not None:
            self._update_plots()
        elif self.last_spectrogram_data is not None:
            params = self._get_parameters()
            if params is None:
                return

            f = self.last_spectrogram_data["frequencies"]
            t = self.last_spectrogram_data["times"]
            Sxx_dB = self.last_spectrogram_data["spectrogram"]
            t_start = self.last_spectrogram_data["t_start"]
            t_relative = t - t_start

            self.plotter.update_spectrogram(f, t_relative, Sxx_dB, t_start, params, None)
            self.plotter.align_plots()

        messagebox.showinfo("Успех", "Наложение CSV данных удалено.")


def main() -> None:
    """
    Запускает приложение.
    """
    root = tk.Tk()
    app = VoiceAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
