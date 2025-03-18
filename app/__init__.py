import time
from flask import Flask
from app.config import Config
from app.models import db, Patient
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes import user_bp, patient_bp, mail
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import send_push_notification

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

    scheduler = BackgroundScheduler()
    scheduler.start()

    def send_periodical_push_notification():
        with app.app_context():
            patients = Patient.query.all()
            # print("人數 {} 位".format(len(patients)))
            for patient in patients:
                if patient.push_token and patient.push_token.startswith("ExponentPushToken"):
                    _, _ = send_push_notification(patient.push_token, "你好", "新的開始，祝您有個愉快的一週！")
                    time.sleep(0.5)

    scheduler.add_job(send_periodical_push_notification, trigger='cron', day_of_week='mon')
    # scheduler.add_job(send_periodical_push_notification, trigger='interval', seconds=20)

    return app

app = create_app()