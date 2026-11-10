#!/bin/bash
# Двойной щелчок в Finder собирает VoiceAnalyzer для macOS.
# chmod +x build_macos.command
cd "$(dirname "$0")" || exit 1

pause() {
  echo
  read -r -p "Нажмите Enter, чтобы закрыть окно..."
}

fail() {
  echo "$1"
  pause
  exit 1
}

echo "Сборка VoiceAnalyzer"
echo "Папка: $(pwd)"
echo

python3 -m venv venv || fail "Не удалось создать виртуальное окружение (нужен python3)."
# shellcheck disable=SC1091
source venv/bin/activate || fail "Не удалось активировать venv."
pip install -r requirements.txt || fail "Не удалось установить зависимости."
python build_macos.py || fail "Сборка завершилась с ошибкой."

echo
echo "Готово. Приложение: dist/VoiceAnalyzer.app"
pause
