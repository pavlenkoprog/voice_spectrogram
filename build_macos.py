"""
Скрипт для сборки исполняемого файла для macOS.

Использование:
    python build_macos.py
"""

import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=VoiceAnalyzer',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--hidden-import=tkinter',
    '--hidden-import=matplotlib.backends.backend_tkagg',
    '--hidden-import=scipy.signal',
    '--hidden-import=numpy',
    '--collect-all=matplotlib',
    '--collect-all=scipy',
    '--noconfirm',
    '--clean',
])

