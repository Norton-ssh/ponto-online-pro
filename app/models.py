from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Company(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(160),nullable=False)
    cnpj=db.Column(db.String(30)); address=db.Column(db.String(255))
    lat=db.Column(db.Float); lng=db.Column(db.Float)
    radius_m=db.Column(db.Integer,default=200); tolerance_min=db.Column(db.Integer,default=10)
    work_start=db.Column(db.String(5),default='08:00'); break_start=db.Column(db.String(5),default='12:00')
    break_end=db.Column(db.String(5),default='13:00'); work_end=db.Column(db.String(5),default='17:30')
    weekly_hours=db.Column(db.Float,default=44); active=db.Column(db.Boolean,default=True)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True); company_id=db.Column(db.Integer,db.ForeignKey('company.id'),nullable=True)
    name=db.Column(db.String(160),nullable=False); cpf=db.Column(db.String(30)); matricula=db.Column(db.String(50)); cargo=db.Column(db.String(120)); department=db.Column(db.String(120))
    username=db.Column(db.String(80),unique=True,nullable=False); password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(30),default='employee'); active=db.Column(db.Boolean,default=True)
    company=db.relationship('Company',backref='users')
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)

class Punch(db.Model):
    id=db.Column(db.Integer,primary_key=True); company_id=db.Column(db.Integer,db.ForeignKey('company.id'),nullable=False); employee_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.now,nullable=False); kind=db.Column(db.String(40),nullable=False); photo_path=db.Column(db.String(255))
    latitude=db.Column(db.Float); longitude=db.Column(db.Float); distance_m=db.Column(db.Float); ip=db.Column(db.String(80)); user_agent=db.Column(db.String(255))
    edited=db.Column(db.Boolean,default=False); correction_note=db.Column(db.String(500)); employee=db.relationship('User'); company=db.relationship('Company')

class Correction(db.Model):
    id=db.Column(db.Integer,primary_key=True); company_id=db.Column(db.Integer,db.ForeignKey('company.id'),nullable=False); employee_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    punch_id=db.Column(db.Integer,db.ForeignKey('punch.id')); requested_at=db.Column(db.DateTime,default=datetime.now); requested_time=db.Column(db.DateTime,nullable=False)
    reason=db.Column(db.String(500),nullable=False); status=db.Column(db.String(20),default='PENDENTE'); reviewed_at=db.Column(db.DateTime); reviewed_by=db.Column(db.Integer); review_note=db.Column(db.String(500))
    employee=db.relationship('User'); punch=db.relationship('Punch')

class Holiday(db.Model):
    id=db.Column(db.Integer,primary_key=True); company_id=db.Column(db.Integer,db.ForeignKey('company.id'),nullable=False); day=db.Column(db.Date,nullable=False); name=db.Column(db.String(160),nullable=False)

class AuditLog(db.Model):
    id=db.Column(db.Integer,primary_key=True); company_id=db.Column(db.Integer,db.ForeignKey('company.id')); user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    action=db.Column(db.String(120),nullable=False); details=db.Column(db.String(1000)); created_at=db.Column(db.DateTime,default=datetime.now); ip=db.Column(db.String(80))
