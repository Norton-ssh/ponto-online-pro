@echo off
cd /d %~dp0..
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist uploads mkdir uploads
if not exist instance mkdir instance
netsh advfirewall firewall add rule name="Ponto Online Pro 5000" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Ponto Online Pro.lnk');$s.TargetPath='%~dp0iniciar_local.bat';$s.WorkingDirectory='%~dp0..';$s.Save()"
echo Instalacao concluida. Use o atalho Ponto Online Pro na area de trabalho.
pause
