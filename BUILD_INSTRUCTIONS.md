# Инструкции по сборке исполняемого файла

## Подготовка

1. Убедитесь, что установлен Python 3.8 или выше
2. Активируйте виртуальное окружение (если используется):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Сборка для Windows

1. На Windows выполните:
   ```bash
   python build_windows.py
   ```

2. Исполняемый файл будет находиться в папке `dist/VoiceAnalyzer.exe`

3. Для запуска просто дважды кликните на `VoiceAnalyzer.exe`

## Сборка для macOS

1. На macOS выполните:
   ```bash
   python build_macos.py
   ```

2. Исполняемый файл будет находиться в папке `dist/VoiceAnalyzer`

3. При первом запуске macOS может показать предупреждение о безопасности. 
   Для запуска:
   - Откройте "Системные настройки" → "Безопасность и конфиденциальность"
   - Нажмите "Открыть в любом случае" рядом с предупреждением

## Альтернативный способ (через командную строку)

### Windows:
```bash
pyinstaller --name=VoiceAnalyzer --onefile --windowed --hidden-import=tkinter --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=scipy.signal --collect-all=matplotlib --collect-all=scipy main.py
```

### macOS:
```bash
pyinstaller --name=VoiceAnalyzer --onefile --windowed --hidden-import=tkinter --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=scipy.signal --collect-all=matplotlib --collect-all=scipy main.py
```

## Примечания

- Размер исполняемого файла будет около 100-200 МБ из-за включенных библиотек (numpy, scipy, matplotlib)
- Для сборки macOS версии нужен компьютер с macOS
- Для сборки Windows версии нужен компьютер с Windows
- Файл конфигурации `voice_analyzer_config.json` будет создаваться автоматически рядом с исполняемым файлом при первом запуске

## Устранение проблем

Если при запуске возникают ошибки:

1. Убедитесь, что все зависимости установлены
2. Попробуйте собрать без флага `--onefile` (создаст папку с файлами):
   ```bash
   pyinstaller --name=VoiceAnalyzer --windowed main.py
   ```
3. Проверьте логи в консоли при запуске

