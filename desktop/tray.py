import os, sys, time, threading, webbrowser, socket
from pathlib import Path

def app_root(): return Path(__file__).resolve().parents[1]
os.chdir(app_root())
from app import create_app
app=create_app()

def run_server(): app.run(host='0.0.0.0',port=5000,debug=False,use_reloader=False)

def local_ip():
 try:
  s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); ip=s.getsockname()[0]; s.close(); return ip
 except Exception: return '127.0.0.1'

def open_app(icon=None,item=None): webbrowser.open('http://127.0.0.1:5000/login')
def open_wifi(icon=None,item=None): webbrowser.open(f'http://{local_ip()}:5000/login')
def quit_app(icon,item): icon.stop(); os._exit(0)

def main():
 import pystray
 from PIL import Image,ImageDraw
 ico=app_root()/'desktop'/'ponto.ico'
 try: image=Image.open(ico)
 except: 
  image=Image.new('RGB',(64,64),'white'); d=ImageDraw.Draw(image); d.rectangle((8,8,56,56),outline='black',width=5); d.text((18,20),'P',fill='black')
 menu=pystray.Menu(pystray.MenuItem('Abrir Ponto',open_app),pystray.MenuItem('Abrir na rede Wi-Fi',open_wifi),pystray.MenuItem('Encerrar servidor',quit_app))
 icon=pystray.Icon('PontoOnline',image,'Ponto Online Pro',menu); threading.Thread(target=run_server,daemon=True).start(); time.sleep(2); webbrowser.open('http://127.0.0.1:5000/login'); icon.run()
if __name__=='__main__': main()
