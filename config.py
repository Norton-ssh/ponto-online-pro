import os
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
SECRET_KEY=os.environ.get('SECRET_KEY','troque-esta-chave-em-producao')
_db=os.environ.get('DATABASE_URL')
if _db and _db.startswith('postgres://'): _db=_db.replace('postgres://','postgresql://',1)
SQLALCHEMY_DATABASE_URI=_db or 'sqlite:///'+os.path.join(BASE_DIR,'instance','ponto.db')
SQLALCHEMY_TRACK_MODIFICATIONS=False
MAX_CONTENT_LENGTH=5*1024*1024
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
