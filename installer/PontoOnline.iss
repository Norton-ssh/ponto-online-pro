; Fonte para gerar um instalador EXE com Inno Setup em um Windows.
#define MyAppName "Ponto Online Pro"
#define MyAppVersion "1.2"
#define MyAppPublisher "Ponto Online Pro"
#define MyAppDir "C:\Ponto_Online_Pro"
[Setup]
AppId={{C0A4D2E8-5A65-4A5E-9B50-PTONLINE120}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={#MyAppDir}
DefaultGroupName={#MyAppName}
OutputBaseFilename=Ponto_Online_Pro_Instalador_V1_2
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
[Files]
Source: "..\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion; Excludes: "venv\*;instance\*"
[Icons]
Name: "{userdesktop}\Ponto Online Pro"; Filename: "{sys}\wscript.exe"; Parameters: "\"{app}\desktop\start_hidden.vbs\""; IconFilename: "{app}\desktop\ponto.ico"
Name: "{group}\Ponto Online Pro"; Filename: "{sys}\wscript.exe"; Parameters: "\"{app}\desktop\start_hidden.vbs\""; IconFilename: "{app}\desktop\ponto.ico"
[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File \"{app}\installer\instalar_windows.ps1\""; Flags: runhidden waituntilterminated
