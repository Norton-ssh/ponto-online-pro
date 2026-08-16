from pathlib import Path
import socket,datetime,ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'instance'/'certs'; OUT.mkdir(parents=True,exist_ok=True)
def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('192.0.2.1',1)); ip=s.getsockname()[0]; s.close(); return ip
    except Exception:
        try: return socket.gethostbyname(socket.gethostname())
        except Exception: return '127.0.0.1'
ip=local_ip(); key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Ponto Online Pro Local')])
san=[x509.DNSName('localhost'),x509.DNSName('ponto.local'),x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]
try: san.append(x509.IPAddress(ipaddress.ip_address(ip)))
except Exception: pass
cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(minutes=5)).not_valid_after(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=825)).add_extension(x509.SubjectAlternativeName(san),critical=False).add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True).sign(key,hashes.SHA256()))
(OUT/'server.key').write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.TraditionalOpenSSL,serialization.NoEncryption()))
(OUT/'server.crt').write_bytes(cert.public_bytes(serialization.Encoding.PEM)); (OUT/'server_ip.txt').write_text(ip,encoding='utf-8'); print(ip)
