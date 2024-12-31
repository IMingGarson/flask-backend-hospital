from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.dialects.mysql import FLOAT

# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            "deleted_at": self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    invide_code = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.String(255), nullable=False)
    survey_data = db.Column(db.JSON, nullable=True)
    video_progression_data = db.Column(db.JSON, nullable=True)
    document_progression_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "birthday": self.birthday,
            "survey_data": self.survey_data,
            "video_progression_data": self.video_progression_data,
            "document_progression_data": self.document_progression_data,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            "deleted_at": self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }


class PSA(db.Model):
    __tablename__ = 'patient_psa_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(255), nullable=False)
    psa = db.Column(FLOAT(unsigned=True), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "date": self.date,
            "psa": self.psa,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            "deleted_at": self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }