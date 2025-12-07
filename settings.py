"""
Модуль для работы с настройками приложения.

Обеспечивает загрузку, сохранение и управление настройками анализа голосовых файлов.
"""

import json
import os
import sys
from typing import Dict
from tkinter import messagebox
from pathlib import Path


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
            config_file (str): Имя файла конфигурации.
        """
        # Используем папку пользователя для сохранения настроек
        # Это более безопасно и не требует прав администратора
        if sys.platform == "win32":
            # Windows: AppData\Local\VoiceAnalyzer
            config_dir = Path(os.getenv("LOCALAPPDATA", "")) / "VoiceAnalyzer"
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/VoiceAnalyzer
            config_dir = Path.home() / "Library" / "Application Support" / "VoiceAnalyzer"
        else:
            # Linux: ~/.config/VoiceAnalyzer
            config_dir = Path.home() / ".config" / "VoiceAnalyzer"

        # Создаем директорию, если её нет
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Если не удалось создать в папке пользователя, используем папку приложения
            if getattr(sys, "frozen", False):
                config_dir = Path(os.path.dirname(sys.executable))
            else:
                config_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        self.config_file = config_dir / config_file

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
            # Убеждаемся, что директория существует
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except PermissionError:
            messagebox.showerror(
                "Ошибка доступа",
                f"Антивирус или система безопасности блокирует сохранение настроек.\n\n"
                f"Путь: {self.config_file}\n\n"
                f"Решение:\n"
                f"1. Добавьте приложение в исключения антивируса\n"
                f"2. Запустите программу от имени администратора\n"
                f"3. Проверьте права доступа к папке"
            )
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить настройки: {str(e)}\n\nПуть: {self.config_file}"
            )

