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
# --icon=NONE сюда передавать нельзя: сборка ищет файл с именем NONE и падает.
args = [
    'main.py',
    '--name=VoiceAnalyzer',
    '--windowed',
    '--hidden-import=tkinter',
    '--hidden-import=matplotlib.backends.backend_tkagg',
    '--hidden-import=scipy.signal',
    '--hidden-import=numpy',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--collect-all=matplotlib',
    '--collect-all=scipy',
    '--collect-all=PIL',
    # backend_macosx требует Python-framework и роняет сборку на Homebrew Python.
    '--exclude-module=matplotlib.backends.backend_macosx',
    '--noconfirm',
    '--clean',
]

icon_path = 'icon.icns'
if os.path.exists(icon_path):
    args.append(f'--icon={icon_path}')
else:
    print("Предупреждение: файл icon.icns не найден. Используется иконка по умолчанию.")

# Без --onefile PyInstaller собирает dist/VoiceAnalyzer.app —
# обычное приложение macOS, которое можно открыть двойным щелчком.
PyInstaller.__main__.run(args)

