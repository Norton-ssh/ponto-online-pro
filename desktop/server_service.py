import os,sys,logging,threading,ssl,socket,http.client
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]; os.chdir(ROOT); sys.path.insert(0,str(ROOT)); LOG_DIR=ROOT/'logs'; LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=str(LOG_DIR/'flask.log'),level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
BACKEND_HOST='127.0.0.1'; BACKEND_PORT=5001; HTTPS_HOST='0.0.0.0'; HTTPS_PORT=5000
class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def _forward(self):
        try:
            length=int(self.headers.get('Content-Length','0') or 0); body=self.rfile.read(length) if length else None
            headers={k:v for k,v in self.headers.items() if k.lower() not in ('host','connection','content-length','transfer-encoding')}
            headers['Host']=self.headers.get('Host','127.0.0.1:5000');
            if body is not None: headers['Content-Length']=str(len(body))
            conn=http.client.HTTPConnection(BACKEND_HOST,BACKEND_PORT,timeout=30); conn.request(self.command,self.path,body=body,headers=headers); resp=conn.getresponse(); data=resp.read()
            self.send_response(resp.status,resp.reason)
            for k,v in resp.getheaders():
                if k.lower() in ('connection','transfer-encoding','content-length','keep-alive','server','date'): continue
                self.send_header(k,v)
            self.send_header('Content-Length',str(len(data))); self.send_header('Connection','close'); self.end_headers()
            if self.command!='HEAD': self.wfile.write(data)
            conn.close()
        except Exception as e:
            logging.exception('Proxy error: %s',e)
            try:
                self.send_response(502); self.send_header('Content-Type','text/plain; charset=utf-8'); self.send_header('Connection','close'); self.end_headers(); self.wfile.write(b'Ponto Online Pro: servidor temporariamente indisponivel.')
            except Exception: pass
    def do_GET(self): self._forward()
    def do_POST(self): self._forward()
    def do_HEAD(self): self._forward()
    def log_message(self,fmt,*args): logging.info('HTTPS %s - %s',self.address_string(),fmt%args)
def start_backend():
    from app import create_app
    from waitress import serve
    app=create_app(); logging.info('Backend Waitress em 127.0.0.1:5001'); serve(app,host=BACKEND_HOST,port=BACKEND_PORT,threads=8,url_scheme='http')
def main():
    cert=ROOT/'instance'/'certs'/'server.crt'; key=ROOT/'instance'/'certs'/'server.key'
    if not cert.exists() or not key.exists(): raise RuntimeError('Certificado local não encontrado. Execute o instalador novamente.')
    t=threading.Thread(target=start_backend,daemon=True); t.start()
    import time
    for _ in range(50):
        try:
            s=socket.create_connection((BACKEND_HOST,BACKEND_PORT),timeout=0.3); s.close(); break
        except Exception: time.sleep(.1)
    server=ThreadingHTTPServer((HTTPS_HOST,HTTPS_PORT),ProxyHandler)
    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(str(cert),str(key)); server.socket=ctx.wrap_socket(server.socket,server_side=True)
    logging.info('HTTPS local em https://0.0.0.0:5000'); server.serve_forever()
if __name__=='__main__':
    try: main()
    except Exception: logging.exception('ERRO FATAL NO SERVIDOR'); raise
