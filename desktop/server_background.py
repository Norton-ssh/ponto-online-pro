import os, sys, time, subprocess, threading, webbrowser, socket, traceback, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'server.log'
PYTHON = Path(sys.executable)
RUNNER = ROOT / 'desktop' / 'server_service.py'

CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)


def log(msg):
    with LOG_FILE.open('a', encoding='utf-8') as f:
        f.write(time.strftime('[%Y-%m-%d %H:%M:%S] ') + str(msg) + '\n')


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.0.2.1', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def open_local():
    webbrowser.open('https://127.0.0.1:5000/login')


def open_wifi():
    webbrowser.open(f'https://{get_local_ip()}:5000/login')


def wait_http(seconds=20):
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen('https://127.0.0.1:5000/login', context=__import__('ssl')._create_unverified_context(), timeout=1.5) as r:
                return 200 <= r.status < 500
        except Exception:
            time.sleep(0.5)
    return False


def start_server():
    if not RUNNER.exists():
        log(f'ERRO: run_local.py não encontrado: {RUNNER}')
        return None
    try:
        log(f'Iniciando servidor com: {PYTHON} {RUNNER}')
        out = LOG_DIR / 'flask.log'
        fh = out.open('a', encoding='utf-8')
        proc = subprocess.Popen(
            [str(PYTHON), str(RUNNER)],
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            stdout=fh,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW,
            close_fds=True,
        )
        log(f'Processo do servidor criado. PID={proc.pid}')
        return proc, fh
    except Exception:
        log('ERRO AO CRIAR PROCESSO DO SERVIDOR:')
        log(traceback.format_exc())
        return None


def run_tray():
    try:
        import pystray
        from PIL import Image, ImageDraw
        ico = ROOT / 'desktop' / 'ponto.ico'
        try:
            image = Image.open(ico)
        except Exception:
            image = Image.new('RGB', (64, 64), 'white')
            d = ImageDraw.Draw(image)
            d.rectangle((8, 8, 56, 56), outline='black', width=5)
            d.text((20, 20), 'P', fill='black')

        def quit_app(icon, item):
            log('Servidor encerrado pelo menu da bandeja')
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem('Abrir Ponto', lambda i, x: open_local()),
            pystray.MenuItem('Abrir na rede Wi-Fi', lambda i, x: open_wifi()),
            pystray.MenuItem('Abrir pasta do sistema', lambda i, x: os.startfile(str(ROOT))),
            pystray.MenuItem('Encerrar servidor', quit_app),
        )
        icon = pystray.Icon('PontoOnline', image, 'Ponto Online Pro', menu)
        icon.run()
    except Exception:
        log('Aviso: ícone da bandeja não iniciou:')
        log(traceback.format_exc())


def main():
    try:
        log('--- INÍCIO DO LANÇADOR V2.0 ---')
        result = start_server()
        if not result:
            return
        proc, fh = result
        threading.Thread(target=run_tray, daemon=True).start()
        if wait_http(20):
            log('Servidor respondeu em http://127.0.0.1:5000/login')
            open_local()
        else:
            log('ERRO: servidor não respondeu em 20 segundos.')
            if proc.poll() is not None:
                log(f'Processo terminou imediatamente. Código={proc.returncode}')
            else:
                log(f'Processo ainda ativo. PID={proc.pid}')
        while proc.poll() is None:
            time.sleep(2)
        log(f'Processo do servidor encerrou. Código={proc.returncode}')
        fh.close()
    except Exception:
        log('ERRO NO LANÇADOR:')
        log(traceback.format_exc())


if __name__ == '__main__':
    main()
