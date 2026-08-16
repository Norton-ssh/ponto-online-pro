@echo off
setlocal
set "ROOT=C:\Ponto_Online_Pro"
title Ponto Online Pro - Teste de Rede Wi-Fi
color 0A
echo ================================================
echo       PONTO ONLINE PRO - TESTE DE REDE
echo ================================================
echo.
echo [1] Enderecos IPv4 deste computador:
ipconfig | findstr /R /C:"IPv4" /C:"Adaptador" /C:"adapter"
echo.
echo [2] Teste local 127.0.0.1:5000:
powershell -NoProfile -Command "try{$r=Invoke-WebRequest 'http://127.0.0.1:5000/login' -UseBasicParsing -TimeoutSec 3; Write-Host ('OK - HTTP '+$r.StatusCode) -ForegroundColor Green}catch{Write-Host ('FALHOU - '+$_.Exception.Message) -ForegroundColor Red}"
echo.
echo [3] Portas TCP 5000 em escuta:
netstat -ano | findstr ":5000"
echo.
echo [4] Regras de firewall do Ponto Online Pro:
netsh advfirewall firewall show rule name="Ponto Online Pro 5000"
netsh advfirewall firewall show rule name="Ponto Online Pro - TCP 5000"
echo.
echo Se o celular nao abrir:
echo - confirme que ele esta na MESMA Wi-Fi deste computador;
echo - desligue temporariamente os dados moveis do celular;
echo - use o IPv4 mostrado acima, por exemplo http://192.168.1.100:5000/login;
echo - se a rede Wi-Fi for de empresa/hotel, pode haver isolamento entre dispositivos.
echo.
pause
