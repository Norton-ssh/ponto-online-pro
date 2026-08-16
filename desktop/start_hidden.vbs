Option Explicit
Dim sh, fso, root, pyw, script, logFile, f
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
pyw = root & "\venv\Scripts\pythonw.exe"
script = root & "\desktop\server_https.py"
logFile = root & "\logs\launcher.log"
If Not fso.FileExists(pyw) Then
  Set f = fso.OpenTextFile(logFile, 8, True)
  f.WriteLine Now & " ERRO: pythonw.exe não encontrado: " & pyw
  f.Close
  WScript.Quit 1
End If
If Not fso.FileExists(script) Then
  Set f = fso.OpenTextFile(logFile, 8, True)
  f.WriteLine Now & " ERRO: server_https.py não encontrado: " & script
  f.Close
  WScript.Quit 1
End If
On Error Resume Next
sh.CurrentDirectory = root
sh.Run Chr(34) & pyw & Chr(34) & " " & Chr(34) & script & Chr(34), 0, False
If Err.Number <> 0 Then
  Set f = fso.OpenTextFile(logFile, 8, True)
  f.WriteLine Now & " ERRO AO INICIAR: " & Err.Description
  f.Close
Else
  Set f = fso.OpenTextFile(logFile, 8, True)
  f.WriteLine Now & " Lançador iniciado: server_https.py"
  f.Close
End If
