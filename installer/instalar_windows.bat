@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_windows.ps1"
if errorlevel 1 (
  echo.
  echo INSTALACAO NAO CONCLUIDA. Veja C:\Ponto_Online_Pro\logs
  pause
  exit /b 1
)
echo.
echo INSTALACAO CONCLUIDA.
pause
