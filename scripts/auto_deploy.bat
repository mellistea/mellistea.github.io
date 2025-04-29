@echo off
cd /d %~dp0
echo Запуск генерации Markdown...
python generate_md.py
if %ERRORLEVEL% NEQ 0 (
    echo [Ошибка] generate_md.py завершился с ошибкой. Прерываю выполнение.
    pause
    exit /b %ERRORLEVEL%
)
echo Готово. Теперь деплой...
python deploy.py
pause
