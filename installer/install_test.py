import os, sys, traceback
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
try:
    from app import create_app
    app = create_app()
    with app.test_client() as client:
        r = client.get('/login')
        assert r.status_code == 200, f'/login retornou HTTP {r.status_code}'
    db_path = os.path.join(ROOT, 'instance', 'ponto.db')
    assert os.path.exists(db_path), f'Banco não foi criado: {db_path}'
    print('OK - aplicação, banco SQLite e rota /login funcionando')
except Exception:
    traceback.print_exc()
    sys.exit(1)
