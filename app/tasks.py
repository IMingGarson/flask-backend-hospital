import time
from app.celery_app import celery
from app.models import Patient
from flask import current_app
import requests
import json

@celery.task
def send_periodical_push_notification():
    patients = Patient.query.all()
    url = "https://app.nativenotify.com/api/indie/notification"
    for patient in patients:
        payload = {
            'subID': 'PUSH_ID_' + str(patient.id),
            'appId': current_app.config['NATIVE_NOTIFY_APP_ID'],
            'appToken': current_app.config['NATIVE_NOTIFY_APP_TOKEN'],
            'title': '你好',
            'message': '新的開始，祝您有個愉快的一週！'
        }
        requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        time.sleep(0.5)