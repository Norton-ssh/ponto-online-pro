import os, math, base64, re, csv, io
from datetime import datetime,date,timedelta
from functools import wraps
from flask import Blueprint,render_template,request,redirect,url_for,session,flash,jsonify,current_app,send_from_directory,make_response
from app import db
from app.models import Company,User,Punch,Correction,Holiday,AuditLog
bp=Blueprint('main',__name__)

def current_user(): return User.query.get(session.get('user_id')) if session.get('user_id') else None

def login_required(role=None):
 def deco(fn):
  @wraps(fn)
  def wrapper(*a,**kw):
   u=current_user()
   if not u or not u.active: return redirect(url_for('main.login'))
   if role and u.role!=role: return redirect(url_for('main.home'))
   return fn(*a,**kw)
  return wrapper
 return deco

def audit(action,details=''):
 u=current_user(); db.session.add(AuditLog(company_id=u.company_id if u else None,user_id=u.id if u else None,action=action,details=details,ip=request.remote_addr)); db.session.commit()

def haversine(a,b,c,d):
 if None in (a,b,c,d): return None
 r=6371000; p1,p2=math.radians(a),math.radians(c); dp=math.radians(c-a); dl=math.radians(d-b)
 x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
 return 2*r*math.asin(math.sqrt(x))

def work_minutes(punches):
 ps=sorted(punches,key=lambda p:p.timestamp); total=0
 for i in range(0,len(ps)-1,2): total+=max(0,int((ps[i+1].timestamp-ps[i].timestamp).total_seconds()/60))
 return total

def fmt_minutes(m): return f'{m//60:02d}:{m%60:02d}'

@bp.context_processor
def inject():
    ip='127.0.0.1'
    try:
        fp=os.path.join(current_app.instance_path,'certs','server_ip.txt')
        if os.path.exists(fp): ip=open(fp,encoding='utf-8').read().strip() or ip
    except Exception: pass
    return {'me':current_user(),'fmt_minutes':fmt_minutes,'lan_ip':ip,'employee_login_url':f'https://{ip}:5000/login'}

@bp.route('/')
def home():
 u=current_user(); return redirect(url_for('main.login')) if not u else redirect(url_for('main.admin_dashboard' if u.role=='admin' else 'main.employee'))

@bp.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=User.query.filter_by(username=request.form.get('username','').strip()).first()
  if u and u.active and u.check_password(request.form.get('password','')):
   session.clear(); session['user_id']=u.id; return redirect(url_for('main.home'))
  flash('Login ou senha inválidos.','danger')
 return render_template('login.html',prefill=request.args.get('usuario',''))
@bp.route('/logout')
def logout(): session.clear(); return redirect(url_for('main.login'))

@bp.route('/admin')
@login_required('admin')
def admin_dashboard():
 c=current_user().company; emps=User.query.filter_by(company_id=c.id,role='employee').order_by(User.name).all(); ps=Punch.query.filter_by(company_id=c.id).order_by(Punch.timestamp.desc()).limit(30).all()
 today=[p for p in ps if p.timestamp.date()==date.today()]
 return render_template('admin.html',company=c,employees=emps,punches=ps,today_count=len(today),pending=Correction.query.filter_by(company_id=c.id,status='PENDENTE').count())

@bp.route('/admin/company',methods=['GET','POST'])
@login_required('admin')
def company_edit():
 c=current_user().company
 if request.method=='POST':
  for f in ['name','cnpj','address','work_start','break_start','break_end','work_end']:
   setattr(c,f,request.form.get(f,'').strip())
  c.lat=float(request.form['lat']) if request.form.get('lat') else None; c.lng=float(request.form['lng']) if request.form.get('lng') else None
  c.radius_m=max(1,int(request.form.get('radius_m') or 200)); c.tolerance_min=max(0,int(request.form.get('tolerance_min') or 0)); c.weekly_hours=float(request.form.get('weekly_hours') or 44)
  db.session.commit(); audit('ALTEROU_CONFIG_EMPRESA',c.name); flash('Configurações salvas.','success'); return redirect(url_for('main.company_edit'))
 return render_template('company.html',company=c)

@bp.route('/admin/employees',methods=['GET','POST'])
@login_required('admin')
def employees():
 c=current_user().company
 if request.method=='POST':
  if User.query.filter_by(username=request.form.get('username','').strip()).first(): flash('Login já existe.','danger'); return redirect(url_for('main.employees'))
  u=User(company_id=c.id,name=request.form.get('name','').strip(),cpf=request.form.get('cpf','').strip(),matricula=request.form.get('matricula','').strip(),cargo=request.form.get('cargo','').strip(),department=request.form.get('department','').strip(),username=request.form.get('username','').strip(),role='employee',active=True); u.set_password(request.form.get('password') or '123456'); db.session.add(u); db.session.commit(); audit('CADASTROU_FUNCIONARIO',u.name); flash('Funcionário cadastrado.','success'); return redirect(url_for('main.employees'))
 return render_template('employees.html',employees=User.query.filter_by(company_id=c.id,role='employee').order_by(User.name).all())

@bp.route('/admin/employee/<int:id>/edit',methods=['GET','POST'])
@login_required('admin')
def employee_edit(id):
 u=User.query.filter_by(id=id,company_id=current_user().company.id,role='employee').first_or_404()
 if request.method=='POST':
  for f in ['name','cpf','matricula','cargo','department']: setattr(u,f,request.form.get(f,'').strip())
  if request.form.get('password'): u.set_password(request.form['password'])
  db.session.commit(); audit('EDITOU_FUNCIONARIO',u.name); flash('Funcionário atualizado.','success'); return redirect(url_for('main.employees'))
 return render_template('employee_edit.html',employee=u)
@bp.route('/admin/employee/<int:id>/toggle',methods=['POST'])
@login_required('admin')
def employee_toggle(id):
 u=User.query.filter_by(id=id,company_id=current_user().company.id,role='employee').first_or_404(); u.active=not u.active; db.session.commit(); audit('ALTEROU_STATUS_FUNCIONARIO',u.name); return redirect(url_for('main.employees'))

@bp.route('/admin/punches')
@login_required('admin')
def admin_punches():
 c=current_user().company; q=Punch.query.filter_by(company_id=c.id); emp=request.args.get('employee'); start=request.args.get('start'); end=request.args.get('end')
 if emp: q=q.filter_by(employee_id=int(emp))
 if start: q=q.filter(Punch.timestamp>=datetime.strptime(start,'%Y-%m-%d'))
 if end: q=q.filter(Punch.timestamp<datetime.strptime(end,'%Y-%m-%d')+timedelta(days=1))
 ps=q.order_by(Punch.timestamp.desc()).all(); return render_template('punches.html',punches=ps,employees=User.query.filter_by(company_id=c.id,role='employee').all(),filters={'employee':emp,'start':start,'end':end})

@bp.route('/admin/punches.csv')
@login_required('admin')
def punches_csv():
 c=current_user().company; q=Punch.query.filter_by(company_id=c.id).order_by(Punch.timestamp); out=io.StringIO(); w=csv.writer(out,delimiter=';'); w.writerow(['ID','Funcionário','CPF','Data','Hora','Tipo','Distância(m)','Latitude','Longitude','Editado'])
 for p in q.all(): w.writerow([p.id,p.employee.name,p.employee.cpf,p.timestamp.strftime('%d/%m/%Y'),p.timestamp.strftime('%H:%M:%S'),p.kind,f'{p.distance_m:.1f}' if p.distance_m else '',p.latitude or '',p.longitude or '', 'SIM' if p.edited else 'NÃO'])
 r=make_response('\ufeff'+out.getvalue()); r.headers['Content-Disposition']='attachment; filename=relatorio_pontos.csv'; r.headers['Content-Type']='text/csv; charset=utf-8'; return r

@bp.route('/photo/<int:id>')
@login_required('admin')
def photo(id):
 p=Punch.query.filter_by(id=id,company_id=current_user().company.id).first_or_404(); return send_from_directory(current_app.config['UPLOAD_FOLDER'],os.path.basename(p.photo_path)) if p.photo_path else ('',404)

@bp.route('/admin/corrections')
@login_required('admin')
def corrections():
 c=current_user().company; return render_template('corrections.html',items=Correction.query.filter_by(company_id=c.id).order_by(Correction.requested_at.desc()).all())
@bp.route('/admin/correction/<int:id>/<action>',methods=['POST'])
@login_required('admin')
def review_correction(id,action):
 x=Correction.query.filter_by(id=id,company_id=current_user().company.id).first_or_404()
 if x.status!='PENDENTE': return redirect(url_for('main.corrections'))
 if action=='approve':
  if x.punch_id:
   p=Punch.query.get(x.punch_id); p.timestamp=x.requested_time; p.edited=True; p.correction_note=x.reason
  x.status='APROVADA'
 else: x.status='REPROVADA'
 x.reviewed_at=datetime.now(); x.reviewed_by=current_user().id; x.review_note=request.form.get('review_note',''); db.session.commit(); audit('ANALISOU_CORRECAO',f'{x.id}:{x.status}'); return redirect(url_for('main.corrections'))

@bp.route('/admin/holidays',methods=['GET','POST'])
@login_required('admin')
def holidays():
 c=current_user().company
 if request.method=='POST': db.session.add(Holiday(company_id=c.id,day=datetime.strptime(request.form['day'],'%Y-%m-%d').date(),name=request.form['name'].strip())); db.session.commit(); return redirect(url_for('main.holidays'))
 return render_template('holidays.html',items=Holiday.query.filter_by(company_id=c.id).order_by(Holiday.day).all())

@bp.route('/admin/audit')
@login_required('admin')
def audit_page(): return render_template('audit.html',items=AuditLog.query.filter_by(company_id=current_user().company.id).order_by(AuditLog.created_at.desc()).limit(300).all())

@bp.route('/admin/report')
@login_required('admin')
def report():
 c=current_user().company; start=request.args.get('start') or date.today().replace(day=1).isoformat(); end=request.args.get('end') or date.today().isoformat(); a=datetime.strptime(start,'%Y-%m-%d'); b=datetime.strptime(end,'%Y-%m-%d')+timedelta(days=1)
 rows=[]
 for u in User.query.filter_by(company_id=c.id,role='employee').order_by(User.name):
  ps=Punch.query.filter(Punch.employee_id==u.id,Punch.timestamp>=a,Punch.timestamp<b).order_by(Punch.timestamp).all(); rows.append((u,ps,work_minutes(ps)))
 return render_template('report.html',rows=rows,start=start,end=end)

@bp.route('/employee')
@login_required('employee')
def employee():
 u=current_user(); start=request.args.get('start') or date.today().replace(day=1).isoformat(); end=request.args.get('end') or date.today().isoformat(); q=Punch.query.filter(Punch.employee_id==u.id,Punch.timestamp>=datetime.strptime(start,'%Y-%m-%d'),Punch.timestamp<datetime.strptime(end,'%Y-%m-%d')+timedelta(days=1)); ps=q.order_by(Punch.timestamp.desc()).all(); return render_template('employee.html',punches=ps,filters={'start':start,'end':end})

@bp.route('/employee/correction',methods=['POST'])
@login_required('employee')
def correction_request():
 u=current_user(); p=Punch.query.filter_by(id=int(request.form['punch_id']),employee_id=u.id).first_or_404(); requested=datetime.strptime(request.form['requested_time'],'%Y-%m-%dT%H:%M'); reason=request.form.get('reason','').strip()
 if not reason: flash('Informe a justificativa.','danger'); return redirect(url_for('main.employee'))
 db.session.add(Correction(company_id=u.company_id,employee_id=u.id,punch_id=p.id,requested_time=requested,reason=reason)); db.session.commit(); flash('Solicitação enviada para aprovação.','success'); return redirect(url_for('main.employee'))

@bp.route('/api/punch',methods=['POST'])
@login_required('employee')
def punch_api():
 u=current_user(); c=u.company; data=request.get_json(silent=True) or {}; lat=data.get('latitude'); lng=data.get('longitude'); accuracy=data.get('accuracy')
 try: lat=float(lat); lng=float(lng)
 except: return jsonify(ok=False,message='A localização é obrigatória.'),400
 distance=haversine(c.lat,c.lng,lat,lng) if c.lat is not None and c.lng is not None else None
 if c.lat is None or c.lng is None: return jsonify(ok=False,message='A empresa ainda não configurou a localização.'),400
 if distance>c.radius_m: return jsonify(ok=False,message=f'Fora da área permitida: {distance:.0f} m. Limite: {c.radius_m} m.'),403
 photo=data.get('photo',''); path=None
 if photo.startswith('data:image/'):
  m=re.match(r'data:image/(png|jpeg|jpg);base64,(.*)',photo)
  if m:
   ext='jpg' if m.group(1) in ('jpeg','jpg') else 'png'; name=f'punch_{u.id}_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.{ext}'
   with open(os.path.join(current_app.config['UPLOAD_FOLDER'],name),'wb') as f: f.write(base64.b64decode(m.group(2)))
   path=name
 if not path: return jsonify(ok=False,message='A foto da batida é obrigatória.'),400
 last=Punch.query.filter_by(employee_id=u.id).order_by(Punch.timestamp.desc()).first(); kinds=['ENTRADA','INTERVALO - SAÍDA','INTERVALO - RETORNO','SAÍDA']; kind=kinds[0] if not last or last.kind=='SAÍDA' else kinds[kinds.index(last.kind)+1]
 p=Punch(company_id=c.id,employee_id=u.id,kind=kind,photo_path=path,latitude=lat,longitude=lng,distance_m=distance,ip=request.headers.get('X-Forwarded-For',request.remote_addr),user_agent=request.user_agent.string[:255]); db.session.add(p); db.session.commit(); audit('BATEU_PONTO',f'{p.id}:{p.kind}')
 return jsonify(ok=True,punch={'id':p.id,'name':u.name,'cpf':u.cpf,'matricula':u.matricula,'cargo':u.cargo,'date':p.timestamp.strftime('%d/%m/%Y'),'time':p.timestamp.strftime('%H:%M:%S'),'kind':p.kind,'distance':f'{distance:.0f} m','latitude':lat,'longitude':lng,'accuracy':accuracy})
