from app import db
from app.models import Company,User

def seed():
    if User.query.filter_by(username='admin').first(): return
    c=Company(name='Empresa Demonstração',cnpj='',address='',lat=None,lng=None,radius_m=200,tolerance_min=10)
    db.session.add(c); db.session.flush()
    u=User(company_id=c.id,name='Administrador',username='admin',role='admin',active=True); u.set_password('admin123')
    db.session.add(u); db.session.commit()
