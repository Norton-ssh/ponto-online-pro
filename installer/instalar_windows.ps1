$ErrorActionPreference = 'Stop'
$Root = 'C:\Ponto_Online_Pro'
$Source = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $Root, $LogDir | Out-Null
function Log($msg) { Add-Content -Path (Join-Path $LogDir 'install.log') -Value ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg) }
Log 'Iniciando instalação V2.2'
Write-Host 'Ponto Online Pro V2.2' -ForegroundColor Cyan
Copy-Item "$Source\*" $Root -Recurse -Force -Exclude 'venv','instance','logs'
Set-Location $Root
function Find-Python {
  $c=@("$env:LOCALAPPDATA\Programs\Python\Python313\python.exe","$env:LOCALAPPDATA\Programs\Python\Python312\python.exe","$env:LOCALAPPDATA\Programs\Python\Python311\python.exe","$env:ProgramFiles\Python313\python.exe","$env:ProgramFiles\Python312\python.exe","$env:ProgramFiles\Python311\python.exe")
  foreach($p in $c){ if(Test-Path $p){ try{ $v=& $p --version 2>&1 | Out-String; if($v -match 'Python 3\.(11|12|13)'){return $p} }catch{} } }
  try{ $cmd=Get-Command python.exe -ErrorAction Stop; $v=& $cmd.Source --version 2>&1 | Out-String; if($v -match 'Python 3\.(11|12|13)'){return $cmd.Source} }catch{}
  return $null
}
$Python=Find-Python
if(-not $Python){
  Write-Host 'Python não encontrado. Baixando Python 3.12...' -ForegroundColor Yellow
  $url='https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe'; $tmp=Join-Path $env:TEMP 'python-3.12.10-amd64.exe'
  Invoke-WebRequest $url -OutFile $tmp -UseBasicParsing
  Start-Process $tmp -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0' -Wait
  Start-Sleep 3; $Python=Find-Python
}
if(-not $Python){throw 'Python 3.11/3.12/3.13 não foi encontrado após a instalação.'}
Log "Python=$Python"
$Venv=Join-Path $Root 'venv'; $Vpy=Join-Path $Venv 'Scripts\python.exe'
if(Test-Path $Venv){ Remove-Item $Venv -Recurse -Force }
Write-Host 'Criando ambiente virtual...' -ForegroundColor Cyan
& $Python -m venv $Venv 2>&1 | Tee-Object -FilePath (Join-Path $LogDir 'venv.log')
if($LASTEXITCODE -ne 0 -or -not(Test-Path $Vpy)){throw 'Falha ao criar ambiente virtual.'}
Write-Host 'Instalando dependências...' -ForegroundColor Cyan
& $Vpy -m pip install --upgrade pip --disable-pip-version-check 2>&1 | Tee-Object -FilePath (Join-Path $LogDir 'pip.log')
if($LASTEXITCODE -ne 0){throw 'Falha ao atualizar pip.'}
& $Vpy -m pip install -r (Join-Path $Root 'requirements.txt') --disable-pip-version-check 2>&1 | Tee-Object -FilePath (Join-Path $LogDir 'pip-install.log')
if($LASTEXITCODE -ne 0){throw 'Falha ao instalar dependências.'}
Write-Host 'Testando aplicação...' -ForegroundColor Cyan
$TestScript=Join-Path $Root 'installer\install_test.py'
$TestLog=Join-Path $LogDir 'install_test.log'
& $Vpy $TestScript *> $TestLog
$code=$LASTEXITCODE
if($code -ne 0){
  Write-Host 'ERRO REAL DA APLICAÇÃO:' -ForegroundColor Red
  Get-Content $TestLog | ForEach-Object { Write-Host $_ -ForegroundColor Red }
  throw "Teste da aplicação falhou. Veja $TestLog"
}
Write-Host 'Aplicação e banco: OK' -ForegroundColor Green
Remove-Item (Join-Path $Root 'instance\certs\server.crt') -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $Root 'instance\certs\server.key') -Force -ErrorAction SilentlyContinue
Write-Host 'Gerando certificado HTTPS local...' -ForegroundColor Cyan
& $Vpy (Join-Path $Root 'desktop\generate_cert.py') *> (Join-Path $LogDir 'cert.log')
if($LASTEXITCODE -ne 0){ throw 'Falha ao gerar certificado HTTPS local.' }
Write-Host 'HTTPS local configurado.' -ForegroundColor Green
try{
  $rule=Get-NetFirewallRule -DisplayName 'Ponto Online Pro - TCP 5000' -ErrorAction SilentlyContinue
  if($rule){ Set-NetFirewallRule -DisplayName 'Ponto Online Pro - TCP 5000' -Enabled True -Profile Any -Action Allow | Out-Null }
  else { New-NetFirewallRule -DisplayName 'Ponto Online Pro - TCP 5000' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any | Out-Null }
  & netsh advfirewall firewall delete rule name="Ponto Online Pro 5000" | Out-Null
  & netsh advfirewall firewall add rule name="Ponto Online Pro 5000" dir=in action=allow protocol=TCP localport=5000 profile=any | Out-Null
  Log 'Firewall TCP 5000 liberado em todos os perfis.'
}catch{Log "Firewall: $($_.Exception.Message)"}
$Desktop=[Environment]::GetFolderPath('Desktop'); $Startup=Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'; $ws=Join-Path $env:WINDIR 'System32\wscript.exe'; $vbs=Join-Path $Root 'desktop\start_hidden.vbs'; $ico=Join-Path $Root 'desktop\ponto.ico'; $shell=New-Object -ComObject WScript.Shell
foreach($folder in @($Desktop,$Startup)){New-Item -ItemType Directory -Force -Path $folder|Out-Null;$lnk=$shell.CreateShortcut((Join-Path $folder 'Ponto Online Pro.lnk'));$lnk.TargetPath=$ws;$lnk.Arguments='"'+$vbs+'"';$lnk.WorkingDirectory=$Root;if(Test-Path $ico){$lnk.IconLocation=$ico};$lnk.Save()}
Start-Process $ws -ArgumentList ('"'+$vbs+'"') -WorkingDirectory $Root
$ok=$false
$testUrl='https://127.0.0.1:5000/login'
for($i=1;$i -le 30;$i++){
  Start-Sleep 1
  try{
    $resp=Invoke-WebRequest -Uri $testUrl -SkipCertificateCheck -UseBasicParsing -TimeoutSec 2
    if($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500){$ok=$true;break}
  }catch{}
}
if(-not $ok){
  Write-Host 'O servidor não respondeu.' -ForegroundColor Red
  foreach($lf in @('server.log','launcher.log','https_test.log')){
    $fp=Join-Path $LogDir $lf
    if(Test-Path $fp){ Write-Host "--- $lf ---" -ForegroundColor Yellow; Get-Content $fp | Select-Object -Last 80 }
  }
  throw 'Servidor local não iniciou. Consulte os logs.'
}
# Confirma que o processo continua atendendo depois do primeiro sucesso.
Start-Sleep 3
try{
  $resp2=Invoke-WebRequest -Uri $testUrl -SkipCertificateCheck -UseBasicParsing -TimeoutSec 3
  if($resp2.StatusCode -lt 200 -or $resp2.StatusCode -ge 500){ throw 'Resposta inválida' }
}catch{
  throw 'Servidor respondeu inicialmente, mas não permaneceu ativo. Consulte C:\Ponto_Online_Pro\logs\server.log.'
}
Write-Host 'SERVIDOR LOCAL: OK' -ForegroundColor Green
Log 'Instalação concluída com servidor respondendo.'
Write-Host 'Instalação concluída. Atalho criado na Área de Trabalho.' -ForegroundColor Green
