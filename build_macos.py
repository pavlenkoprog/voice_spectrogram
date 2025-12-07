"""
Скрипт для сборки исполняемого файла для macOS.

Использование:
    python build_macos.py

Примечание:
    Для установки иконки поместите файл icon.icns в корень проекта.
    Если файл отсутствует, будет использована иконка по умолчанию.
"""

import os
import PyInstaller.__main__

# Проверка наличия иконки
icon_path = 'icon.icns'
if os.path.exists(icon_path):
    icon_arg = f'--icon={icon_path}'
else:
    icon_arg = '--icon=NONE'
    print("Предупреждение: файл icon.icns не найден. Используется иконка по умолчанию.")

PyInstaller.__main__.run([
    'main.py',
    '--name=VoiceAnalyzer',
    '--onefile',
    '--windowed',
    icon_arg,
    '--hidden-import=tkinter',
    '--hidden-import=matplotlib.backends.backend_tkagg',
    '--hidden-import=scipy.signal',
    '--hidden-import=numpy',
    '--collect-all=matplotlib',
    '--collect-all=scipy',
    '--noconfirm',
    '--clean',
])

