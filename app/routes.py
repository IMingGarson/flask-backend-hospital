from flask import Blueprint, request, jsonify, url_for, current_app, render_template
from app.models import db, User, Patient, PSA
from app.utils import validate_date, validate, hash_password, check_password, generate_confirmation_token, confirm_token, validate_email
from flask_mail import Message, Mail
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import timedelta
from flask_cors import cross_origin

mail = Mail()
user_bp = Blueprint('user', __name__, url_prefix='/api/user')
patient_bp = Blueprint('patient', __name__)

@user_bp.route('/test', methods=['GET'])
def test_route():
    user = User.query.all()
    return jsonify({
        "message": "",
        "patients": [u.to_dict() for u in user]
    }), 200

@user_bp.route('/send_verify_email', methods=['GET'])
def send_verify_email():
    id = request.args.get('id')
    if int(id) == 0:
        return render_template('email_verify_failure.html', user_id=0)
    
    user = User.query.filter_by(id=id).first()
    if not user:
        return render_template('email_verify_failure.html', user_id=0)
    
    name = user.name
    email = user.email
    token = generate_confirmation_token(email)
    confirm_url = url_for('user.verify_user_email', token=token, _external=True)
    msg = Message('Please confirm your email', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
    html = f"""
            <!DOCTYPE html>
            <html>
            <body bgcolor="#ffffff" style="font-family: Arial, sans-serif; background-color: #fffaf0; margin: 0; padding: 0; color: #4a4a4a;">
                <table align="center" style="background-color: #ffffff; border-collapse: collapse; border: 1px solid #ddd; border-radius: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); margin: 20px auto; padding: 20px;">
                    <tr>
                        <td align="center" style="background-color: #ff8c42; border-radius: 10px 10px 0 0; color: #ffffff; padding: 10px;">
                            <h1 style="margin: 0; font-size: 24px;">驗證您的 Email</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px; line-height: 1.6; font-size: 16px; color: #4a4a4a;">
                            <p>您好 {name}，</p>
                            <p>
                                您可以點擊下方按鈕驗證您的 Email 並完成註冊，請注意，此連結將在<strong>10分鐘內</strong>過期。
                            </p>
                            <p style="text-align: center;">
                                <a href="{confirm_url}" class="verify-button" style="display: inline-block; padding: 10px 20px; color: #ffffff; background-color: #ff8c42; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">驗證我的 Email</a>
                            </p>
                            <p>
                                如果按鈕沒有正確引導您到驗證頁面，請直接複製下方網址到瀏覽器內驗證：
                            </p>
                            <p style="word-wrap: break-word;">
                                <a href="{confirm_url}" style="color: #ff8c42; text-decoration: none;">{confirm_url}</a>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="font-size: 12px; color: #999; padding: 20px;">
                            <p>此 Email 是系統自動發送，請勿直接回覆。</p>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
    msg.html = html
    mail.send(msg)

    return render_template('email_verify_resend.html')

@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({"message": "Missing required fields"}), 400
    
    if validate(email) is None:
        return jsonify({"message": "Invalid email"}), 400

    hashed_password = hash_password(password)
    new_user = User(email=email, name=name, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email error"}), 400

    token = generate_confirmation_token(email)
    confirm_url = url_for('user.verify_user_email', token=token, _external=True)

    msg = Message('Please confirm your email', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
    html = f"""
            <!DOCTYPE html>
            <html>
            <body bgcolor="#ffffff" style="font-family: Arial, sans-serif; background-color: #fffaf0; margin: 0; padding: 0; color: #4a4a4a;">
                <table align="center" style="background-color: #ffffff; border-collapse: collapse; border: 1px solid #ddd; border-radius: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); margin: 20px auto; padding: 20px;">
                    <tr>
                        <td align="center" style="background-color: #ff8c42; border-radius: 10px 10px 0 0; color: #ffffff; padding: 10px;">
                            <h1 style="margin: 0; font-size: 24px;">驗證您的 Email</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px; line-height: 1.6; font-size: 16px; color: #4a4a4a;">
                            <p>您好 {name}，</p>
                            <p>
                                您可以點擊下方按鈕驗證您的 Email 並完成註冊，請注意，此連結將在<strong>10分鐘內</strong>過期。
                            </p>
                            <p style="text-align: center;">
                                <a href="{confirm_url}" class="verify-button" style="display: inline-block; padding: 10px 20px; color: #ffffff; background-color: #ff8c42; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">驗證我的 Email</a>
                            </p>
                            <p>
                                如果按鈕沒有正確引導您到驗證頁面，請直接複製下方網址到瀏覽器內驗證：
                            </p>
                            <p style="word-wrap: break-word;">
                                <a href="{confirm_url}" style="color: #ff8c42; text-decoration: none;">{confirm_url}</a>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="font-size: 12px; color: #999; padding: 20px;">
                            <p>此 Email 是系統自動發送，請勿直接回覆。</p>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
    msg.html = html
    mail.send(msg)

    return jsonify({"message": "User registered successfully. Please check your email to verify your account."}), 201

@user_bp.route('/verify', methods=['GET'])
def verify_user_email():
    token = request.args.get('token')
    if not token:
        return render_template('email_verify_failure.html', user_id=0)

    email = confirm_token(token)
    if not email:
        return render_template('email_verify_failure.html', user_id=0)

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template('email_verify_failure.html', user_id=0)

    if user.is_active:
        return render_template('email_verify_success.html')

    try:
        user.is_active = True
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template('email_verify_failure.html', user_id=user.id)

    return render_template('email_verify_success.html')

@user_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.is_active:
        return jsonify({"message": "Account not verified"}), 403

    if not check_password(password, user.password):
        return jsonify({"message": "Incorrect password"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": "M",
    }), 200

# 醫護人員取得所有病患的資料
@patient_bp.route('/api/patient', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_patients():
    if request.method == 'OPTIONS':
        return '', 200
    
    @jwt_required()
    def method():
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user or not user.is_active:
            return jsonify({"message": "Invalid user."}), 404
        
        patients_objs = Patient.query.all()
        return jsonify({
            "message": "",
            "patients": [p.to_dict() for p in patients_objs]
        }), 200
    
    return method()

# 病患取得自己的資料
@patient_bp.route('/api/patient/get', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    @jwt_required()
    def method():
        patient_id = get_jwt_identity()
        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            return jsonify({"message": "Error."}), 404

        return jsonify({
            "message": "",
            "patient": patient.to_dict()
        }), 200
    return method()

# 病患透過邀請碼註冊
@patient_bp.route('/api/patient', methods=['POST', 'OPTIONS'])
@cross_origin()
def add_patient():
    if request.method == 'OPTIONS':
        return '', 200

    def method():
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        birthday = data.get('birthday')
        invide_code = data.get('inviteCode')

        if not name or not email or not birthday or not invide_code or invide_code != '123456':
            return jsonify({"message": "Patient name and email are required."}), 400

        existing_patient = Patient.query.filter_by(email=email).first()
        if existing_patient:
            return jsonify({"message": "A patient with this email already exists."}), 400

        hashed_password = hash_password(current_app.config['TEMP_PASSWORD'])

        new_patient = Patient(
            name=name,
            email=email,
            password=hashed_password,
            birthday=birthday,
            invide_code=invide_code,
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
                "email": new_patient.email,
                "birthday": new_patient.birthday,
                "invide_code": new_patient.invide_code
            }
        }), 201
    return method()

# 病患登入
@patient_bp.route('/api/patient/signin', methods=['POST', 'OPTIONS'])
def patient_signin():
    if request.method == 'OPTIONS':
        return '', 200
    
    def method():
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
    
    return method()

# 病患取得 PSA 資料
@patient_bp.route('/api/patient/psa', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_psa_data():
    if request.method == 'OPTIONS':
        return '', 200

    @jwt_required()
    def method():
        patient_id = get_jwt_identity()
        if not patient_id:
            return jsonify({"message": "Missing patient_id"}), 400
        
        psa_objs = PSA.query.filter_by(patient_id=patient_id).all()
        return jsonify({
            "message": "",
            "psa": [p.to_dict() for p in psa_objs]
        }), 200
    
    return method()

# 醫護人員 or 病患使用日期取得 PSA 資料
@patient_bp.route('/api/patient/psa_on_date', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_pas_data_on_date():
    if request.method == 'OPTIONS':
        return '', 200
    
    @jwt_required()
    def method():
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"message": "Missing ID"}), 400
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        patient_id = request.args.get('pid')
        if not start_date or not end_date or not validate_date(start_date) or not validate_date(end_date):
            return jsonify({"message": "Missing date"}), 400
        
        if patient_id:
            psa = PSA.query.filter(
                and_(
                    PSA.patient_id == patient_id,
                    PSA.date.between(start_date, end_date)
                )
            ).all()
        else:
            psa = PSA.query.filter(
                and_(
                    PSA.patient_id == user_id,
                    PSA.date.between(start_date, end_date)
                )
            ).all()

        if not psa:
            return jsonify({"message": "PSA data not found"}), 404
        
        return jsonify({
            "message": "",
            "psa": [p.to_dict() for p in psa]
        }), 200
    
    return method()

# 病患更新/新增 PSA 資料
@patient_bp.route('/api/patient/psa', methods=['PATCH', 'OPTIONS'])
@cross_origin()
def update_psa_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    @jwt_required()
    def method():
        try:
            patient_id = get_jwt_identity()
            if not patient_id:
                return jsonify({"message": "Missing patient_id"}), 400
            data = request.get_json()
            date = data.get('date')
            psa = data.get('psa')
            if not date or not psa:
                return jsonify({"message": "Missing required fields"}), 400
            
            row = PSA.query.filter_by(patient_id=patient_id, date=date).first()
            if row:
                row.psa = psa
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return jsonify({"message": "Create Patient Error"}), 400
            else:
                new_psa = PSA(patient_id=patient_id, date=date, psa=psa)
                try:
                    db.session.add(new_psa)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return jsonify({"message": "Create Patient Error"}), 400
        except Exception as e:
            return jsonify({"message": "Patient Error: " + str(e)}), 500
                
        return jsonify({
            "message": "PSA data updated successfully",
            "psa": {
                "date": date,
                "psa": psa
            }
        }), 200
    
    return method()

# 病患更新資料
@patient_bp.route('/api/patient/update_data', methods=['PATCH', 'OPTIONS'])
@cross_origin()
def update_patient_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    @jwt_required()
    def method():
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
    return method()