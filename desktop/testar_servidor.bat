@echo off
setlocal
cd /d C:\Ponto_Online_Pro
if not exist "venv\Scripts\python.exe" (
  echo Python do ambiente nao encontrado.
  pause
  exit /b 1
)
echo Testando aplicacao diretamente...
"venv\Scripts\python.exe" run_local.py
pause
