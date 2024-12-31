from flask import Blueprint, request, jsonify, current_app
from app.models import db, User, Patient
from app.utils import hash_password, check_password
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import timedelta

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

# 醫護人員取得所有病患的資料
@patient_bp.route('/', methods=['GET'])
@jwt_required()
def get_patients():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if not user or not user.is_active:
        return jsonify({"message": "Invalid user."}), 404

    # patients_objs = Patient.query.filter_by(user_id=user_id).all()
    patients_objs = Patient.query.all()
    return jsonify({
        "message": "",
        "patients": [p.to_dict() for p in patients_objs]
    }), 200

# 病患取得自己的資料
@patient_bp.route('/get', methods=['GET'])
@jwt_required()
def get_data():
    patient_id = get_jwt_identity()
    patient = Patient.query.filter_by(id=patient_id).first()
    if not patient:
        return jsonify({"message": "Error."}), 404

    return jsonify({
        "message": "",
        "patient": patient.to_dict()
    }), 200

@patient_bp.route('/', methods=['POST'])
@jwt_required()
def add_patient():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_active:
        return jsonify({"message": "Only verified users can add patients."}), 403

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"message": "Patient name and email are required."}), 400

    existing_patient = Patient.query.filter_by(email=email).first()
    if existing_patient:
        return jsonify({"message": "A patient with this email already exists."}), 400

    hashed_password = hash_password(current_app.config['TEMP_PASSWORD'])

    new_patient = Patient(
        name=name,
        email=email,
        password=hashed_password,
        user_id=user.id,
        video_progression_data={},
        document_progression_data={},
        survey_data={},
    )
    try:
        db.session.add(new_patient)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Create Patient Error"}), 400

    return jsonify({
        "message": "Patient added successfully.",
        "patient": {
            "id": new_patient.id,
            "name": new_patient.name,
            "email": new_patient.email
        }
    }), 201

@patient_bp.route('/signin', methods=['POST'])
def patient_signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400
    
    patient = Patient.query.filter_by(email=email).first()
    if not patient:
        return jsonify({"message": "User not found"}), 404
    
    actual_pass = check_password(password, patient.password)
    if not actual_pass:
        return jsonify({"message": "Incorrect password"}), 401

    if not patient:
        return jsonify({"message": "User not found"}), 404
    
    access_token = create_access_token(
        identity=str(patient.id),
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": "P",
    }), 200

@patient_bp.route('/update_data', methods=['PATCH', 'OPTIONS'])
@jwt_required()
def update_patient_data():
    try:
        patient_id = get_jwt_identity()
        if not patient_id:
            return jsonify({"message": "Missing patient_id"}), 400
        
        data = request.get_json()
        survey_data = data.get('survey_data')
        video_progression_data = data.get('video_progression_data')
        document_progression_data = data.get('document_progression_data')

        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            return jsonify({"message": "Patient Not Found"}), 404

        if survey_data:
            patient.survey_data = survey_data
        elif video_progression_data:
            patient.video_progression_data = video_progression_data
        elif document_progression_data:
            patient.document_progression_data = document_progression_data
        else:
            return jsonify({"message": "Data Error"}), 404

        db.session.commit()
        return jsonify({
            "message": "Patient data updated successfully",
            "patient": {
                "id": patient.id,
                "name": patient.name,
                "survey_data": patient.survey_data,
                "video_progression_data": patient.video_progression_data,
                "document_progression_data": patient.document_progression_data,
                "updated_at": patient.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 200
    except Exception as e:
        return jsonify({"message": "Patient Error: " + str(e)}), 500