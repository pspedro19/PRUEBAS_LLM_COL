@echo off
echo Iniciando backend ICFES AI Tutor...
echo.

REM Activar entorno virtual
call venv-all\Scripts\activate.bat

REM Cambiar al directorio del backend
cd backend

REM Verificar que Python funciona
echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo Error: Python no encontrado en el entorno virtual
    pause
    exit /b 1
)

REM Iniciar el servidor
echo.
echo Iniciando servidor en http://127.0.0.1:8000
echo Presiona Ctrl+C para detener
echo.
python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000

pause 