from flask import Flask
from app.config import Config
from app.models import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
# from app.routes import register_blueprints
# from app.extension import mail
from flask_cors import CORS

# from app.apis.user import user_bp
# from app.apis.patient import patient_bp

from app.routes import user_bp, patient_bp, mail

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

app = create_app()
