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
        # Кэш для интерполированных данных наложения
        self.overlay_cache: Optional[Dict] = None

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

        # Подготовка данных для отображения
        Sxx_display = Sxx_dB.copy()

        # Замена данных обработанного звука на данные из CSV в соответствующей области
        if overlay_data is not None:
            f_overlay = overlay_data["frequencies"]
            t_overlay = overlay_data["times"]
            Sxx_overlay = overlay_data["spectrogram"]

            # Временная сетка для наложения
            t_main = t + t_start
            num_time_overlay = min(len(t_overlay), len(t_main))

            if num_time_overlay > 0:
                # Ограничиваем диапазон частот
                f_overlay_limited = f_overlay[f_overlay <= params["freq_limit"]]
                f_main_limited = f[f <= params["freq_limit"]]

                # Проверяем, можно ли обойтись без интерполяции
                can_direct_copy = (
                    len(f_overlay_limited) == len(f_main_limited)
                    and num_time_overlay <= Sxx_display.shape[1]
                    and np.allclose(f_overlay_limited, f_main_limited, atol=1.0)
                )

                if can_direct_copy:
                    # Быстрая замена без интерполяции
                    num_freq = min(len(f_overlay_limited), Sxx_display.shape[0])
                    Sxx_display[:num_freq, :num_time_overlay] = Sxx_overlay[
                        :num_freq, :num_time_overlay
                    ]
                else:
                    # Интерполяция нужна, но используем кэш если параметры не изменились
                    cache_key = (
                        len(f_main_limited),
                        num_time_overlay,
                        params["freq_limit"],
                        id(overlay_data),
                    )

                    # Проверяем кэш
                    if (
                        self.overlay_cache is not None
                        and self.overlay_cache.get("key") == cache_key
                        and self.overlay_cache.get("freq_limit") == params["freq_limit"]
                    ):
                        # Используем кэшированные интерполированные данные
                        Sxx_overlay_interp = self.overlay_cache["data"]
                    else:
                        # Интерполируем и кэшируем результат
                        try:
                            from scipy.interpolate import griddata

                            # Создаем сетки координат для интерполяции
                            t_overlay_grid, f_overlay_grid = np.meshgrid(
                                t_overlay[:num_time_overlay], f_overlay_limited
                            )
                            points_overlay = np.column_stack(
                                [t_overlay_grid.ravel(), f_overlay_grid.ravel()]
                            )
                            values_overlay = Sxx_overlay[
                                : len(f_overlay_limited), :num_time_overlay
                            ].ravel()

                            t_main_grid, f_main_grid = np.meshgrid(
                                t_main[:num_time_overlay], f_main_limited
                            )
                            points_main = np.column_stack(
                                [t_main_grid.ravel(), f_main_grid.ravel()]
                            )

                            # Интерполируем CSV данные на сетку основной спектрограммы
                            Sxx_overlay_interp = griddata(
                                points_overlay,
                                values_overlay,
                                points_main,
                                method="linear",
                                fill_value=np.nan,
                            ).reshape((len(f_main_limited), num_time_overlay))

                            # Кэшируем результат
                            self.overlay_cache = {
                                "key": cache_key,
                                "freq_limit": params["freq_limit"],
                                "data": Sxx_overlay_interp,
                            }
                        except Exception:
                            # Если интерполяция не удалась, пропускаем замену
                            Sxx_overlay_interp = None

                    # Заменяем данные основной спектрограммы на данные из CSV
                    if Sxx_overlay_interp is not None:
                        num_freq = min(len(f_main_limited), Sxx_display.shape[0])
                        num_time = min(num_time_overlay, Sxx_display.shape[1])
                        
                        # Быстрая замена: используем прямое присваивание с маской валидных значений
                        overlay_segment = Sxx_overlay_interp[:num_freq, :num_time]
                        display_segment = Sxx_display[:num_freq, :num_time]
                        
                        # Заменяем только валидные (не NaN) значения
                        valid_mask = ~np.isnan(overlay_segment)
                        if np.any(valid_mask):
                            display_segment[valid_mask] = overlay_segment[valid_mask]
                            Sxx_display[:num_freq, :num_time] = display_segment

        # Отображение спектрограммы (с замененными данными из CSV, если они есть)
        im = self.ax_spectro.pcolormesh(
            t + t_start, f, Sxx_display, shading=params["shading"], cmap=params["cmap"]
        )

        self.ax_spectro.set_ylabel("Частота (Гц)")
        self.ax_spectro.set_xlabel("Время (с)")
        self.ax_spectro.set_title("Спектрограмма")
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

