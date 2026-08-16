$Root='C:\Ponto_Online_Pro'
Get-Process python,pythonw -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "$Root*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName 'Ponto Online Pro - TCP 5000' -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\Desktop\Ponto Online Pro.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Ponto Online Pro.lnk" -Force -ErrorAction SilentlyContinue
Write-Host 'Atalhos e regra de firewall removidos. A pasta C:\Ponto_Online_Pro pode ser excluída manualmente para preservar o banco e as fotos.'
