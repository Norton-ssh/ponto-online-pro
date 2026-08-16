import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

def create_app():
    app=Flask(__name__,instance_relative_config=True)
    os.makedirs(app.instance_path,exist_ok=True)
    os.makedirs(os.path.join(app.instance_path,'uploads'),exist_ok=True)
    app.config.from_object('config')
    app.config['UPLOAD_FOLDER']=os.path.join(app.instance_path,'uploads')
    db.init_app(app)
    from app.routes import bp
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
        from app.seed import seed
        seed()
    return app
