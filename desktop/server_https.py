import os, sys, socket, logging, webbrowser, time
from pathlib import Path
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=str(LOG_DIR / "server.log"), level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

HOST = "0.0.0.0"
PORT = 5000

def get_lan_ip():
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.0.2.1", 1))
        ip=s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

def main():
    cert = ROOT / "instance" / "certs" / "server.crt"
    key = ROOT / "instance" / "certs" / "server.key"
    if not cert.exists() or not key.exists():
        raise RuntimeError("Certificado HTTPS não encontrado. Execute o instalador novamente.")
    from app import create_app
    app=create_app()
    ip=get_lan_ip()
    (ROOT/"instance"/"certs"/"server_ip.txt").write_text(ip,encoding="utf-8")
    logging.info("Iniciando servidor HTTPS direto em %s:%s", HOST, PORT)
    logging.info("IP da rede local: %s", ip)
    server=make_server(HOST, PORT, app, threaded=True, ssl_context=(str(cert), str(key)))
    logging.info("SERVIDOR LOCAL ATIVO: https://127.0.0.1:%s/login", PORT)
    logging.info("SERVIDOR WIFI ATIVO: https://%s:%s/login", ip, PORT)
    if os.environ.get("PONTO_OPEN_BROWSER","1")=="1":
        try: webbrowser.open(f"https://127.0.0.1:{PORT}/login")
        except Exception: pass
    server.serve_forever()

if __name__=="__main__":
    try: main()
    except Exception:
        logging.exception("ERRO FATAL NO SERVIDOR")
        raise
