# Ponto Online Pro V1.5

Versão local + Wi-Fi + online, com instalador Windows e servidor oculto.

## Instalação Windows
Execute `installer\instalar_windows.bat`. Ele solicita administrador, instala Python se necessário, cria o ambiente virtual, instala as dependências, testa o sistema, libera a porta 5000 na rede privada e cria o atalho na Área de Trabalho.

Depois, o atalho `Ponto Online Pro` inicia o servidor sem janela preta. O processo fica em segundo plano e o ícone aparece na bandeja do Windows.

## Se não abrir
Verifique:
- `C:\Ponto_Online_Pro\logs\install_test.log`
- `C:\Ponto_Online_Pro\logs\server.log`
- `C:\Ponto_Online_Pro\logs\launcher.log`

O servidor local é `http://127.0.0.1:5000/login`.
Na rede Wi-Fi use `http://IP-DO-PC:5000/login`.

## Login inicial
Usuário: `admin`
Senha: `admin123`

## Código editável
Todo o Python, HTML, CSS, JS, scripts e configuração ficam na pasta `C:\Ponto_Online_Pro`.
