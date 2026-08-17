import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

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
        # Migração automática: as fotos passam a ser armazenadas no PostgreSQL/SQLite.
        # Isso evita que desapareçam quando o Render reinicia ou faz novo deploy.
        try:
            columns={c['name'] for c in inspect(db.engine).get_columns('punch')}
            if 'photo_data' not in columns:
                coltype='BYTEA' if db.engine.dialect.name=='postgresql' else 'BLOB'
                with db.engine.begin() as conn:
                    conn.execute(text(f'ALTER TABLE punch ADD COLUMN photo_data {coltype}'))
        except Exception:
            # Em instalação nova db.create_all já cria a coluna; não interromper o boot.
            pass
        from app.seed import seed
        seed()
    return app
