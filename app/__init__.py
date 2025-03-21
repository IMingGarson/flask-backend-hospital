from flask import Flask
from app.config import Config
from app.models import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes import user_bp, patient_bp, mail
from celery import Celery

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    _ = Migrate(app, db)
    mail.init_app(app)
    _ = JWTManager(app)

    CORS(app, resources={r"/*": {"origins": "*"}})
    app.register_blueprint(user_bp)
    app.register_blueprint(patient_bp)

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('broker_url'),
        backend=app.config.get('result_backend'),
        include=['app.tasks'],
    )
    celery.conf.update(app.config)
    celery.conf.update(broker_connection_retry_on_startup=True)
    
    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)
    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)