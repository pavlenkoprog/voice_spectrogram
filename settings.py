"""
Модуль для работы с настройками приложения.

Обеспечивает загрузку, сохранение и управление настройками анализа голосовых файлов.
"""

import json
import os
from typing import Dict
from tkinter import messagebox


class SettingsManager:
    """Класс для управления настройками приложения."""

    DEFAULT_SETTINGS = {
        "t_start": "0",
        "t_end": "1.0",
        "nperseg": "1024",
        "window": "hann",
        "freq_limit": "20000",
        "noverlap_percent": "90",
        "mode": "magnitude",
        "scaling": "density",
        "db_min": "-50",
        "db_max": "0",
        "shading": "gouraud",
        "cmap": "inferno",
        "smooth_window": "5",
    }

    def __init__(self, config_file: str = "voice_analyzer_config.json") -> None:
        """
        Инициализирует менеджер настроек.

        Параметры:
            config_file (str): Путь к файлу конфигурации.
        """
        self.config_file = config_file

    def get_default_settings(self) -> Dict[str, str]:
        """
        Возвращает настройки по умолчанию.

        Возвращает:
            Dict[str, str]: Словарь с настройками по умолчанию.
        """
        return self.DEFAULT_SETTINGS.copy()

    def load_settings(self) -> Dict[str, str]:
        """
        Загружает настройки из файла конфигурации.

        Возвращает:
            Dict[str, str]: Словарь с настройками.
        """
        default_settings = self.get_default_settings()

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                # Объединяем загруженные настройки с настройками по умолчанию
                result = default_settings.copy()
                result.update(settings)
                return result
            except Exception as e:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Не удалось загрузить настройки: {str(e)}\nИспользуются значения по умолчанию.",
                )
                return default_settings
        else:
            return default_settings

    def save_settings(self, settings: Dict[str, str]) -> None:
        """
        Сохраняет настройки в файл конфигурации.

        Параметры:
            settings (Dict[str, str]): Словарь с настройками для сохранения.
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

