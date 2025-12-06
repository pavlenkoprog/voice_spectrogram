"""
Комплексная программа для анализа голосовых файлов с графиками спектрограммы и громкости.

Позволяет загружать WAV файлы, настраивать параметры анализа и визуализировать
спектрограмму и график громкости в реальном времени.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.io import wavfile
from scipy.signal import spectrogram
from typing import Optional, Tuple

try:
    import ttkthemes
    HAS_TTKTHEMES = True
except ImportError:
    HAS_TTKTHEMES = False


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

        self.sample_rate: Optional[int] = None
        self.data: Optional[np.ndarray] = None
        self.file_path: Optional[str] = None
        self.cbar_spectro: Optional[object] = None

        self._setup_dark_theme()
        self._create_widgets()
        self._setup_defaults()

    def _setup_dark_theme(self) -> None:
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
            except:
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
        style.configure("TLabelFrame", background=bg_color, foreground=fg_color, 
                       bordercolor=border_color, relief="solid", borderwidth=1)
        style.configure("TLabelFrame.Label", background=bg_color, foreground=fg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=button_bg, foreground=fg_color, 
                       bordercolor=border_color)
        style.map("TButton", 
                  background=[("active", button_active), ("pressed", "#606060")],
                  bordercolor=[("active", "#666666")])
        style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color, 
                       bordercolor=border_color, insertcolor=fg_color,
                       selectbackground="#606060", selectforeground=fg_color)
        style.map("TEntry", 
                  fieldbackground=[("focus", entry_bg)],
                  bordercolor=[("focus", "#777777")])
        style.configure("TCombobox", fieldbackground=entry_bg, foreground=fg_color,
                       bordercolor=border_color, arrowcolor=fg_color,
                       selectbackground="#606060", selectforeground=fg_color)
        style.map("TCombobox", 
                  fieldbackground=[("readonly", entry_bg)],
                  selectbackground=[("readonly", "#606060")],
                  bordercolor=[("focus", "#777777")])
        
        # Темная тема для matplotlib
        plt.style.use("dark_background")

    def _create_widgets(self) -> None:
        """Создает виджеты интерфейса."""
        # Настройка grid для всего окна
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # Графики могут сжиматься
        # Панель настроек (row=2) без weight - всегда видна

        # Верхняя панель с кнопкой загрузки
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(
            top_frame, text="Загрузить WAV файл", command=self._load_file
        ).pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(top_frame, text="Файл не загружен")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # Контейнер для графиков с процентным распределением
        graphs_container = ttk.Frame(self.root)
        graphs_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)

        # Настройка grid для процентного распределения графиков
        graphs_container.columnconfigure(0, weight=1)
        graphs_container.rowconfigure(0, weight=60)  # Спектрограмма 60%
        graphs_container.rowconfigure(1, weight=20)  # Громкость 20%

        # Фрейм для спектрограммы (60%)
        spectro_frame = ttk.Frame(graphs_container)
        spectro_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # График спектрограммы
        self.fig_spectro = Figure(figsize=(12, 6), dpi=100, facecolor="#1e1e1e")
        self.ax_spectro = self.fig_spectro.add_subplot(111, facecolor="#1e1e1e")
        self.ax_spectro.tick_params(colors="#ffffff")
        self.ax_spectro.xaxis.label.set_color("#ffffff")
        self.ax_spectro.yaxis.label.set_color("#ffffff")
        self.ax_spectro.title.set_color("#ffffff")
        self.ax_spectro.spines["bottom"].set_color("#ffffff")
        self.ax_spectro.spines["top"].set_color("#ffffff")
        self.ax_spectro.spines["right"].set_color("#ffffff")
        self.ax_spectro.spines["left"].set_color("#ffffff")

        self.canvas_spectro = FigureCanvasTkAgg(self.fig_spectro, spectro_frame)
        self.canvas_spectro.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Фрейм для графика громкости (20%)
        volume_frame = ttk.Frame(graphs_container)
        volume_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # График громкости
        self.fig_volume = Figure(figsize=(12, 2), dpi=100, facecolor="#1e1e1e")
        self.ax_volume = self.fig_volume.add_subplot(111, facecolor="#1e1e1e")
        self.ax_volume.tick_params(colors="#ffffff")
        self.ax_volume.xaxis.label.set_color("#ffffff")
        self.ax_volume.yaxis.label.set_color("#ffffff")
        self.ax_volume.title.set_color("#ffffff")
        self.ax_volume.spines["bottom"].set_color("#ffffff")
        self.ax_volume.spines["top"].set_color("#ffffff")
        self.ax_volume.spines["right"].set_color("#ffffff")
        self.ax_volume.spines["left"].set_color("#ffffff")

        self.canvas_volume = FigureCanvasTkAgg(self.fig_volume, volume_frame)
        self.canvas_volume.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Панель настроек (приоритетная, всегда видна, не сжимается)
        # Используем обычный Frame вместо LabelFrame для лучшего контроля цвета
        settings_container = tk.Frame(self.root, bg="#2b2b2b", relief="solid", bd=1)
        settings_container.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Заголовок панели
        settings_label = tk.Label(
            settings_container, 
            text="Настройки", 
            bg="#2b2b2b", 
            fg="#ffffff",
            font=("TkDefaultFont", 9, "bold")
        )
        settings_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Фрейм для содержимого
        settings_frame = tk.Frame(settings_container, bg="#2b2b2b")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Контейнер для колонок и кнопки
        columns_container = tk.Frame(settings_frame, bg="#2b2b2b")
        columns_container.pack(fill=tk.X, pady=5)

        # Колонка 1: Время
        col1 = tk.Frame(columns_container, bg="#2b2b2b")
        col1.pack(side=tk.LEFT, padx=10)
        
        row = tk.Frame(col1, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Начало времени (с):", bg="#2b2b2b", fg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        self.t_start_var = tk.StringVar(value="0")
        ttk.Entry(row, textvariable=self.t_start_var, width=12).pack(side=tk.LEFT, padx=5)
        
        row = tk.Frame(col1, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Конец времени (с):", bg="#2b2b2b", fg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        self.t_end_var = tk.StringVar(value="1.0")
        ttk.Entry(row, textvariable=self.t_end_var, width=12).pack(side=tk.LEFT, padx=5)

        # Колонка 2: Окно
        col2 = tk.Frame(columns_container, bg="#2b2b2b")
        col2.pack(side=tk.LEFT, padx=10)
        
        row = tk.Frame(col2, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Размер окна:", bg="#2b2b2b", fg="#ffffff", width=12, anchor="w").pack(side=tk.LEFT)
        self.nperseg_var = tk.StringVar(value="1024")
        ttk.Entry(row, textvariable=self.nperseg_var, width=12).pack(side=tk.LEFT, padx=5)
        
        row = tk.Frame(col2, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Функция окна:", bg="#2b2b2b", fg="#ffffff", width=12, anchor="w").pack(side=tk.LEFT)
        self.window_var = tk.StringVar(value="hann")
        window_combo = ttk.Combobox(
            row,
            textvariable=self.window_var,
            values=["hann", "hamming", "blackman", "bartlett", "boxcar"],
            width=10,
            state="readonly",
        )
        window_combo.pack(side=tk.LEFT, padx=5)

        # Колонка 3: Частота и перекрытие
        col3 = tk.Frame(columns_container, bg="#2b2b2b")
        col3.pack(side=tk.LEFT, padx=10)
        
        row = tk.Frame(col3, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Макс. частота (Гц):", bg="#2b2b2b", fg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        self.freq_limit_var = tk.StringVar(value="20000")
        ttk.Entry(row, textvariable=self.freq_limit_var, width=12).pack(side=tk.LEFT, padx=5)
        
        row = tk.Frame(col3, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Перекрытие (%):", bg="#2b2b2b", fg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        self.noverlap_percent_var = tk.StringVar(value="90")
        ttk.Entry(row, textvariable=self.noverlap_percent_var, width=12).pack(side=tk.LEFT, padx=5)

        # Колонка 4: Режим и масштабирование
        col4 = tk.Frame(columns_container, bg="#2b2b2b")
        col4.pack(side=tk.LEFT, padx=10)
        
        row = tk.Frame(col4, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Режим:", bg="#2b2b2b", fg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="magnitude")
        mode_combo = ttk.Combobox(
            row,
            textvariable=self.mode_var,
            values=["magnitude", "psd", "phase", "angle", "complex"],
            width=10,
            state="readonly",
        )
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        row = tk.Frame(col4, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Масштабирование:", bg="#2b2b2b", fg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        self.scaling_var = tk.StringVar(value="density")
        scaling_combo = ttk.Combobox(
            row,
            textvariable=self.scaling_var,
            values=["density", "spectrum"],
            width=10,
            state="readonly",
        )
        scaling_combo.pack(side=tk.LEFT, padx=5)

        # Колонка 5: Диапазон дБ
        col5 = tk.Frame(columns_container, bg="#2b2b2b")
        col5.pack(side=tk.LEFT, padx=10)
        
        row = tk.Frame(col5, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Мин. дБ:", bg="#2b2b2b", fg="#ffffff", width=8, anchor="w").pack(side=tk.LEFT)
        self.db_min_var = tk.StringVar(value="-50")
        ttk.Entry(row, textvariable=self.db_min_var, width=12).pack(side=tk.LEFT, padx=5)
        
        row = tk.Frame(col5, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Макс. дБ:", bg="#2b2b2b", fg="#ffffff", width=8, anchor="w").pack(side=tk.LEFT)
        self.db_max_var = tk.StringVar(value="0")
        ttk.Entry(row, textvariable=self.db_max_var, width=12).pack(side=tk.LEFT, padx=5)

        # Кнопка обновления справа от колонок
        ttk.Button(
            columns_container, text="Обновить графики", command=self._update_plots
        ).pack(side=tk.LEFT, padx=10)

        # Скрытые переменные для параметров, убранных из интерфейса
        self.shading_var = tk.StringVar(value="gouraud")
        self.cmap_var = tk.StringVar(value="inferno")
        self.smooth_window_var = tk.StringVar(value="5")

    def _setup_defaults(self) -> None:
        """Устанавливает значения по умолчанию."""
        pass

    def _load_file(self) -> None:
        """
        Загружает WAV файл для анализа.
        """
        file_path = filedialog.askopenfilename(
            title="Выберите WAV файл",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            self.sample_rate, self.data = wavfile.read(file_path)
            if len(self.data.shape) > 1:
                self.data = self.data[:, 0]

            self.file_path = file_path
            self.file_label.config(text=f"Файл: {file_path.split('/')[-1]}")

            # Устанавливаем по умолчанию первую секунду
            self.t_start_var.set("0")
            self.t_end_var.set("1.0")

            self._update_plots()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _get_parameters(self) -> dict:
        """
        Получает параметры из интерфейса.

        Возвращает:
            dict: Словарь с параметрами анализа.
        """
        try:
            return {
                "t_start": float(self.t_start_var.get()),
                "t_end": float(self.t_end_var.get()),
                "nperseg": int(self.nperseg_var.get()),
                "freq_limit": float(self.freq_limit_var.get()),
                "window": self.window_var.get(),
                "scaling": self.scaling_var.get(),
                "mode": self.mode_var.get(),
                "cmap": self.cmap_var.get(),
                "shading": self.shading_var.get(),
                "noverlap_percent": float(self.noverlap_percent_var.get()),
                "db_min": float(self.db_min_var.get()),
                "db_max": float(self.db_max_var.get()),
                "smooth_window_ms": float(self.smooth_window_var.get()),
            }
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверное значение параметра: {str(e)}")
            return None

    def _update_plots(self) -> None:
        """
        Обновляет графики спектрограммы и громкости.
        """
        if self.data is None or self.sample_rate is None:
            return

        params = self._get_parameters()
        if params is None:
            return

        try:
            # Выбор временного сегмента
            t_start = params["t_start"]
            t_end = params["t_end"]

            start_idx = int(t_start * self.sample_rate)
            end_idx = int(t_end * self.sample_rate)

            if start_idx < 0:
                start_idx = 0
            if end_idx > len(self.data):
                end_idx = len(self.data)
            if start_idx >= end_idx:
                messagebox.showerror("Ошибка", "t_start должен быть меньше t_end")
                return

            data_segment = self.data[start_idx:end_idx]

            # Параметры спектрограммы
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

            # Очистка и отрисовка спектрограммы
            # Удаление старого colorbar
            if self.cbar_spectro is not None:
                self.cbar_spectro.remove()
                self.cbar_spectro = None
            
            self.ax_spectro.clear()
            self.ax_spectro.set_facecolor("#1e1e1e")
            im = self.ax_spectro.pcolormesh(
                t + t_start,
                f,
                Sxx_dB,
                shading=params["shading"],
                cmap=params["cmap"],
            )
            self.ax_spectro.set_ylabel("Частота (Гц)")
            self.ax_spectro.set_xlabel("Время (с)")
            self.ax_spectro.set_title("Спектрограмма")
            self.ax_spectro.set_ylim(0, freq_limit)
            self.ax_spectro.tick_params(colors="#ffffff")
            self.ax_spectro.xaxis.label.set_color("#ffffff")
            self.ax_spectro.yaxis.label.set_color("#ffffff")
            self.ax_spectro.title.set_color("#ffffff")
            self.ax_spectro.spines["bottom"].set_color("#ffffff")
            self.ax_spectro.spines["top"].set_color("#ffffff")
            self.ax_spectro.spines["right"].set_color("#ffffff")
            self.ax_spectro.spines["left"].set_color("#ffffff")
            
            self.cbar_spectro = self.fig_spectro.colorbar(im, ax=self.ax_spectro, label="Амплитуда (dB)")
            self.cbar_spectro.set_label("Амплитуда (dB)", color="#ffffff")
            self.cbar_spectro.ax.yaxis.set_tick_params(colors="#ffffff")
            self.cbar_spectro.outline.set_edgecolor("#ffffff")
            
            # Получаем позицию axes спектрограммы после добавления colorbar
            spectro_pos = self.ax_spectro.get_position()

            # График громкости
            self.ax_volume.clear()
            self.ax_volume.set_facecolor("#1e1e1e")
            
            # Устанавливаем ту же ширину области графика, что и у спектрограммы
            volume_pos = self.ax_volume.get_position()
            self.ax_volume.set_position([spectro_pos.x0, volume_pos.y0, 
                                         spectro_pos.width, volume_pos.height])

            # Нормализация данных
            segment_normalized = data_segment / np.max(np.abs(data_segment)) if np.max(np.abs(data_segment)) > 0 else data_segment

            # Мгновенная амплитуда
            abs_signal = np.abs(segment_normalized)

            # Сглаживание
            smooth_window_ms = params["smooth_window_ms"]
            window_size = int(smooth_window_ms * self.sample_rate / 1000)
            if window_size > 0:
                window = np.ones(window_size) / window_size
                envelope = np.convolve(abs_signal, window, mode="same")
            else:
                envelope = abs_signal

            # Шкала времени
            time = np.linspace(t_start, t_end, len(envelope))

            self.ax_volume.plot(time, envelope, linewidth=1, color="#00ff00")
            self.ax_volume.set_xlabel("Время (с)")
            self.ax_volume.set_ylabel("Амплитуда")
            self.ax_volume.set_title("График громкости")
            self.ax_volume.grid(True, alpha=0.3, color="#555555")
            self.ax_volume.tick_params(colors="#ffffff")
            self.ax_volume.xaxis.label.set_color("#ffffff")
            self.ax_volume.yaxis.label.set_color("#ffffff")
            self.ax_volume.title.set_color("#ffffff")
            self.ax_volume.spines["bottom"].set_color("#ffffff")
            self.ax_volume.spines["top"].set_color("#ffffff")
            self.ax_volume.spines["right"].set_color("#ffffff")
            self.ax_volume.spines["left"].set_color("#ffffff")

            # Обновление обоих canvas
            # Используем tight_layout для правильного размещения элементов
            self.fig_spectro.tight_layout()
            self.fig_volume.tight_layout()
            
            # После tight_layout снова выравниваем позиции
            spectro_pos = self.ax_spectro.get_position()
            volume_pos = self.ax_volume.get_position()
            self.ax_volume.set_position([spectro_pos.x0, volume_pos.y0, 
                                         spectro_pos.width, volume_pos.height])
            
            self.canvas_spectro.draw()
            self.canvas_volume.draw()

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

