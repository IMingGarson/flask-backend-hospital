from flask import Blueprint, request, jsonify, url_for, current_app, render_template
from app.models import db, User
from app.utils import validate, hash_password, check_password, generate_confirmation_token, confirm_token, validate_email
from flask_mail import Message, Mail
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from datetime import timedelta

mail = Mail()
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

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