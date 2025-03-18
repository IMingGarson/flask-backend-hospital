from flask import current_app
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from email_validator import validate_email, EmailNotValidError
import bcrypt
from exponent_server_sdk import (
    PushClient,
    PushMessage,
)

def send_push_notification(push_token, title, body):
    client = PushClient()
    response = client.publish(PushMessage(to=push_token, title=title, body=body, sound="default", channel_id="default"))
    response.validate_response()
    return 200, {"status": "ok"}

    # message = {
    #     "to": push_token,
    #     "sound": "default",
    #     "title": title,
    #     "body": body,
    # }
    # response = requests.post(
    #     "https://exp.host/--/api/v2/push/send",
    #     headers={
    #         "Accept": "application/json",
    #         "Accept-Encoding": "gzip, deflate",
    #         "Content-Type": "application/json",
    #     },
    #     json=message,
    # )
    # return response.status_code, response.json()

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate(email):
    try:
        v = validate_email(email)
        return v['email']
    except EmailNotValidError as e:
        print(str(e))
        return None

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration
        )
    except:
        return False
    return email
