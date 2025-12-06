"""
Модуль для обработки аудио файлов.

Обеспечивает загрузку и обработку WAV файлов.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram
from typing import Optional, Tuple, Dict


class AudioProcessor:
    """Класс для обработки аудио файлов."""

    def __init__(self) -> None:
        """Инициализирует процессор аудио."""
        self.sample_rate: Optional[int] = None
        self.data: Optional[np.ndarray] = None
        self.file_path: Optional[str] = None

    def load_file(self, file_path: str) -> Tuple[int, np.ndarray]:
        """
        Загружает WAV файл.

        Параметры:
            file_path (str): Путь к WAV файлу.

        Возвращает:
            Tuple[int, np.ndarray]: Частота дискретизации и данные аудио.
        """
        self.sample_rate, self.data = wavfile.read(file_path)
        if len(self.data.shape) > 1:
            self.data = self.data[:, 0]

        self.file_path = file_path
        return self.sample_rate, self.data

    def get_segment(
        self, t_start: float, t_end: float
    ) -> Tuple[np.ndarray, int, int]:
        """
        Получает сегмент аудио данных по времени.

        Параметры:
            t_start (float): Начало сегмента в секундах.
            t_end (float): Конец сегмента в секундах.

        Возвращает:
            Tuple[np.ndarray, int, int]: Сегмент данных, начальный и конечный индексы.
        """
        if self.data is None or self.sample_rate is None:
            raise ValueError("Аудио файл не загружен")

        start_idx = int(t_start * self.sample_rate)
        end_idx = int(t_end * self.sample_rate)

        if start_idx < 0:
            start_idx = 0
        if end_idx > len(self.data):
            end_idx = len(self.data)
        if start_idx >= end_idx:
            raise ValueError("t_start должен быть меньше t_end")

        data_segment = self.data[start_idx:end_idx]
        return data_segment, start_idx, end_idx

    def compute_spectrogram(
        self, data_segment: np.ndarray, params: Dict
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Вычисляет спектрограмму для сегмента данных.

        Параметры:
            data_segment (np.ndarray): Сегмент аудио данных.
            params (Dict): Параметры для вычисления спектрограммы.

        Возвращает:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: Частоты, времена и спектрограмму.
        """
        if self.sample_rate is None:
            raise ValueError("Частота дискретизации не установлена")

        nperseg = params["nperseg"]
        noverlap = int(nperseg * params["noverlap_percent"] / 100)
        freq_limit = params["freq_limit"]

        # Вычисление спектрограммы
        f, t, Sxx = spectrogram(
            data_segment,
            fs=self.sample_rate,
            window=params["window"],
            nperseg=nperseg,
            noverlap=noverlap,
            scaling=params["scaling"],
            mode=params["mode"],
        )

        # Ограничение частоты
        mask = f <= freq_limit
        f = f[mask]
        Sxx = Sxx[mask, :]

        # Перевод в dB
        if params["mode"] != "phase" and params["mode"] != "angle":
            Sxx_dB = 20 * np.log10(Sxx + 1e-10)
            Sxx_dB = np.clip(Sxx_dB, params["db_min"], params["db_max"])
        else:
            Sxx_dB = Sxx

        return f, t, Sxx_dB

    def compute_volume_envelope(
        self, data_segment: np.ndarray, smooth_window_ms: float
    ) -> np.ndarray:
        """
        Вычисляет огибающую громкости для сегмента данных.

        Параметры:
            data_segment (np.ndarray): Сегмент аудио данных.
            smooth_window_ms (float): Размер окна сглаживания в миллисекундах.

        Возвращает:
            np.ndarray: Огибающая громкости.
        """
        if self.sample_rate is None:
            raise ValueError("Частота дискретизации не установлена")

        # Нормализация данных
        segment_normalized = (
            data_segment / np.max(np.abs(data_segment))
            if np.max(np.abs(data_segment)) > 0
            else data_segment
        )

        # Мгновенная амплитуда
        abs_signal = np.abs(segment_normalized)

        # Сглаживание
        window_size = int(smooth_window_ms * self.sample_rate / 1000)
        if window_size > 0:
            window = np.ones(window_size) / window_size
            envelope = np.convolve(abs_signal, window, mode="same")
        else:
            envelope = abs_signal

        return envelope

