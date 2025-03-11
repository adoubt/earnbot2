@echo off
REM Активация виртуального окружения
set VENV_PATH=venv\Scripts\python.exe
set SCRIPT_PATH=main.py

REM Проверяем, существует ли интерпретатор Python в виртуальном окружении
if exist %VENV_PATH% (
    :start
    %VENV_PATH% %SCRIPT_PATH%

    REM Ждем 1 час (3600 секунд)
    timeout /t 1200
    goto start
) else (
    echo Виртуальное окружение не найдено. Убедитесь, что venv настроен корректно.
    pause
)

