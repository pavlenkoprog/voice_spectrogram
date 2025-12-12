"""
Модуль для работы с графиками.

Обеспечивает создание и обновление графиков спектрограммы и громкости.
"""

import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Optional, Dict, Tuple


class Plotter:
    """Класс для работы с графиками."""

    def __init__(self, parent_frame: tk.Frame) -> None:
        """
        Инициализирует построитель графиков.

        Параметры:
            parent_frame (tk.Frame): Родительский фрейм для графиков.
        """
        self.parent_frame = parent_frame
        self.cbar_spectro: Optional[object] = None

        # Создание графиков
        self._create_plots()

    def _create_plots(self) -> None:
        """Создает графики спектрограммы и громкости."""
        # Контейнер для графиков
        graphs_container = tk.Frame(self.parent_frame, bg="#2b2b2b")
        graphs_container.pack(fill=tk.BOTH, expand=True)

        # Настройка grid для процентного распределения графиков
        graphs_container.columnconfigure(0, weight=1)
        graphs_container.rowconfigure(0, weight=60)  # Спектрограмма 60%
        graphs_container.rowconfigure(1, weight=20)  # Громкость 20%

        # Фрейм для спектрограммы
        spectro_frame = tk.Frame(graphs_container, bg="#2b2b2b")
        spectro_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # График спектрограммы
        self.fig_spectro = Figure(figsize=(12, 6), dpi=100, facecolor="#1e1e1e")
        self.ax_spectro = self.fig_spectro.add_subplot(111, facecolor="#1e1e1e")
        self._configure_axes_style(self.ax_spectro)

        self.canvas_spectro = FigureCanvasTkAgg(self.fig_spectro, spectro_frame)
        self.canvas_spectro.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Фрейм для графика громкости
        volume_frame = tk.Frame(graphs_container, bg="#2b2b2b")
        volume_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # График громкости
        self.fig_volume = Figure(figsize=(12, 2), dpi=100, facecolor="#1e1e1e")
        self.ax_volume = self.fig_volume.add_subplot(111, facecolor="#1e1e1e")
        self._configure_axes_style(self.ax_volume)

        self.canvas_volume = FigureCanvasTkAgg(self.fig_volume, volume_frame)
        self.canvas_volume.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _configure_axes_style(self, ax) -> None:
        """
        Настраивает стиль осей графика.

        Параметры:
            ax: Оси matplotlib для настройки.
        """
        ax.tick_params(colors="#ffffff")
        ax.xaxis.label.set_color("#ffffff")
        ax.yaxis.label.set_color("#ffffff")
        ax.title.set_color("#ffffff")
        ax.spines["bottom"].set_color("#ffffff")
        ax.spines["top"].set_color("#ffffff")
        ax.spines["right"].set_color("#ffffff")
        ax.spines["left"].set_color("#ffffff")

    def update_spectrogram(
        self,
        f: np.ndarray,
        t: np.ndarray,
        Sxx_dB: np.ndarray,
        t_start: float,
        params: Dict,
        overlay_data: Optional[Dict] = None,
    ) -> None:
        """
        Обновляет график спектрограммы.

        Параметры:
            f (np.ndarray): Массив частот.
            t (np.ndarray): Массив времен.
            Sxx_dB (np.ndarray): Спектрограмма в дБ.
            t_start (float): Начало временного сегмента.
            params (Dict): Параметры визуализации.
            overlay_data (Optional[Dict]): Данные для наложения поверх спектрограммы.
        """
        # Удаление старого colorbar
        if self.cbar_spectro is not None:
            self.cbar_spectro.remove()
            self.cbar_spectro = None

        self.ax_spectro.clear()
        self.ax_spectro.set_facecolor("#1e1e1e")

        # Отображение основной спектрограммы
        im = self.ax_spectro.pcolormesh(
            t + t_start, f, Sxx_dB, shading=params["shading"], cmap=params["cmap"], alpha=0.7
        )

        # Наложение CSV данных поверх основной спектрограммы
        if overlay_data is not None:
            f_overlay = overlay_data["frequencies"]
            t_overlay = overlay_data["times"]
            Sxx_overlay = overlay_data["spectrogram"]

            # Проверяем, пересекаются ли диапазоны времени
            t_main = t + t_start
            t_overlay_start = float(t_overlay[0])
            t_overlay_end = float(t_overlay[-1])
            t_main_start = float(t_main[0])
            t_main_end = float(t_main[-1])

            # Находим пересечение временных диапазонов
            t_intersect_start = max(t_main_start, t_overlay_start)
            t_intersect_end = min(t_main_end, t_overlay_end)

            if t_intersect_start < t_intersect_end:
                # Находим индексы для наложенных данных в пределах пересечения
                mask_overlay = (t_overlay >= t_intersect_start) & (t_overlay <= t_intersect_end)
                t_overlay_segment = t_overlay[mask_overlay]
                idx_overlay_start = np.where(mask_overlay)[0][0]
                idx_overlay_end = np.where(mask_overlay)[0][-1] + 1

                if len(t_overlay_segment) > 0:
                    # Получаем сегмент наложенных данных
                    Sxx_overlay_segment = Sxx_overlay[:, idx_overlay_start:idx_overlay_end]

                    # Отображаем наложенные данные с другим цветом и прозрачностью
                    try:
                        im_overlay = self.ax_spectro.pcolormesh(
                            t_overlay_segment,
                            f_overlay,
                            Sxx_overlay_segment,
                            shading=params["shading"],
                            cmap="hot",
                            alpha=0.5,
                            vmin=params["db_min"],
                            vmax=params["db_max"],
                        )
                    except Exception:
                        pass  # Если отображение не удалось, просто пропускаем наложение

        self.ax_spectro.set_ylabel("Частота (Гц)")
        self.ax_spectro.set_xlabel("Время (с)")
        title = "Спектрограмма"
        if overlay_data is not None:
            title += " (с наложением CSV)"
        self.ax_spectro.set_title(title)
        self.ax_spectro.set_ylim(0, params["freq_limit"])
        self._configure_axes_style(self.ax_spectro)

        self.cbar_spectro = self.fig_spectro.colorbar(
            im, ax=self.ax_spectro, label="Амплитуда (dB)"
        )
        self.cbar_spectro.set_label("Амплитуда (dB)", color="#ffffff")
        self.cbar_spectro.ax.yaxis.set_tick_params(colors="#ffffff")
        self.cbar_spectro.outline.set_edgecolor("#ffffff")

    def update_volume(
        self, time: np.ndarray, envelope: np.ndarray, t_start: float, t_end: float
    ) -> None:
        """
        Обновляет график громкости.

        Параметры:
            time (np.ndarray): Массив времен.
            envelope (np.ndarray): Огибающая громкости.
            t_start (float): Начало временного сегмента.
            t_end (float): Конец временного сегмента.
        """
        self.ax_volume.clear()
        self.ax_volume.set_facecolor("#1e1e1e")

        self.ax_volume.plot(time, envelope, linewidth=1, color="#00ff00")
        self.ax_volume.set_xlabel("Время (с)")
        self.ax_volume.set_ylabel("Амплитуда")
        self.ax_volume.set_title("График громкости")
        self.ax_volume.grid(True, alpha=0.3, color="#555555")
        self._configure_axes_style(self.ax_volume)

    def align_plots(self) -> None:
        """Выравнивает графики по ширине."""
        # Обновление обоих canvas
        self.fig_spectro.tight_layout()
        self.fig_volume.tight_layout()

        # После tight_layout выравниваем позиции
        spectro_pos = self.ax_spectro.get_position()
        volume_pos = self.ax_volume.get_position()
        self.ax_volume.set_position(
            [spectro_pos.x0, volume_pos.y0, spectro_pos.width, volume_pos.height]
        )

        self.canvas_spectro.draw()
        self.canvas_volume.draw()

