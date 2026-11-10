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

# На macOS PyInstaller принимает только .icns, не Windows-иконку .ico.
icon_path = 'icon.icns'
if os.path.exists(icon_path):
    icon_arg = f'--icon={icon_path}'
else:
    icon_arg = '--icon=NONE'
    print("Предупреждение: файл icon.icns не найден. Используется иконка по умолчанию.")

# Без --onefile PyInstaller собирает dist/VoiceAnalyzer.app —
# обычное приложение macOS, которое можно открыть двойным щелчком.
PyInstaller.__main__.run([
    'main.py',
    '--name=VoiceAnalyzer',
    '--windowed',
    icon_arg,
    '--hidden-import=tkinter',
    '--hidden-import=matplotlib.backends.backend_tkagg',
    '--hidden-import=scipy.signal',
    '--hidden-import=numpy',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--collect-all=matplotlib',
    '--collect-all=scipy',
    '--collect-all=PIL',
    '--noconfirm',
    '--clean',
])

